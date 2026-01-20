"""Tests for search providers."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.providers.base import SearchResult, SearchResponse
from app.providers.google_news import GoogleNewsProvider


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_create_search_result(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            title="Test Title",
            link="https://example.com",
            published="Mon, 20 Jan 2026 10:00:00 GMT",
            source="Test Source"
        )
        assert result.title == "Test Title"
        assert result.link == "https://example.com"
        assert result.published == "Mon, 20 Jan 2026 10:00:00 GMT"
        assert result.source == "Test Source"

    def test_create_search_result_minimal(self):
        """Test creating a SearchResult with minimal fields."""
        result = SearchResult(title="Title", link="https://example.com")
        assert result.title == "Title"
        assert result.link == "https://example.com"
        assert result.published is None
        assert result.source is None


class TestSearchResponse:
    """Tests for SearchResponse dataclass."""

    def test_create_search_response(self):
        """Test creating a SearchResponse."""
        results = [SearchResult(title="Test", link="https://example.com")]
        response = SearchResponse(
            query="test query",
            results=results,
            total=1,
            duration=0.5,
            company_name="TestCo",
            url="https://example.com/search"
        )
        assert response.query == "test query"
        assert len(response.results) == 1
        assert response.total == 1
        assert response.duration == 0.5
        assert response.company_name == "TestCo"
        assert response.url == "https://example.com/search"


class TestGoogleNewsProvider:
    """Tests for GoogleNewsProvider."""

    def test_provider_attributes(self, google_news_provider):
        """Test provider class attributes."""
        assert google_news_provider.PROVIDER_ID == "google_news_rss"
        assert google_news_provider.PROVIDER_NAME == "Google News RSS"
        assert "Google News RSS" in google_news_provider.PROVIDER_DESCRIPTION

    def test_build_query_with_company_and_query(self, google_news_provider):
        """Test query building with company and query."""
        query = google_news_provider._build_query(
            query="data breach",
            company_name="Microsoft"
        )
        assert "Microsoft" in query
        assert "data breach" in query
        assert "AND" in query

    def test_build_query_company_only(self, google_news_provider):
        """Test query building with company only."""
        query = google_news_provider._build_query(
            query="",
            company_name="Google"
        )
        assert query == "Google"

    def test_build_query_with_country(self, google_news_provider):
        """Test query building with country filter."""
        query = google_news_provider._build_query(
            query="news",
            country="USA"
        )
        assert "location:USA" in query

    def test_build_query_with_time_days(self, google_news_provider):
        """Test query building with time filter."""
        query = google_news_provider._build_query(
            query="news",
            time_days=30
        )
        assert "after:" in query
        # Check date is approximately 30 days ago
        expected_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        assert expected_date in query

    def test_build_query_full(self, google_news_provider):
        """Test query building with all parameters."""
        query = google_news_provider._build_query(
            query="AI",
            company_name="OpenAI",
            time_days=7,
            country="USA"
        )
        assert "OpenAI" in query
        assert "AI" in query
        assert "location:USA" in query
        assert "after:" in query

    def test_build_url(self, google_news_provider):
        """Test URL building."""
        url = google_news_provider._build_url("test query")
        assert url.startswith("https://news.google.com/rss/search")
        assert "q=" in url
        assert "hl=en-US" in url

    def test_parse_feed(self, google_news_provider, mock_rss_response):
        """Test RSS feed parsing."""
        results = google_news_provider._parse_feed(mock_rss_response, limit=10)
        assert len(results) == 2
        assert results[0].title == "Test Article 1"
        assert results[1].title == "Test Article 2"

    def test_parse_feed_with_limit(self, google_news_provider, mock_rss_response):
        """Test RSS feed parsing with limit."""
        results = google_news_provider._parse_feed(mock_rss_response, limit=1)
        assert len(results) == 1

    def test_parse_empty_feed(self, google_news_provider, empty_rss_response):
        """Test parsing empty RSS feed."""
        results = google_news_provider._parse_feed(empty_rss_response, limit=10)
        assert len(results) == 0

    @patch('requests.get')
    def test_search_sync(self, mock_get, google_news_provider, mock_rss_response):
        """Test synchronous search."""
        mock_response = MagicMock()
        mock_response.content = mock_rss_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = google_news_provider.search("test", limit=10)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        assert result.total == 2
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_search_sync_error(self, mock_get, google_news_provider):
        """Test synchronous search with error."""
        mock_get.side_effect = Exception("Network error")

        result = google_news_provider.search("test", limit=10)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_search_async(self, google_news_provider, mock_rss_response):
        """Test asynchronous search."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.content = mock_rss_response
            mock_response.raise_for_status = MagicMock()

            mock_client_instance = MagicMock()
            mock_client_instance.get = MagicMock(return_value=mock_response)
            mock_client_instance.__aenter__ = MagicMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = MagicMock(return_value=None)
            mock_client.return_value = mock_client_instance

            result = await google_news_provider.search_async("test", limit=10)

            assert isinstance(result, SearchResponse)


class TestProviderRegistry:
    """Tests for provider registry."""

    def test_list_providers(self):
        """Test listing providers."""
        from app.providers import list_providers
        providers = list_providers()
        assert len(providers) >= 1
        assert any(p["id"] == "google_news_rss" for p in providers)

    def test_get_provider(self):
        """Test getting a provider by ID."""
        from app.providers import get_provider
        provider = get_provider("google_news_rss")
        assert provider is not None
        assert isinstance(provider, GoogleNewsProvider)

    def test_get_unknown_provider(self):
        """Test getting an unknown provider."""
        from app.providers import get_provider
        provider = get_provider("unknown_provider")
        assert provider is None
