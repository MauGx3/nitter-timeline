import pytest

from nitter_timeline.models.feed import FeedItem
from nitter_timeline.services.aggregator import aggregate


@pytest.mark.asyncio
async def test_aggregate_basic():
    fake_feed = {
        "entries": [
            {
                "id": "1",
                "author": "a",
                "summary": "hello",
                "published": "2024-01-01T00:00:00Z",
            },
            {
                "id": "2",
                "author": "b",
                "summary": "world",
                "published": "2024-01-02T00:00:00Z",
            },
        ]
    }
    agg = aggregate([("u", fake_feed)], limit=10)
    assert len(agg.items) == 2
    assert isinstance(agg.items[0], FeedItem)
