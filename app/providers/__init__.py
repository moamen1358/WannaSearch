"""Simple provider registry for search providers."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from app.providers.base import SearchProvider

# Provider registry
_providers: Dict[str, SearchProvider] = {}

# Global config
_config: dict = {}

# Load config
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.json"


def load_config() -> dict:
    """Load configuration from config.json."""
    global _config
    try:
        with open(CONFIG_PATH) as f:
            _config = json.load(f)
            return _config
    except Exception:
        return {}


def get_config() -> dict:
    """Get the loaded configuration."""
    return _config


def get_cairo_time() -> datetime:
    """Get current time in Cairo timezone."""
    tz = ZoneInfo("Africa/Cairo")
    return datetime.now(tz)


def get_cairo_timestamp() -> str:
    """Get formatted timestamp in Cairo timezone."""
    cairo_time = get_cairo_time()
    return cairo_time.strftime("%Y-%m-%d_%H-%M-%S")


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Replace spaces and special chars with underscores
    sanitized = re.sub(r'[^\w\-]', '_', name)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Strip leading/trailing underscores
    return sanitized.strip('_')


def create_search_log(company_name: str, results: list, url: str, query: str) -> str:
    """Create a new log file for a search with Cairo timezone timestamp.

    Returns the path to the created log file.
    """
    log_config = _config.get("logging", {})
    log_dir = log_config.get("log_dir", "logs")

    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create filename with company name and Cairo timestamp
    timestamp = get_cairo_timestamp()
    safe_company = sanitize_filename(company_name) if company_name else "search"
    log_filename = f"{safe_company}_{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)

    # Write log file
    cairo_time = get_cairo_time()
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Search Log - {cairo_time.strftime('%Y-%m-%d %H:%M:%S')} (Cairo Time)\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Company: {company_name or 'N/A'}\n")
        f.write(f"Query: {query}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Results: {len(results)}\n")
        f.write("\n" + "-" * 60 + "\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"[{i}] {result.get('title', 'N/A')}\n")
            f.write(f"    Source: {result.get('source', 'N/A')}\n")
            f.write(f"    Published: {result.get('published', 'N/A')}\n")
            f.write(f"    Link: {result.get('link', 'N/A')}\n\n")

    return log_path


def setup_logging() -> None:
    """Setup logging based on config."""
    log_config = _config.get("logging", {})

    level = getattr(logging, log_config.get("level", "INFO"), logging.INFO)
    log_format = log_config.get("format", "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    date_format = log_config.get("date_format", "%Y-%m-%d %H:%M:%S")
    log_dir = log_config.get("log_dir", "logs")

    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler only (per-search logs are created separately)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    for lib in ["httpx", "httpcore", "urllib3"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


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

    config = load_config()
    setup_logging()

    user_agents = config.get("user_agents", [])
    search_config = config.get("search", {})

    register(GoogleNewsProvider(
        user_agents=user_agents if user_agents else None,
        search_config=search_config
    ))


# Auto-discover on import
discover_providers()
