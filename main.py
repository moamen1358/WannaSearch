"""WannaSearch CLI."""

import argparse
import json
import sys

from app.providers import get_provider, list_providers


def main():
    parser = argparse.ArgumentParser(description="WannaSearch - News Search CLI")
    parser.add_argument("-q", "--query", help="Search query")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("-p", "--provider", default="google_news_rss", help="Provider ID")
    parser.add_argument("--list-providers", action="store_true", help="List providers")

    args = parser.parse_args()

    if args.list_providers:
        for p in list_providers():
            print(f"  {p['id']}: {p['description']}")
        return

    if not args.query:
        parser.error("-q/--query is required")

    provider = get_provider(args.provider)
    if not provider:
        print(f"Error: Unknown provider '{args.provider}'", file=sys.stderr)
        sys.exit(1)

    result = provider.search(args.query, limit=args.limit)

    output = [
        {"title": r.title, "link": r.link, "published": r.published, "source": r.source}
        for r in result.results
    ]
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
