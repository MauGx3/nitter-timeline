from __future__ import annotations
from typing import Iterable, Sequence
from ..models.feed import FeedItem, AggregatedTimeline
from dateutil import parser as dateparser
import hashlib

def _make_id(entry: dict) -> str:
    parts = [entry.get("id"), entry.get("guid"), entry.get("link"), entry.get("title")]
    key = "|".join([p for p in parts if p])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]

def parse_items(parsed_feed: dict) -> list[FeedItem]:
    items: list[FeedItem] = []
    feed_entries = parsed_feed.get("entries", [])
    for e in feed_entries:
        published = None
        if dt := e.get("published") or e.get("updated"):
            try:
                published = dateparser.parse(dt)
            except Exception:
                published = None
        content_html = ""
        if e.get("content"):
            first = e["content"][0]
            content_html = first.get("value", "")
        else:
            content_html = e.get("summary", "")
        items.append(
            FeedItem(
                id=_make_id(e),
                author=e.get("author", "unknown"),
                author_url=e.get("author_detail", {}).get("href") if e.get("author_detail") else None,
                content_html=content_html,
                summary=e.get("summary"),
                link=e.get("link"),
                published=published,
                avatar_url=None,
                raw=e,
            )
        )
    return items

def aggregate(feeds: Sequence[tuple[str, dict]], limit: int = 100) -> AggregatedTimeline:
    all_items: list[FeedItem] = []
    for _url, parsed in feeds:
        all_items.extend(parse_items(parsed))
    # dedupe by id
    uniq: dict[str, FeedItem] = {}
    for item in all_items:
        uniq[item.id] = item
    sorted_items = sorted(uniq.values(), key=lambda x: (x.published or 0), reverse=True)
    return AggregatedTimeline(items=sorted_items[:limit])
