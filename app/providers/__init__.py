"""Simple provider registry for search providers."""

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional
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


def setup_logging() -> None:
    """Setup logging based on config."""
    log_config = _config.get("logging", {})

    level = getattr(logging, log_config.get("level", "INFO"), logging.INFO)
    log_format = log_config.get("format", "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    date_format = log_config.get("date_format", "%Y-%m-%d %H:%M:%S")
    log_file = log_config.get("log_file", "logs/search.log")

    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)

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
