"""Async feed fetching utilities.

Responsible for retrieving individual or multiple RSS feeds concurrently
with a small in-memory TTL cache to reduce network load.
"""
from __future__ import annotations

import asyncio
import ipaddress
import logging
import socket
from collections.abc import Iterable
from urllib.parse import urlparse

import feedparser
import httpx
from cachetools import TTLCache

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

    def _valid(url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in settings.allowed_feed_schemes:
                return False
            if settings.enforce_https_feeds and parsed.scheme != "https":
                return False
            host = parsed.hostname or ""
            if not any(
                host.endswith(suf)
                for suf in settings.allowed_feed_domain_suffixes
            ):
                return False
            # Resolve and ensure not private
            for info in socket.getaddrinfo(host, None):
                ip = ipaddress.ip_address(info[4][0])
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
            return True
        except Exception:  # validation failure -> False
            return False

    async def one(feed_url: str) -> None:
        parsed = await fetch_feed(feed_url)
        if parsed:
            results.append((feed_url, parsed))

    filtered = []
    for u in urls:
        if _valid(u):
            filtered.append(u)
            if len(filtered) >= settings.max_feeds_per_request:
                break
    await asyncio.gather(*(one(u) for u in filtered))
    return results
