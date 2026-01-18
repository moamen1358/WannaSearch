"""NewsAPI.org search provider."""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Optional

import httpx

from app.providers.base import SearchProvider, SearchResponse, SearchResult

logger = logging.getLogger("providers.newsapi")

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.json"


def _load_api_key() -> Optional[str]:
    """Load API key from config or environment."""
    # Check environment variable first
    key = os.environ.get("NEWSAPI_KEY")
    if key:
        return key

    # Fall back to config file
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                return config.get("newsapi_key")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    return None


class NewsAPIProvider(SearchProvider):
    """Search provider for NewsAPI.org."""

    PROVIDER_ID = "newsapi"
    PROVIDER_NAME = "NewsAPI"
    PROVIDER_DESCRIPTION = "Search news via NewsAPI.org (100 req/day free)"

    API_URL = "https://newsapi.org/v2/everything"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or _load_api_key()

    def _parse_response(self, data: dict, limit: int) -> List[SearchResult]:
        """Parse API response into SearchResult objects."""
        results = []
        articles = data.get("articles", [])

        for article in articles[:limit]:
            source_name = None
            if article.get("source"):
                source_name = article["source"].get("name")

            results.append(SearchResult(
                title=article.get("title", ""),
                link=article.get("url", ""),
                published=article.get("publishedAt"),
                source=source_name,
            ))

        return results

    def search(self, query: str, limit: int = 10) -> SearchResponse:
        """Execute synchronous search."""
        import requests

        start = time.time()

        if not self.api_key:
            logger.error("NewsAPI key not configured")
            return SearchResponse(
                query=query,
                results=[],
                total=0,
                duration=time.time() - start,
            )

        params = {
            "q": query,
            "pageSize": limit,
            "sortBy": "relevancy",
        }
        headers = {"X-Api-Key": self.api_key}

        try:
            resp = requests.get(self.API_URL, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                results = []
            else:
                results = self._parse_response(data, limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            results = []

        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
            duration=time.time() - start,
        )

    async def search_async(self, query: str, limit: int = 10) -> SearchResponse:
        """Execute async search."""
        start = time.time()

        if not self.api_key:
            logger.error("NewsAPI key not configured")
            return SearchResponse(
                query=query,
                results=[],
                total=0,
                duration=time.time() - start,
            )

        params = {
            "q": query,
            "pageSize": limit,
            "sortBy": "relevancy",
        }
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(self.API_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                if data.get("status") != "ok":
                    logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                    results = []
                else:
                    results = self._parse_response(data, limit)
        except Exception as e:
            logger.error(f"Async search failed: {e}")
            results = []

        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
            duration=time.time() - start,
        )
