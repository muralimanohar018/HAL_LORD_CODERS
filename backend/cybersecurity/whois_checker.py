"""
WHOIS-based domain age checks for CampusShield.
"""

from __future__ import annotations

import contextlib
import io
import warnings
from datetime import datetime, timezone

try:
    import whois
except ImportError:  # pragma: no cover - depends on local environment
    whois = None


def _normalize_datetime(value: object) -> datetime | None:
    """
    Normalize WHOIS creation_date to a timezone-aware datetime.
    """
    if value is None:
        return None

    # python-whois may return a list of dates for some TLDs.
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    return None


def get_domain_age(domain: str) -> int:
    """
    Return domain age in days. Returns -1 when WHOIS data is unavailable.
    """
    if not domain:
        return -1
    if whois is None:
        return -1

    try:
        # Suppress noisy stdout/stderr from whois/socket internals.
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            warnings.catch_warnings(),
        ):
            warnings.simplefilter("ignore", ResourceWarning)
            result = whois.whois(domain)
        creation_date = _normalize_datetime(getattr(result, "creation_date", None))
        if creation_date is None:
            return -1

        now = datetime.now(timezone.utc)
        delta = now - creation_date
        return max(0, delta.days)
    except Exception:
        return -1


def analyze_domain_age(domain: str) -> str:
    """
    Return risk classification based on domain age.
    """
    age_days = get_domain_age(domain)
    if age_days < 0:
        return "WHOIS lookup failed or creation date unavailable"
    if age_days < 90:
        return "High risk: newly created website"
    if age_days < 365:
        return "Suspicious: recently created website"
    return "Safe: domain age appears legitimate"
