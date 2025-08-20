from __future__ import annotations
import asyncio
import logging
from typing import Iterable
import httpx
import feedparser
from cachetools import TTLCache
from . import aggregator  # noqa: F401 (planned usage)
from ..core.config import settings

logger = logging.getLogger(__name__)

_cache = TTLCache(maxsize=512, ttl=settings.cache_ttl_seconds)
_client: httpx.AsyncClient | None = None

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, headers={"User-Agent": settings.user_agent})
    return _client

async def fetch_feed(url: str) -> dict | None:
    if url in _cache:
        return _cache[url]
    client = await get_client()
    try:
        resp = await client.get(url)
        resp.raise_for_status()
    except Exception as exc:  # broad catch for logging
        logger.warning("fetch failed %s: %s", url, exc)
        return None
    parsed = feedparser.parse(resp.content)
    _cache[url] = parsed
    return parsed

async def fetch_many(urls: Iterable[str]) -> list[tuple[str, dict]]:
    results: list[tuple[str, dict]] = []

    async def one(u: str):
        parsed = await fetch_feed(u)
        if parsed:
            results.append((u, parsed))

    await asyncio.gather(*(one(u) for u in urls))
    return results
