"""
Domain verification utilities for CampusShield.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import tldextract

FREE_HOSTING_DOMAINS = {
    "netlify.app",
    "github.io",
    "wixsite.com",
    "blogspot.com",
    "weebly.com",
}

# Use offline PSL snapshot to avoid network/cache warnings in locked environments.
EXTRACTOR = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)


def _load_company_whitelist() -> dict[str, list[str]]:
    """
    Load known official company domains from local JSON.
    """
    config_path = Path(__file__).with_name("company_domains.json")
    try:
        with config_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    # Normalize all keys/values for reliable comparisons.
    normalized: dict[str, list[str]] = {}
    for company, domains in raw.items():
        normalized[str(company).strip().lower()] = [str(d).strip().lower() for d in domains]
    return normalized


COMPANY_WHITELIST = _load_company_whitelist()


def _normalize_company_token(company: str) -> str:
    """
    Normalize company name for lexical comparisons.
    """
    return re.sub(r"[^a-z0-9]", "", company.lower())


def get_root_domain(url: str) -> str:
    """
    Return root domain (e.g., 'example.com') from URL.
    """
    if not url:
        return ""

    extracted = EXTRACTOR(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}".lower()
    return ""


def check_company_domain(company: str, url: str) -> list[str]:
    """
    Validate URL domain against known official domains for the given company.
    """
    warnings: list[str] = []
    if not company or not url:
        return warnings

    company_key = company.strip().lower()
    allowed_domains = COMPANY_WHITELIST.get(company_key, [])
    if not allowed_domains:
        return warnings

    root_domain = get_root_domain(url)
    if root_domain and root_domain not in allowed_domains:
        warnings.append("Website domain does not match official company domain")

    return warnings


def check_unlisted_company(company: str) -> list[str]:
    """
    Warn when the company is not in the verified domain whitelist.
    """
    # Kept for backward compatibility, but unknown companies are now treated as
    # "unverified" and should not be marked fake by default.
    return []


def get_company_verification_status(company: str | None) -> str:
    """
    Return company verification status used by risk aggregation logic.
    """
    if not company:
        return "not_provided"
    if company.strip().lower() in COMPANY_WHITELIST:
        return "verified"
    return "unverified"


def check_company_keyword_mismatch(company: str, url: str) -> list[str]:
    """
    Heuristic for startup/unlisted companies:
    domain label should roughly contain the company token.
    """
    if not company or not url:
        return []

    root_domain = get_root_domain(url)
    if not root_domain:
        return []

    company_token = _normalize_company_token(company)
    if len(company_token) < 3:
        return []

    domain_label = root_domain.split(".")[0]
    if company_token not in domain_label:
        return ["Domain does not appear to represent the claimed company name"]

    return []


def check_free_hosting(domain: str) -> bool:
    """
    Detect domains hosted on commonly abused free hosting platforms.
    """
    if not domain:
        return False
    return domain.lower() in FREE_HOSTING_DOMAINS
