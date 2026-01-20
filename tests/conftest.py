"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.providers.base import SearchResult, SearchResponse
from app.providers.google_news import GoogleNewsProvider


@pytest.fixture
def mock_rss_response():
    """Mock RSS feed response."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test News</title>
            <item>
                <title>Test Article 1</title>
                <link>https://example.com/article1</link>
                <pubDate>Mon, 20 Jan 2026 10:00:00 GMT</pubDate>
                <source url="https://example.com">Example News</source>
            </item>
            <item>
                <title>Test Article 2</title>
                <link>https://example.com/article2</link>
                <pubDate>Sun, 19 Jan 2026 09:00:00 GMT</pubDate>
                <source url="https://test.com">Test Source</source>
            </item>
        </channel>
    </rss>"""


@pytest.fixture
def empty_rss_response():
    """Mock empty RSS feed response."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Empty News</title>
        </channel>
    </rss>"""


@pytest.fixture
def google_news_provider():
    """Create a GoogleNewsProvider instance."""
    return GoogleNewsProvider(
        user_agents=["TestAgent/1.0"],
        search_config={"time_range_years": 1}
    )


@pytest.fixture
def mock_search_response():
    """Create a mock SearchResponse."""
    return SearchResponse(
        query="test query",
        results=[
            SearchResult(
                title="Test Article",
                link="https://example.com/test",
                published="Mon, 20 Jan 2026 10:00:00 GMT",
                source="Test Source"
            )
        ],
        total=1,
        duration=0.5,
        company_name="TestCompany",
        url="https://news.google.com/rss/search?q=test"
    )


@pytest.fixture
def api_client():
    """Create a test client for the API."""
    from app.api.search_api import app
    return TestClient(app)
