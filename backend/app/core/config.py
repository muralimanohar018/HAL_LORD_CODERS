"""Application configuration.

Responsibility:
- Load environment variables and expose config values.
"""

import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> None:
        """Fallback when python-dotenv is unavailable."""
        return None


class Settings:
    """Configuration container backed by environment variables."""

    def __init__(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        self.supabase_results_table = os.getenv("SUPABASE_RESULTS_TABLE", "scan_results")
        self.ml_endpoint = os.getenv("ML_ENDPOINT", "")


def load_environment() -> None:
    """Load environment variables from .env if available."""
    load_dotenv()


def get_settings() -> Settings:
    """Return current application settings."""
    return Settings()
