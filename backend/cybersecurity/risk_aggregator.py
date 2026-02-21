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
    check_unlisted_company,
    get_root_domain,
)
from .email_analyzer import analyze_emails
from .url_extractor import extract_urls
from .whois_checker import analyze_domain_age


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
    email_warnings: list[str], domain_warnings: list[str], whois_warnings: list[str]
) -> int:
    """
    Build a simple integer risk score (0-100) from warning categories.
    """
    score = 0
    score += len(email_warnings) * 20
    score += len(domain_warnings) * 20

    for warning in whois_warnings:
        if warning.startswith("High risk"):
            score += 30
        elif warning.startswith("Suspicious"):
            score += 20
        elif warning.startswith("WHOIS lookup failed"):
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
    email_warnings = analyze_emails(text)
    domain_warnings: list[str] = []
    whois_warnings: list[str] = []

    inferred_company = company.strip().lower() if company else _infer_company_from_text(text)
    domain_warnings.extend(check_unlisted_company(inferred_company))

    for url in urls_found:
        root_domain = get_root_domain(url)
        if not root_domain:
            continue

        if check_free_hosting(root_domain):
            domain_warnings.append("Website hosted on free hosting platform")

        domain_warnings.extend(check_company_domain(inferred_company, url))
        domain_warnings.extend(check_company_keyword_mismatch(inferred_company, url))

        age_message = analyze_domain_age(root_domain)
        if age_message != "Safe: domain age appears legitimate":
            whois_warnings.append(f"{root_domain}: {age_message}")

    # Keep warnings stable and readable without duplicates.
    domain_warnings = list(dict.fromkeys(domain_warnings))
    whois_warnings = list(dict.fromkeys(whois_warnings))

    risk_score = _score_from_warnings(email_warnings, domain_warnings, whois_warnings)

    return {
        "urls_found": urls_found,
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
