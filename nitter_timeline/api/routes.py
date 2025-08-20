from fastapi import APIRouter, Query
from ..services.fetcher import fetch_many
from ..services.aggregator import aggregate
from ..core.config import settings

api_router = APIRouter()

@api_router.get("/timeline")
async def get_timeline(feeds: list[str] | None = Query(None), limit: int = 100):
    feed_urls = feeds or settings.default_feeds
    fetched = await fetch_many(feed_urls)
    agg = aggregate(fetched, limit=limit)
    return agg
