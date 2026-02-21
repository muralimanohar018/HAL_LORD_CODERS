"""
URL extraction utilities for CampusShield.
"""

from __future__ import annotations

import re

# Matches http/https URLs until whitespace or common closing punctuation.
URL_PATTERN = re.compile(r"(https?://[^\s<>\")\]]+)", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    """
    Extract all http/https URLs from text.
    """
    if not text:
        return []

    if not isinstance(text, str):
        text = str(text)

    urls = URL_PATTERN.findall(text)

    # Remove common trailing punctuation that may be attached in plain text.
    cleaned_urls = [url.rstrip(".,;:!?") for url in urls]
    return cleaned_urls

