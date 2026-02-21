"""
CampusShield dataset builder:
1) Collect publicly available scam-related recruitment text from Reddit
   (Pushshift-compatible comments + submissions + Reddit public search fallback)
2) Clean and label scam text as label=1
3) Generate safe synthetic recruitment messages as label=0
4) Save scam-only and final shuffled datasets

Ethics:
- Uses only public data endpoints
- Does not scrape private chats or private platforms
- Intended for academic research
"""

from __future__ import annotations

import argparse
import random
import re
import time
from typing import Any

import pandas as pd
import requests


COMMENT_API_ENDPOINTS = [
    "https://api.pushshift.io/reddit/search/comment/",
    "https://api.pullpush.io/reddit/search/comment/",
]

SUBMISSION_API_ENDPOINTS = [
    "https://api.pushshift.io/reddit/search/submission/",
    "https://api.pullpush.io/reddit/search/submission/",
]

REDDIT_SEARCH_URL = "https://www.reddit.com/r/{subreddit}/search.json"

# Base + extra public communities where scam/job-warning discussions are common.
SUBREDDITS = [
    "scams",
    "india",
    "developersIndia",
    "IndianAcademia",
    "jobs",
    "careerguidance",
    "cscareerquestions",
    "csMajors",
]

KEYWORDS = [
    "internship scam",
    "job scam",
    "fake internship",
    "registration fee job",
    "training fee internship",
    "job offer scam",
    "fake recruiter",
    "placement scam",
    "employment fraud",
    "work from home scam",
    "offer letter scam",
    "hr asking money",
    "document verification fee",
    "onboarding fee",
    "security deposit job",
]

DEFAULT_TARGET_SCAM_MESSAGES = 5000
DEFAULT_SAFE_MESSAGE_COUNT = 20000

REQUEST_PAGE_SIZE = 100
MAX_COMMENT_PAGES_PER_QUERY = 60
MAX_SUBMISSION_PAGES_PER_QUERY = 60
MAX_REDDIT_POST_PAGES_PER_QUERY = 20
REQUEST_TIMEOUT = 30

MIN_RAW_TEXT_LEN = 80
MIN_CLEAN_TEXT_LEN = 40

REQUEST_HEADERS = {
    "User-Agent": "CampusShieldDatasetBuilder/1.1 (AcademicResearch; public-data-only)",
}

DEFAULT_SCAM_OUTPUT_PATH = "reddit_recruitment_scam_dataset.csv"
DEFAULT_FINAL_OUTPUT_PATH = "final_training_dataset.csv"


def clean_text(text: str) -> str:
    """
    Clean text:
    - lowercase
    - remove URLs
    - remove usernames
    - remove emojis/non-ascii symbols
    - remove extra whitespace
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"(?:(?:/)?u/[a-zA-Z0-9_-]+|@[a-zA-Z0-9_]+)", " ", text)
    text = re.sub(r"[\U00010000-\U0010ffff]", " ", text)
    text = re.sub(r"[^\w\s.,!?'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _request_endpoint(url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    if response.status_code in {401, 403, 429}:
        raise requests.HTTPError(f"HTTP {response.status_code} from {url}")
    response.raise_for_status()
    return response.json()


def _fetch_from_endpoints(endpoints: list[str], params: dict[str, Any]) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for endpoint in endpoints:
        try:
            payload = _request_endpoint(endpoint, params=params)
            return payload.get("data", [])
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise requests.RequestException(str(last_error))
    return []


def fetch_comments(
    subreddit: str, keyword: str, before: int | None = None, size: int = REQUEST_PAGE_SIZE
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "subreddit": subreddit,
        "q": keyword,
        "size": size,
        "sort": "desc",
        "sort_type": "created_utc",
        "filter": "body,created_utc",
    }
    if before is not None:
        params["before"] = before
    return _fetch_from_endpoints(COMMENT_API_ENDPOINTS, params)


def fetch_submissions(
    subreddit: str, keyword: str, before: int | None = None, size: int = REQUEST_PAGE_SIZE
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "subreddit": subreddit,
        "q": keyword,
        "size": size,
        "sort": "desc",
        "sort_type": "created_utc",
        "filter": "title,selftext,created_utc",
    }
    if before is not None:
        params["before"] = before
    return _fetch_from_endpoints(SUBMISSION_API_ENDPOINTS, params)


def fetch_reddit_posts(
    subreddit: str, keyword: str, after: str | None = None, size: int = REQUEST_PAGE_SIZE
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Public Reddit JSON fallback (submission text from title + selftext).
    """
    params: dict[str, Any] = {
        "q": keyword,
        "restrict_sr": "on",
        "sort": "new",
        "t": "all",
        "limit": size,
    }
    if after:
        params["after"] = after

    payload = _request_endpoint(REDDIT_SEARCH_URL.format(subreddit=subreddit), params=params)
    data = payload.get("data", {})
    children = data.get("children", [])

    rows: list[dict[str, Any]] = []
    for child in children:
        post = child.get("data", {})
        rows.append(
            {
                "body": f"{post.get('title', '')} {post.get('selftext', '')}".strip(),
                "created_utc": post.get("created_utc"),
            }
        )

    return rows, data.get("after")


def _try_add_message(raw_text: str, collected: list[str], seen: set[str]) -> bool:
    if not isinstance(raw_text, str):
        return False

    raw_text = raw_text.strip()
    if len(raw_text) < MIN_RAW_TEXT_LEN:
        return False
    if raw_text.lower() in {"[removed]", "[deleted]", "[removed by reddit]"}:
        return False

    cleaned = clean_text(raw_text)
    if len(cleaned) < MIN_CLEAN_TEXT_LEN:
        return False
    if cleaned in seen:
        return False

    seen.add(cleaned)
    collected.append(cleaned)
    return True


def _load_existing_scam_messages(path: str) -> list[str]:
    """
    Enables incremental scraping across multiple runs.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        return []
    except Exception:
        return []

    if "text" not in df.columns:
        return []

    if "label" in df.columns:
        df = df[df["label"] == 1]

    messages: list[str] = []
    for value in df["text"].dropna().astype(str).tolist():
        cleaned = clean_text(value)
        if len(cleaned) >= MIN_CLEAN_TEXT_LEN:
            messages.append(cleaned)
    return list(dict.fromkeys(messages))


def collect_scam_messages(
    target_count: int = DEFAULT_TARGET_SCAM_MESSAGES,
    scam_output_path: str = DEFAULT_SCAM_OUTPUT_PATH,
) -> list[str]:
    """
    Collect scam-related text from comments, submissions, and fallback post search.
    """
    collected = _load_existing_scam_messages(scam_output_path)
    seen = set(collected)

    if collected:
        print(f"[INFO] Loaded {len(collected)} existing scam samples from {scam_output_path}")

    for subreddit in SUBREDDITS:
        for keyword in KEYWORDS:
            query_start_count = len(collected)

            # 1) Collect comments
            before: int | None = None
            for _ in range(MAX_COMMENT_PAGES_PER_QUERY):
                if len(collected) >= target_count:
                    break
                try:
                    rows = fetch_comments(subreddit=subreddit, keyword=keyword, before=before)
                except requests.RequestException as exc:
                    print(f"[WARN] Comment fetch failed for r/{subreddit} '{keyword}': {exc}")
                    break
                if not rows:
                    break

                oldest_timestamp: int | None = None
                page_added = 0
                for row in rows:
                    if _try_add_message(row.get("body", ""), collected, seen):
                        page_added += 1
                    created_utc = row.get("created_utc")
                    if isinstance(created_utc, int):
                        oldest_timestamp = (
                            created_utc
                            if oldest_timestamp is None
                            else min(oldest_timestamp, created_utc)
                        )
                    if len(collected) >= target_count:
                        break

                if oldest_timestamp is None:
                    break
                before = oldest_timestamp - 1
                if page_added == 0:
                    break
                time.sleep(0.35)

            # 2) Collect submissions
            before = None
            for _ in range(MAX_SUBMISSION_PAGES_PER_QUERY):
                if len(collected) >= target_count:
                    break
                try:
                    rows = fetch_submissions(subreddit=subreddit, keyword=keyword, before=before)
                except requests.RequestException as exc:
                    print(f"[WARN] Submission fetch failed for r/{subreddit} '{keyword}': {exc}")
                    break
                if not rows:
                    break

                oldest_timestamp = None
                page_added = 0
                for row in rows:
                    body = f"{row.get('title', '')} {row.get('selftext', '')}".strip()
                    if _try_add_message(body, collected, seen):
                        page_added += 1
                    created_utc = row.get("created_utc")
                    if isinstance(created_utc, int):
                        oldest_timestamp = (
                            created_utc
                            if oldest_timestamp is None
                            else min(oldest_timestamp, created_utc)
                        )
                    if len(collected) >= target_count:
                        break

                if oldest_timestamp is None:
                    break
                before = oldest_timestamp - 1
                if page_added == 0:
                    break
                time.sleep(0.35)

            # 3) Fallback: public Reddit search (posts)
            if len(collected) < target_count:
                after: str | None = None
                for _ in range(MAX_REDDIT_POST_PAGES_PER_QUERY):
                    try:
                        post_rows, after = fetch_reddit_posts(
                            subreddit=subreddit,
                            keyword=keyword,
                            after=after,
                        )
                    except requests.RequestException:
                        break
                    if not post_rows:
                        break

                    added_from_posts = 0
                    for row in post_rows:
                        if _try_add_message(row.get("body", ""), collected, seen):
                            added_from_posts += 1
                        if len(collected) >= target_count:
                            break

                    if len(collected) >= target_count:
                        break
                    if added_from_posts == 0 and not after:
                        break
                    time.sleep(0.35)

            added_this_query = len(collected) - query_start_count
            print(
                f"[INFO] r/{subreddit} | '{keyword}' -> +{added_this_query} "
                f"(total {len(collected)})"
            )

            if len(collected) >= target_count:
                return collected

    return collected


def generate_safe_messages(count: int = DEFAULT_SAFE_MESSAGE_COUNT) -> list[str]:
    """
    Generate safe recruitment messages (label=0).
    """
    companies = [
        "TCS",
        "Infosys",
        "Wipro",
        "Accenture",
        "Capgemini",
        "IBM",
        "Zoho",
        "HCL",
        "Tech Mahindra",
        "Cognizant",
    ]
    roles = [
        "software intern",
        "data analyst intern",
        "graduate engineer trainee",
        "python developer intern",
        "qa intern",
        "backend developer intern",
    ]
    locations = ["Bengaluru", "Hyderabad", "Chennai", "Pune", "Noida", "Remote"]
    portals = ["official careers portal", "company jobs page", "campus placement portal"]
    interview_slots = [
        "tomorrow at 10 AM",
        "next Monday at 11 AM",
        "Friday at 2 PM",
        "this week as per availability",
    ]

    templates = [
        "Your interview for {role} at {company} is scheduled {slot}.",
        "{company} hiring team has shortlisted your profile for {role} in {location}.",
        "Please submit your resume through the {portal} for {company}.",
        "{company} will conduct a technical interview round for the {role} position.",
        "Thank you for applying to {company}. HR will share next steps by official email.",
        "The recruitment process at {company} has aptitude and technical interview stages.",
        "Candidates are advised to apply only through {company} {portal}.",
        "Your application for {role} has been received successfully by {company}.",
        "Interview details for {company} will be sent through the college placement office.",
        "{company} recruitment notice: no payment is required at any stage of hiring.",
    ]

    safe_messages: list[str] = []
    for _ in range(count):
        template = random.choice(templates)
        msg = template.format(
            role=random.choice(roles),
            company=random.choice(companies),
            location=random.choice(locations),
            portal=random.choice(portals),
            slot=random.choice(interview_slots),
        )
        safe_messages.append(clean_text(msg))
    return safe_messages


def parse_args() -> argparse.Namespace:
    """
    Command-line options for large-scale or incremental collection runs.
    """
    parser = argparse.ArgumentParser(description="Build CampusShield scam dataset from public Reddit data.")
    parser.add_argument(
        "--target-scam",
        type=int,
        default=DEFAULT_TARGET_SCAM_MESSAGES,
        help="Target number of scam samples (label=1) to collect.",
    )
    parser.add_argument(
        "--safe-count",
        type=int,
        default=DEFAULT_SAFE_MESSAGE_COUNT,
        help="Number of synthetic safe samples (label=0) to generate.",
    )
    parser.add_argument(
        "--scam-output",
        type=str,
        default=DEFAULT_SCAM_OUTPUT_PATH,
        help="Path for scam-only output CSV.",
    )
    parser.add_argument(
        "--final-output",
        type=str,
        default=DEFAULT_FINAL_OUTPUT_PATH,
        help="Path for final mixed output CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("[INFO] Collecting scam recruitment messages from public Reddit data...")
    scam_texts = collect_scam_messages(
        target_count=max(0, args.target_scam),
        scam_output_path=args.scam_output,
    )
    print(f"[INFO] Scam messages collected: {len(scam_texts)}")

    scam_df = pd.DataFrame({"text": scam_texts, "label": 1})
    scam_df = scam_df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    scam_df.to_csv(args.scam_output, index=False)
    print(f"[INFO] Saved scam-only dataset -> {args.scam_output}")

    safe_count = max(0, args.safe_count)
    print(f"[INFO] Generating {safe_count} safe template messages...")
    safe_df = pd.DataFrame({"text": [], "label": []})
    if safe_count > 0:
        safe_texts = generate_safe_messages(count=safe_count)
        safe_df = pd.DataFrame({"text": safe_texts, "label": 0})

    final_df = pd.concat([scam_df, safe_df], ignore_index=True)
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    final_df.to_csv(args.final_output, index=False)

    print(f"[INFO] Saved final mixed dataset -> {args.final_output}")
    print("[INFO] Final label distribution:")
    print(final_df["label"].value_counts().to_dict())

    if len(scam_df) < args.target_scam:
        print(
            f"[NOTE] Collected {len(scam_df)} scam messages (< {args.target_scam}). "
            "Run this script again later to accumulate more unique samples."
        )


if __name__ == "__main__":
    main()
