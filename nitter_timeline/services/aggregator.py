"""Feed aggregation & normalization utilities.

Takes multiple parsed RSS feeds (dicts from feedparser) and produces
de-duplicated, chronologically sorted timeline items.
"""
from __future__ import annotations

import hashlib
from collections.abc import Sequence

from dateutil import parser as dateparser

from nitter_timeline.core.config import settings
from nitter_timeline.models.feed import AggregatedTimeline, FeedItem
from nitter_timeline.services.sanitize import sanitize_html


def _make_id(entry: dict) -> str:
    """Construct a stable synthetic identifier for a feed entry.

    Concatenates several candidate uniqueness fields (guid/id/link/title)
    and hashes them with SHA-256 (truncated for brevity) to mitigate
    collisions while providing deterministic IDs for de-duplication.

    Args:
        entry: Raw feed entry mapping from *feedparser*.

    Returns:
    str: 24-character hex digest identifier.
    """
    parts = [
        entry.get("id"),
        entry.get("guid"),
        entry.get("link"),
        entry.get("title"),
    ]
    key = "|".join([p for p in parts if p])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def parse_items(parsed_feed: dict) -> list[FeedItem]:
    """Convert a parsed feed dictionary into `FeedItem` objects.

    Extracts publication timestamp, author, HTML content (preferring the
    first ``content`` block then falling back to ``summary``), and builds a
    normalized representation used by the UI layer.

    Args:
        parsed_feed: Structure returned by *feedparser.parse*.

    Returns:
        list[FeedItem]: Normalized feed items (may be empty).
    """
    items: list[FeedItem] = []
    feed_entries = parsed_feed.get("entries", [])
    for e in feed_entries:
        published = None
        if dt := e.get("published") or e.get("updated"):
            try:
                published = dateparser.parse(dt)
            except Exception:  # pylint: disable=broad-except
                # fall back to None; downstream sorts handle it
                published = None
        content_html = ""
        if e.get("content"):
            first = e["content"][0]
            content_html = first.get("value", "")
        else:
            content_html = e.get("summary", "")
        if settings.sanitize_html:
            content_html = sanitize_html(content_html)
        items.append(
            FeedItem(
                id=_make_id(e),
                author=e.get("author", "unknown"),
                author_url=e.get("author_detail", {}).get("href")
                if e.get("author_detail")
                else None,
                content_html=content_html,
                summary=e.get("summary"),
                link=e.get("link"),
                published=published,
                avatar_url=None,
                raw=e,
            )
        )
    return items


def aggregate(
    feeds: Sequence[tuple[str, dict]],
    limit: int = 100,
) -> AggregatedTimeline:
    """Aggregate multiple parsed feeds into a single timeline.

    Steps:
      1. Flatten all entries.
    2. De-duplicate by synthetic ID.
      3. Sort descending by published timestamp (missing dates treated as 0).
      4. Truncate to ``limit``.

    Args:
        feeds: Sequence of ``(url, parsed_feed_dict)`` pairs.
        limit: Maximum number of timeline items to include.

    Returns:
        AggregatedTimeline: Timeline slice containing up to ``limit`` items.
    """
    all_items: list[FeedItem] = []
    for _url, parsed in feeds:
        all_items.extend(parse_items(parsed))

    # Deduplicate by id (later: pick earliest/latest deterministically)
    uniq: dict[str, FeedItem] = {item.id: item for item in all_items}
    sorted_items = sorted(
        uniq.values(), key=lambda x: (x.published or 0), reverse=True
    )
    return AggregatedTimeline(items=sorted_items[:limit])
