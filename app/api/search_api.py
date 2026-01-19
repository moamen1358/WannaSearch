"""Scalable News Search API."""

import time
import logging
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from cachetools import TTLCache

from app.providers import get_provider, list_providers

# Logger (configured by providers module on import)
logger = logging.getLogger("api")


# =============================================================================
# Config & Cache
# =============================================================================

class Config:
    """App configuration."""
    cache_ttl: int = 300
    cache_size: int = 1000
    rate_limit: int = 100
    rate_window: int = 60


config = Config()
cache: TTLCache = None
rate_limits: Dict[str, List[float]] = {}


def check_rate_limit(client_ip: str) -> bool:
    """Check if client is within rate limit."""
    now = time.time()
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []

    # Clean old entries
    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < config.rate_window]

    if len(rate_limits[client_ip]) >= config.rate_limit:
        return False

    rate_limits[client_ip].append(now)
    return True


# =============================================================================
# App Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache
    logger.info("Starting API...")
    cache = TTLCache(maxsize=config.cache_size, ttl=config.cache_ttl)
    providers = list_providers()
    logger.info(f"Providers: {[p['id'] for p in providers]}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="WannaSearch API",
    version="3.0.0",
    description="Scalable news search with caching and rate limiting",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Models
# =============================================================================

class SearchRequest(BaseModel):
    query: str = Field(default="", max_length=500)
    company_name: Optional[str] = Field(default=None, max_length=200)
    country: Optional[str] = Field(default=None, max_length=100, description="Company location/country")
    time_days: Optional[int] = Field(default=None, ge=1, le=3650, description="Time range in days")
    provider: str = "google_news_rss"
    limit: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    title: str
    link: str
    published: Optional[str] = None
    source: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    company_name: Optional[str] = None
    provider: str
    results: List[SearchResult]
    total: int
    duration: float
    cached: bool = False


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "providers": [p["id"] for p in list_providers()],
        "cache_size": len(cache) if cache else 0,
    }


@app.get("/providers")
async def providers():
    """List search providers."""
    return {"providers": list_providers()}


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest, request: Request):
    """Search for news."""
    client_ip = request.client.host if request.client else "unknown"

    # Validate: either query or company_name must be provided
    if not req.query and not req.company_name:
        raise HTTPException(400, "Either 'query' or 'company_name' must be provided")

    if not check_rate_limit(client_ip):
        raise HTTPException(429, "Rate limit exceeded")

    start = time.time()

    # Check cache
    cache_key = f"{req.provider}:{req.query}:{req.company_name}:{req.country}:{req.time_days}:{req.limit}"
    if cache and cache_key in cache:
        data = cache[cache_key]
        return SearchResponse(
            query=data.get("query", req.query),
            company_name=req.company_name,
            provider=req.provider,
            results=data["results"],
            total=data["total"],
            duration=time.time() - start,
            cached=True,
        )

    # Get provider
    provider = get_provider(req.provider)
    if not provider:
        raise HTTPException(400, f"Unknown provider: {req.provider}")

    logger.info(f"Search: company='{req.company_name}', country='{req.country}', query='{req.query[:50] if req.query else ''}', time_days={req.time_days} via {req.provider}")

    # Execute search
    try:
        result = await provider.search_async(req.query, limit=req.limit, company_name=req.company_name, time_days=req.time_days, country=req.country)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(500, str(e))

    # Convert results
    items = [
        SearchResult(title=r.title, link=r.link, published=r.published, source=r.source)
        for r in result.results
    ]

    # Cache
    if cache is not None:
        cache[cache_key] = {"results": items, "total": len(items), "query": result.query}

    duration = time.time() - start
    logger.info(f"Found {len(items)} results in {duration:.2f}s")

    return SearchResponse(
        query=result.query,
        company_name=req.company_name,
        provider=req.provider,
        results=items,
        total=len(items),
        duration=duration,
        cached=False,
    )


@app.delete("/cache")
async def clear_cache():
    """Clear search cache."""
    if cache:
        cache.clear()
    return {"status": "ok"}


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.search_api:app", host="0.0.0.0", port=8001, reload=True)
