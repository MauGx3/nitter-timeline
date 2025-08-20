"""Data models for timeline feed items."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class FeedItem(BaseModel):  # pylint: disable=too-few-public-methods
    """Normalized representation of a single post/tweet surrogate.

    Attributes:
        id: Stable synthetic identifier (hash of entry fields).
        author: Display name or handle of the poster.
        author_url: Optional link to the author's profile.
        content_html: Renderable HTML (sanitized upstream if needed).
        summary: Plain-text / summary fallback content.
        link: Permalink to the original post.
        published: Parsed publication datetime (UTC assumed if naive).
        avatar_url: Optional avatar image URL (future enhancement field).
        raw: Original feed entry mapping (for debugging / future parsing).
    """

    id: str
    author: str
    author_url: HttpUrl | None = None
    content_html: str
    summary: str | None = None
    link: HttpUrl | None = None
    published: datetime | None = None
    avatar_url: HttpUrl | None = None
    raw: dict | None = None


class AggregatedTimeline(BaseModel):  # pylint: disable=too-few-public-methods
    """Container for a slice of timeline items with (future) cursors.

    Attributes:
        items: Ordered feed items (newest first).
        next_cursor: Opaque cursor for fetching the next page (TODO).
        prev_cursor: Opaque cursor for fetching the previous page (TODO).
    """

    items: list[FeedItem]
    next_cursor: str | None = None
    prev_cursor: str | None = None
