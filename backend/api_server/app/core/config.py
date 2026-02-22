import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    supabase_url: str
    supabase_service_key: str
    database_url: str
    ml_api_url: str = "http://127.0.0.1:8001/predict"
    ml_timeout_seconds: float = 15.0
    dev_bypass_auth: bool = False
    dev_user_id: str = "00000000-0000-0000-0000-000000000001"

    @property
    def supabase_user_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1/user"


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
        ml_api_url=os.getenv("ML_API_URL", "http://127.0.0.1:8001/predict"),
        ml_timeout_seconds=float(os.getenv("ML_TIMEOUT_SECONDS", "15")),
        dev_bypass_auth=os.getenv("DEV_BYPASS_AUTH", "false").strip().lower() in {"1", "true", "yes", "on"},
        dev_user_id=os.getenv("DEV_USER_ID", "00000000-0000-0000-0000-000000000001").strip(),
    )

    missing = []
    if not settings.supabase_url:
        missing.append("SUPABASE_URL")
    if not settings.supabase_service_key:
        missing.append("SUPABASE_SERVICE_KEY")
    if not settings.database_url:
        missing.append("DATABASE_URL")

    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return settings
