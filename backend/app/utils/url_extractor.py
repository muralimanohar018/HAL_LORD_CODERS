"""URL extractor utilities.

Responsibility:
- Utility helpers for URL extraction only.
"""

import re


_URL_PATTERN = re.compile(r"https?://[^\s]+")


def extract_urls(text: str) -> list[str]:
    """Extract URLs from plain text."""
    return _URL_PATTERN.findall(text)
