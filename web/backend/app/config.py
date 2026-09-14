"""Runtime configuration for the backend."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache
def settings() -> "Settings":
    return Settings()


class Settings:
    # Comma-separated list of origins allowed to call the API (the dev frontend).
    cors_origins: list[str]
    # Minutes a logged-in TJU session is kept server-side before eviction.
    session_ttl_minutes: int

    def __init__(self) -> None:
        raw_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
        self.session_ttl_minutes = int(os.getenv("SESSION_TTL_MINUTES", "60"))
