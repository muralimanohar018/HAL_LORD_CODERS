"""Text cleaner module.

Responsibility:
- Text sanitization and normalization only.
- No model calls, HTTP, or database logic.
"""

import re


_NON_READABLE_PATTERN = re.compile(r"[^\x09\x0A\x0D\x20-\x7E]")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_text(raw_text: str) -> str:
    """Sanitize and normalize input text."""
    normalized = _NON_READABLE_PATTERN.sub(" ", raw_text)
    normalized = _WHITESPACE_PATTERN.sub(" ", normalized)
    return normalized.strip()
