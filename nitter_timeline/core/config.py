from __future__ import annotations

from functools import lru_cache

from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Runtime configuration loaded from environment variables.

    Prefix: ``NT_`` (e.g. ``NT_CACHE_TTL_SECONDS``). Values may be supplied
    via process environment or a local ``.env`` file for development.

    Attributes:
        nitter_base_urls: Preferred Nitter mirror base URLs (failover list).
        default_feeds: Initial feed URLs aggregated when none are provided
            in a request.
        fetch_concurrency: Max concurrent network fetches (future use).
        fetch_timeout_seconds: Per-request timeout.
        cache_ttl_seconds: In-memory feed cache lifetime.
        user_agent: Custom UA for polite identification.
    """

    # e.g. ["https://nitter.net"] allow multiple mirrors
    nitter_base_urls: list[HttpUrl] = []
    # list of RSS feed URLs to aggregate initially
    default_feeds: list[str] = []
    fetch_concurrency: int = 5
    fetch_timeout_seconds: int = 15
    cache_ttl_seconds: int = 120
    user_agent: str = (
        "nitter-timeline/0.1 (+https://github.com/yourname/nitter-timeline)"
    )

    class Config:  # pylint: disable=too-few-public-methods
        env_file = ".env"
        env_prefix = "NT_"
        case_sensitive = False

    
@lru_cache
def get_settings() -> Settings:
    """Return cached singleton settings instance.

    Returns:
        Settings: Parsed settings object (cached; environment read once).
    """
    return Settings()


settings = get_settings()
