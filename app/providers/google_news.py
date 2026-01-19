"""Google News RSS search provider."""

import time
import random
import logging
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import feedparser
import httpx

from app.providers.base import SearchProvider, SearchResponse, SearchResult

logger = logging.getLogger("providers.google_news")

# Default user agents (used if config doesn't provide any)
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class GoogleNewsProvider(SearchProvider):
    """Search provider for Google News RSS feeds."""

    PROVIDER_ID = "google_news_rss"
    PROVIDER_NAME = "Google News RSS"
    PROVIDER_DESCRIPTION = "Search news via Google News RSS feeds"

    RSS_URL = "https://news.google.com/rss/search"

    def __init__(
        self,
        user_agents: List[str] = None,
        proxies: List[str] = None,
        search_config: Dict[str, Any] = None
    ):
        self.user_agents = user_agents or DEFAULT_USER_AGENTS
        self.proxies = proxies or []
        self.search_config = search_config or {}
        self.time_range_years = self.search_config.get("time_range_years", 1.5)

    def _build_query(
        self,
        query: str,
        company_name: Optional[str] = None,
        time_days: Optional[int] = None
    ) -> str:
        """Build the search query with company name, query, and time filter."""
        parts = []

        # Add company name if provided
        if company_name:
            parts.append(company_name)

        # Add query if provided
        if query:
            parts.append(query)

        # Build the final query
        if len(parts) > 1:
            search_query = " AND ".join(parts)
        elif parts:
            search_query = parts[0]
        else:
            search_query = ""

        # Add time filter if provided
        if time_days is not None:
            after_date = datetime.now() - timedelta(days=time_days)
            date_str = after_date.strftime("%Y-%m-%d")
            search_query = f"{search_query} after:{date_str}"

        return search_query

    def _build_url(self, query: str) -> str:
        """Build the RSS URL for a query."""
        encoded = urllib.parse.quote(query)
        return f"{self.RSS_URL}?q={encoded}&hl=en-US&gl=US&ceid=US:en"

    def _parse_feed(self, content: bytes, limit: int) -> List[SearchResult]:
        """Parse RSS feed into SearchResult objects."""
        feed = feedparser.parse(content)
        results = []

        for entry in feed.entries[:limit]:
            results.append(SearchResult(
                title=getattr(entry, 'title', ''),
                link=getattr(entry, 'link', ''),
                published=getattr(entry, 'published', None),
                source=entry.source.title if hasattr(entry, 'source') else None,
            ))

        return results

    def search(
        self,
        query: str,
        limit: int = 10,
        company_name: Optional[str] = None,
        time_days: Optional[int] = None
    ) -> SearchResponse:
        """Execute synchronous search."""
        import requests

        start = time.time()
        search_query = self._build_query(query, company_name, time_days)
        url = self._build_url(search_query)
        headers = {"User-Agent": random.choice(self.user_agents)}

        logger.info(f"Search request: company='{company_name}', query='{search_query}', time_days={time_days}")
        logger.info(f"Search URL: {url}")

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            results = self._parse_feed(resp.content, limit)
            logger.info(f"Search completed: found {len(results)} results")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            results = []

        return SearchResponse(
            query=search_query,
            results=results,
            total=len(results),
            duration=time.time() - start,
            company_name=company_name,
            url=url,
        )

    async def search_async(
        self,
        query: str,
        limit: int = 10,
        company_name: Optional[str] = None,
        time_days: Optional[int] = None
    ) -> SearchResponse:
        """Execute async search."""
        start = time.time()
        search_query = self._build_query(query, company_name, time_days)
        url = self._build_url(search_query)
        headers = {"User-Agent": random.choice(self.user_agents)}

        logger.info(f"Async search request: company='{company_name}', query='{search_query}', time_days={time_days}")
        logger.info(f"Search URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                results = self._parse_feed(resp.content, limit)
                logger.info(f"Async search completed: found {len(results)} results")
        except Exception as e:
            logger.error(f"Async search failed: {e}")
            results = []

        return SearchResponse(
            query=search_query,
            results=results,
            total=len(results),
            duration=time.time() - start,
            company_name=company_name,
            url=url,
        )
