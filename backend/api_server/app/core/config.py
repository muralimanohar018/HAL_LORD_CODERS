import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    supabase_url: str
    supabase_service_key: str
    database_url: str

    @property
    def supabase_user_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1/user"


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
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
