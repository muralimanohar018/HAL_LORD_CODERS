"""
Email analysis utilities for CampusShield.
"""

from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b")
PERSONAL_PROVIDERS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}


def analyze_emails(text: str) -> list[str]:
    """
    Extract emails and report warnings for personal email domains.
    """
    if not text:
        return []

    if not isinstance(text, str):
        text = str(text)

    warnings: list[str] = []
    found_domains = EMAIL_PATTERN.findall(text)

    for domain in found_domains:
        if domain.lower() in PERSONAL_PROVIDERS:
            warnings.append("Recruiter is using a personal email domain")
            break

    return warnings

