from __future__ import annotations

from functools import lru_cache
from pydantic import BaseSettings, HttpUrl, validator
from typing import List

class Settings(BaseSettings):
    nitter_base_urls: List[HttpUrl] = []  # e.g. ["https://nitter.net"] allow multiple mirrors
    default_feeds: List[str] = []  # list of RSS feed URLs to aggregate initially
    fetch_concurrency: int = 5
    fetch_timeout_seconds: int = 15
    cache_ttl_seconds: int = 120
    user_agent: str = "nitter-timeline/0.1 (+https://github.com/yourname/nitter-timeline)"

    class Config:
        env_file = ".env"
        env_prefix = "NT_"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
