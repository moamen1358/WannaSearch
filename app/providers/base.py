"""Base class for search providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    link: str
    published: Optional[str] = None
    source: Optional[str] = None


@dataclass
class SearchResponse:
    """Response from a search provider."""
    query: str
    results: List[SearchResult]
    total: int
    duration: float = 0.0
    company_name: Optional[str] = None
    url: Optional[str] = None


class SearchProvider(ABC):
    """Abstract base class for search providers."""

    PROVIDER_ID: str = ""
    PROVIDER_NAME: str = ""
    PROVIDER_DESCRIPTION: str = ""

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
        company_name: Optional[str] = None,
        time_days: Optional[int] = None
    ) -> SearchResponse:
        """Execute a search query."""
        pass

    @abstractmethod
    async def search_async(
        self,
        query: str,
        limit: int = 10,
        company_name: Optional[str] = None,
        time_days: Optional[int] = None
    ) -> SearchResponse:
        """Execute an async search query."""
        pass
