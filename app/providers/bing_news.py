"""Bing News RSS search provider."""

import time
import random
import logging
import urllib.parse
from typing import List

import feedparser
import httpx

from app.providers.base import SearchProvider, SearchResponse, SearchResult

logger = logging.getLogger("providers.bing_news")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class BingNewsProvider(SearchProvider):
    """Search provider for Bing News RSS feeds."""

    PROVIDER_ID = "bing_news_rss"
    PROVIDER_NAME = "Bing News RSS"
    PROVIDER_DESCRIPTION = "Search news via Bing News RSS feeds"

    RSS_URL = "https://www.bing.com/news/search"

    def __init__(self, user_agents: List[str] = None):
        self.user_agents = user_agents or USER_AGENTS

    def _build_url(self, query: str) -> str:
        """Build the RSS URL for a query."""
        encoded = urllib.parse.quote(query)
        return f"{self.RSS_URL}?format=rss&q={encoded}"

    def _parse_feed(self, content: bytes, limit: int) -> List[SearchResult]:
        """Parse RSS feed into SearchResult objects."""
        feed = feedparser.parse(content)
        results = []

        for entry in feed.entries[:limit]:
            # Extract source from the entry if available
            source = None
            if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                source = entry.source.title
            elif hasattr(entry, 'publisher'):
                source = entry.publisher

            results.append(SearchResult(
                title=getattr(entry, 'title', ''),
                link=getattr(entry, 'link', ''),
                published=getattr(entry, 'published', None),
                source=source,
            ))

        return results

    def search(self, query: str, limit: int = 10) -> SearchResponse:
        """Execute synchronous search."""
        import requests

        start = time.time()
        url = self._build_url(query)
        headers = {"User-Agent": random.choice(self.user_agents)}

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            results = self._parse_feed(resp.content, limit)
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
        url = self._build_url(query)
        headers = {"User-Agent": random.choice(self.user_agents)}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                results = self._parse_feed(resp.content, limit)
        except Exception as e:
            logger.error(f"Async search failed: {e}")
            results = []

        return SearchResponse(
            query=query,
            results=results,
            total=len(results),
            duration=time.time() - start,
        )
