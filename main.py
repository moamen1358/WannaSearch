import argparse
import json
import logging
import sys
import os
from app.services.news_search import search_google_news_rss

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/search.log")
    ]
)
logger = logging.getLogger("cli")

def main():
    parser = argparse.ArgumentParser(description="News Search CLI - Search Google News RSS")

    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Number of results (default: 10)")

    args = parser.parse_args()

    logger.info(f"Searching for: {args.query}")
    results = search_google_news_rss(args.query, limit=args.limit)

    if results:
        logger.info(f"Found {len(results)} results")
        print(json.dumps(results, indent=4, ensure_ascii=False))
    else:
        logger.warning("No results found")
        print(json.dumps([], indent=4))

if __name__ == "__main__":
    main()
