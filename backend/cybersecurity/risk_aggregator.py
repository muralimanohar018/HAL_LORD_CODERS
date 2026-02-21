"""
Rule-based cybersecurity risk aggregation for CampusShield.
"""

from __future__ import annotations

import re

from .domain_checker import (
    COMPANY_WHITELIST,
    check_company_domain,
    check_company_keyword_mismatch,
    check_free_hosting,
    get_company_verification_status,
    get_root_domain,
)
from .email_analyzer import analyze_emails
from .url_extractor import extract_urls
from .whois_checker import analyze_domain_age


BEHAVIOR_RULES: list[tuple[re.Pattern[str], str, int]] = [
    (
        re.compile(r"\b(pay|payment|deposit|fee)\b", re.IGNORECASE),
        "Payment request detected in recruitment message",
        20,
    ),
    (
        re.compile(r"\b(training\s*fee|registration\s*fee|security\s*deposit)\b", re.IGNORECASE),
        "Recruitment fee/deposit request detected",
        25,
    ),
    (
        re.compile(r"\b(immediate\s+joining|quick\s+offer|offer\s+letter)\b", re.IGNORECASE),
        "Urgent or shortcut hiring language detected",
        15,
    ),
    (
        re.compile(
            r"\b(pan|aadhaar|aadhar|bank\s+account|otp|cvv)\b.{0,40}\b(copy|scan|details?|number|upload|share)\b",
            re.IGNORECASE,
        ),
        "Sensitive personal/financial document request detected",
        30,
    ),
    (
        re.compile(
            r"\b(copy|scan|details?|number|upload|share)\b.{0,40}\b(pan|aadhaar|aadhar|bank\s+account|otp|cvv)\b",
            re.IGNORECASE,
        ),
        "Sensitive personal/financial document request detected",
        30,
    ),
]


def _detect_behavioral_warnings(text: str) -> list[str]:
    """
    Detect non-ML recruitment fraud behaviors directly from message text.
    """
    warnings: list[str] = []
    for pattern, warning, _ in BEHAVIOR_RULES:
        if pattern.search(text):
            warnings.append(warning)
    return list(dict.fromkeys(warnings))


def _behavior_score(behavior_warnings: list[str]) -> int:
    """
    Convert behavioral warnings to score using rule severities.
    """
    score = 0
    for warning in behavior_warnings:
        for _, rule_warning, rule_score in BEHAVIOR_RULES:
            if warning == rule_warning:
                score += rule_score
                break
    return min(score, 100)


def _infer_company_from_text(text: str) -> str:
    """
    Infer target company name by matching known company keys in text.
    """
    lowered = text.lower()
    for company in COMPANY_WHITELIST:
        if re.search(rf"\b{re.escape(company)}\b", lowered):
            return company
    return ""


def _score_from_warnings(
    behavior_warnings: list[str],
    email_warnings: list[str],
    domain_warnings: list[str],
    whois_warnings: list[str],
) -> int:
    """
    Build a simple integer risk score (0-100) from warning categories.
    """
    score = 0
    score += _behavior_score(behavior_warnings)
    score += len(email_warnings) * 20
    score += len(domain_warnings) * 20

    for warning in whois_warnings:
        if "High risk" in warning:
            score += 30
        elif "Suspicious" in warning:
            score += 20
        elif "WHOIS lookup failed" in warning:
            score += 10

    return min(score, 100)


def analyze_security(text: str, company: str | None = None) -> dict:
    """
    Run non-ML security checks and return structured risk findings.
    """
    if text is None:
        text = ""
    elif not isinstance(text, str):
        text = str(text)

    urls_found = extract_urls(text)
    behavior_warnings = _detect_behavioral_warnings(text)
    email_warnings = analyze_emails(text)
    domain_warnings: list[str] = []
    whois_warnings: list[str] = []

    inferred_company = company.strip().lower() if company else _infer_company_from_text(text)
    company_verification_status = get_company_verification_status(inferred_company or None)

    for url in urls_found:
        root_domain = get_root_domain(url)
        if not root_domain:
            continue

        if check_free_hosting(root_domain):
            domain_warnings.append("Website hosted on free hosting platform")

        # Strict official-domain checks apply only for known, whitelisted companies.
        domain_warnings.extend(check_company_domain(inferred_company, url))
        # For unknown/startup companies, use weaker lexical mismatch heuristic.
        if company_verification_status == "unverified":
            domain_warnings.extend(check_company_keyword_mismatch(inferred_company, url))

        age_message = analyze_domain_age(root_domain)
        if age_message != "Safe: domain age appears legitimate":
            # Network-related WHOIS failures should not penalize known official domains.
            if (
                "WHOIS lookup failed" in age_message
                and company_verification_status == "verified"
                and root_domain in COMPANY_WHITELIST.get(inferred_company, [])
            ):
                continue
            whois_warnings.append(f"{root_domain}: {age_message}")

    # Keep warnings stable and readable without duplicates.
    domain_warnings = list(dict.fromkeys(domain_warnings))
    whois_warnings = list(dict.fromkeys(whois_warnings))

    risk_score = _score_from_warnings(
        behavior_warnings,
        email_warnings,
        domain_warnings,
        whois_warnings,
    )

    return {
        "urls_found": urls_found,
        "company_inferred": inferred_company or "",
        "company_verification_status": company_verification_status,
        "behavior_warnings": behavior_warnings,
        "email_warnings": email_warnings,
        "domain_warnings": domain_warnings,
        "whois_warnings": whois_warnings,
        "security_risk_score": risk_score,
    }


if __name__ == "__main__":
    example = (
        "Apply at https://tcs-career-portal.netlify.app "
        "contact tcs.hr.jobs@gmail.com"
    )
    print(analyze_security(example, company="tcs"))
