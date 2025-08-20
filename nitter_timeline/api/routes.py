"""API route definitions for timeline endpoints."""
from fastapi import APIRouter, Query

from nitter_timeline.core.config import settings
from nitter_timeline.services.aggregator import aggregate
from nitter_timeline.services.fetcher import fetch_many

api_router = APIRouter()

@api_router.get("/timeline", summary="Aggregate timeline")
async def get_timeline(
    feeds: list[str] | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    """Return an aggregated, sorted timeline.

    Query Parameters:
        feeds: Optional repeatable feed URL(s). If omitted, the configured
            ``default_feeds`` are used.
        limit: Maximum number of items returned (default 100).

    Returns:
        AggregatedTimeline: JSON-serializable Pydantic model with items.
    """
    # Using Query for limit validation; feeds left as raw list.
    # FastAPI handles parsing of repeated query params into a list.
    feed_urls = feeds or settings.default_feeds
    fetched = await fetch_many(feed_urls)
    return aggregate(fetched, limit=limit)
