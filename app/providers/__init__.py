"""Simple provider registry for search providers."""

from typing import Dict, List, Optional
from app.providers.base import SearchProvider

# Provider registry
_providers: Dict[str, SearchProvider] = {}


def register(provider: SearchProvider) -> None:
    """Register a search provider."""
    _providers[provider.PROVIDER_ID] = provider


def get_provider(provider_id: str) -> Optional[SearchProvider]:
    """Get a provider by ID."""
    return _providers.get(provider_id)


def list_providers() -> List[Dict[str, str]]:
    """List all registered providers."""
    return [
        {
            "id": p.PROVIDER_ID,
            "name": p.PROVIDER_NAME,
            "description": p.PROVIDER_DESCRIPTION,
        }
        for p in _providers.values()
    ]


def discover_providers() -> None:
    """Import and register all providers."""
    from app.providers.google_news import GoogleNewsProvider
    register(GoogleNewsProvider())


# Auto-discover on import
discover_providers()
