"""WannaSearch CLI."""

import argparse
import json
import logging
import sys

from app.providers import get_provider, list_providers, create_search_log

logger = logging.getLogger("cli")


def main():
    parser = argparse.ArgumentParser(description="WannaSearch - News Search CLI")
    parser.add_argument("-q", "--query", help="Search query")
    parser.add_argument("-c", "--company", help="Company name")
    parser.add_argument("-t", "--time", type=int, help="Time range in days (e.g., 30 for last 30 days)")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("-p", "--provider", default="google_news_rss", help="Provider ID")
    parser.add_argument("--list-providers", action="store_true", help="List providers")

    args = parser.parse_args()

    if args.list_providers:
        for p in list_providers():
            print(f"  {p['id']}: {p['description']}")
        return

    # Either query or company must be provided
    if not args.query and not args.company:
        parser.error("-q/--query or -c/--company is required")

    provider = get_provider(args.provider)
    if not provider:
        print(f"Error: Unknown provider '{args.provider}'", file=sys.stderr)
        sys.exit(1)

    # Use empty query if only company is provided
    query = args.query or ""

    logger.info(f"CLI search: company='{args.company}', query='{query}', time_days={args.time}, limit={args.limit}")
    result = provider.search(query, limit=args.limit, company_name=args.company, time_days=args.time)

    # Print the URL before results
    print(f"\nSearch URL: {result.url}\n")

    # Convert results to list of dicts
    output = [
        {"title": r.title, "link": r.link, "published": r.published, "source": r.source}
        for r in result.results
    ]

    # Create log file with Cairo timezone
    log_path = create_search_log(
        company_name=args.company,
        results=output,
        url=result.url,
        query=result.query
    )
    print(f"Log saved to: {log_path}\n")

    # Print results
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
