"""Async feed fetching utilities.

Responsible for retrieving individual or multiple RSS feeds concurrently
with a small in-memory TTL cache to reduce network load.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

import feedparser
import httpx
from cachetools import TTLCache

# Local imports
from nitter_timeline.core.config import settings

logger = logging.getLogger(__name__)

_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.cache_ttl_seconds)
_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """Return a shared `httpx.AsyncClient` instance.

    Creates the client lazily on first call and reuses it afterwards to
    take advantage of connection pooling (keep-alive) and reduce TLS
    handshakes.

    Returns:
        httpx.AsyncClient: The shared asynchronous HTTP client.
    """
    global _client  # pylint: disable=global-statement
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=settings.fetch_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
        )
    return _client
 
async def fetch_feed(url: str) -> dict | None:
    """Fetch and parse a single RSS/Atom feed.

    The raw response body is parsed with *feedparser* and cached in an
    in-memory TTL cache keyed by URL.

    Args:
        url: Absolute feed URL (expected to be a Nitter RSS endpoint).

    Returns:
        dict | None: Parsed feed structure, or ``None`` on network / parse
        error (the error is logged, not raised).
    """
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
    """Fetch multiple feeds concurrently.

    Args:
        urls: Iterable of absolute feed URLs.

    Returns:
        list[tuple[str, dict]]: List of ``(url, parsed_feed)`` tuples for
        successfully retrieved feeds (failed ones are silently skipped
        after logging).

    Notes:
        * Uses ``asyncio.gather`` without ``return_exceptions``; failures
          inside individual fetches are already handled in ``fetch_feed``.
        * Output order corresponds to completion order, not input order.
    """
    results: list[tuple[str, dict]] = []

    async def one(feed_url: str) -> None:
        parsed = await fetch_feed(feed_url)
        if parsed:
            results.append((feed_url, parsed))

    await asyncio.gather(*(one(u) for u in urls))
    return results
