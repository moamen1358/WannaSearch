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
    parser.add_argument("--country", help="Company location/country")
    parser.add_argument("-t", "--time", type=int, help="Time range in days (e.g., 30 for last 30 days)")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("-p", "--provider", default="google_news_rss", help="Provider ID")
    parser.add_argument("--list-providers", action="store_true", help="List providers")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=8001, help="API port (default: 8001)")

    args = parser.parse_args()

    # Validate limit range
    if args.limit < 1 or args.limit > 100:
        parser.error("--limit must be between 1 and 100")

    if args.serve:
        import uvicorn
        uvicorn.run("app.api.search_api:app", host="0.0.0.0", port=args.port)
        return

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

    logger.info(f"CLI search: company='{args.company}', country='{args.country}', query='{query}', time_days={args.time}, limit={args.limit}")
    result = provider.search(query, limit=args.limit, company_name=args.company, time_days=args.time, country=args.country)

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
