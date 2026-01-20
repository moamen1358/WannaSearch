"""Tests for the Search API."""

from unittest.mock import patch, MagicMock, AsyncMock



class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "providers" in data

    def test_health_includes_providers(self, api_client):
        """Test health check includes provider list."""
        response = api_client.get("/health")
        data = response.json()
        assert "google_news_rss" in data["providers"]


class TestProvidersEndpoint:
    """Tests for providers endpoint."""

    def test_list_providers(self, api_client):
        """Test listing providers."""
        response = api_client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) >= 1

    def test_provider_structure(self, api_client):
        """Test provider data structure."""
        response = api_client.get("/providers")
        data = response.json()
        provider = data["providers"][0]
        assert "id" in provider
        assert "name" in provider
        assert "description" in provider


class TestSearchEndpoint:
    """Tests for search endpoint."""

    def test_search_requires_query_or_company(self, api_client):
        """Test search requires either query or company_name."""
        response = api_client.post("/search", json={})
        assert response.status_code == 400
        assert "query" in response.json()["detail"].lower() or "company" in response.json()["detail"].lower()

    def test_search_with_query(self, api_client, mock_search_response):
        """Test search with query parameter."""
        with patch('app.api.search_api.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.search_async = AsyncMock(return_value=mock_search_response)
            mock_get_provider.return_value = mock_provider

            response = api_client.post("/search", json={"query": "test news"})

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "total" in data
            assert "duration" in data

    def test_search_with_company_name(self, api_client, mock_search_response):
        """Test search with company_name parameter."""
        with patch('app.api.search_api.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.search_async = AsyncMock(return_value=mock_search_response)
            mock_get_provider.return_value = mock_provider

            response = api_client.post("/search", json={"company_name": "TestCompany"})

            assert response.status_code == 200

    def test_search_with_all_parameters(self, api_client, mock_search_response):
        """Test search with all parameters."""
        with patch('app.api.search_api.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.search_async = AsyncMock(return_value=mock_search_response)
            mock_get_provider.return_value = mock_provider

            response = api_client.post("/search", json={
                "query": "AI news",
                "company_name": "OpenAI",
                "country": "USA",
                "time_days": 30,
                "limit": 20,
                "provider": "google_news_rss"
            })

            assert response.status_code == 200

    def test_search_unknown_provider(self, api_client):
        """Test search with unknown provider."""
        response = api_client.post("/search", json={
            "query": "test",
            "provider": "unknown_provider"
        })
        assert response.status_code == 400
        assert "unknown" in response.json()["detail"].lower()

    def test_search_validates_limit(self, api_client):
        """Test search validates limit parameter."""
        response = api_client.post("/search", json={
            "query": "test",
            "limit": 0
        })
        assert response.status_code == 422  # Validation error

    def test_search_validates_time_days(self, api_client):
        """Test search validates time_days parameter."""
        response = api_client.post("/search", json={
            "query": "test",
            "time_days": 0
        })
        assert response.status_code == 422  # Validation error

    def test_search_response_structure(self, api_client, mock_search_response):
        """Test search response structure."""
        with patch('app.api.search_api.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.search_async = AsyncMock(return_value=mock_search_response)
            mock_get_provider.return_value = mock_provider

            response = api_client.post("/search", json={"query": "test"})

            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "provider" in data
            assert "results" in data
            assert "total" in data
            assert "duration" in data
            assert "cached" in data


class TestCacheEndpoint:
    """Tests for cache endpoint."""

    def test_clear_cache(self, api_client):
        """Test clearing cache."""
        response = api_client.delete("/cache")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_check(self):
        """Test rate limit function."""
        from app.api.search_api import check_rate_limit, rate_limits, config

        # Clear any existing limits
        rate_limits.clear()

        # First request should pass
        assert check_rate_limit("test_ip") is True

        # Fill up the limit
        for _ in range(config.rate_limit - 1):
            check_rate_limit("test_ip")

        # Next request should fail
        assert check_rate_limit("test_ip") is False

        # Different IP should still pass
        assert check_rate_limit("different_ip") is True
