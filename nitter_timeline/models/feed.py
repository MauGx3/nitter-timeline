from __future__ import annotations
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class FeedItem(BaseModel):
    id: str  # guid or constructed unique key
    author: str
    author_url: Optional[HttpUrl] = None
    content_html: str
    summary: Optional[str] = None
    link: Optional[HttpUrl] = None
    published: Optional[datetime] = None
    avatar_url: Optional[HttpUrl] = None
    raw: dict | None = None

class AggregatedTimeline(BaseModel):
    items: list[FeedItem]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
