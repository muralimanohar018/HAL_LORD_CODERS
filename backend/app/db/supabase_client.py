"""Supabase client module.

Responsibility:
- Initialize Supabase client from environment configuration.
- No business logic.
"""

from datetime import datetime, timezone
from typing import Any

from ..core.logging import get_logger
from ..core.config import get_settings

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover
    Client = Any  # type: ignore[assignment]
    create_client = None


logger = get_logger(__name__)


class SupabaseInsertError(Exception):
    """Raised when writing scan results to Supabase fails."""


def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    settings = get_settings()
    if create_client is None:
        raise SupabaseInsertError("Supabase dependency is not installed.")
    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseInsertError("Supabase credentials are not configured.")
    return create_client(settings.supabase_url, settings.supabase_key)


def save_scan_result(input_text: str, ml_response: dict[str, Any], risk_score: float) -> None:
    """Persist a scan result in Supabase."""
    settings = get_settings()
    client = get_supabase_client()
    payload = {
        "input_text": input_text,
        "ml_response": ml_response,
        "risk_score": risk_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        client.table(settings.supabase_results_table).insert(payload).execute()
    except Exception as exc:
        logger.error("Failed to insert scan result into Supabase.")
        raise SupabaseInsertError("Could not save scan result.") from exc
