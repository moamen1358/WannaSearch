# WannaSearch

WannaSearch is a news search tool over Google News RSS, packaged as a
CLI and a FastAPI HTTP service. It supports company-focused queries,
time-range filtering, and writes per-company search logs in the Cairo
timezone for later review.

No API key is required — Google News RSS is the default provider, and
the provider system is pluggable for future sources.

## Features

- Google News RSS search (no API key required)
- Company-focused queries that combine a company name with search terms
- Time-range filtering by days (e.g., last 30, 90, 365)
- Automatic per-search log files at `logs/{company}_{timestamp}.log`
  (Cairo timezone)
- REST API via FastAPI with response caching
- Docker and docker-compose support

## Project structure

```
WannaSearch/
├── app/
│   ├── api/
│   │   └── search_api.py   # FastAPI endpoints
│   └── providers/
│       ├── base.py         # SearchProvider abstract interface
│       └── google_news.py  # Google News RSS implementation
├── main.py                 # CLI entry point
├── logs/                   # Per-search logs (gitignored)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Installation

```bash
pip install -r requirements.txt
```

## CLI Usage

Search news directly from the command line:

```bash
# Search with company name, query, and time range
python main.py -c "Company" -q "search terms" -t 365 -l 10

# Examples:
python main.py -c "Microsoft" -q "data breach" -t 90 -l 5
python main.py -c "Tactful" --country "Egypt" -q "AI customer service" -t 365 -l 10
python main.py -q "cybersecurity news" -t 30 -l 10
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-c, --company` | Company name to search for |
| `--country` | Company location/country |
| `-q, --query` | Search query/keywords |
| `-t, --time` | Time range in days (e.g., 365 for last year) |
| `-l, --limit` | Max results (default: 10) |
| `-p, --provider` | Provider ID (default: `google_news_rss`) |
| `--list-providers` | Print available providers and exit |
| `--serve` | Start the API server |
| `--port` | API server port (default: 8001) |

**Note:** At least one of `-c` (company) or `-q` (query) must be provided for search operations.

### Output

- **Console**: Prints search URL and JSON results
- **Log File**: Automatically saved to `logs/{company}_{timestamp}.log` (Cairo timezone)

Example output:
```json
[
  {
    "title": "Microsoft Reports Data Breach Affecting Users",
    "link": "https://example.com/article",
    "published": "2026-01-18T10:30:00Z",
    "source": "TechNews"
  }
]
```

## Docker Usage

### Using docker-compose (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t wannasearch .

# Run container
docker run -p 8001:8001 -v ./logs:/app/logs wannasearch
```

## API Usage

The API runs on port 8001 by default.

### Search Endpoint

```bash
# POST /search
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Microsoft",
    "country": "USA",
    "query": "data breach",
    "time_days": 365,
    "limit": 10
  }'
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | No | Company name to search |
| `country` | string | No | Company location/country |
| `query` | string | No | Search keywords |
| `time_days` | int | No | Time range in days (1-3650) |
| `limit` | int | No | Max results (1-100, default: 10) |

**Note:** At least one of `company_name` or `query` must be provided.

### Response Format

```json
{
  "query": "data breach",
  "company_name": "Microsoft",
  "provider": "google_news_rss",
  "results": [
    {
      "title": "Article Title",
      "link": "https://example.com/article",
      "published": "2026-01-18T10:30:00Z",
      "source": "Source Name"
    }
  ],
  "total": 1,
  "duration": 0.42,
  "cached": false
}
```

### Other endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/providers` | List available search providers |
| `POST` | `/search` | Run a search |
| `DELETE` | `/cache` | Clear the response cache |

## Running the API Locally

```bash
# Start the API server using CLI
python main.py --serve

# Start on a custom port
python main.py --serve --port 8001

# Or use uvicorn directly with auto-reload for development
uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001 --reload
```

## Verification

Test your setup:

```bash
# Test CLI search
python main.py -c "Test" -q "news" -t 30 -l 3

# Test serve mode
python main.py --serve
# Then in another terminal:
curl http://localhost:8001/health

# Test with custom port
python main.py --serve --port 8001

# Test API search (if server is running)
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Test", "query": "news", "time_days": 30, "limit": 3}'
```

## License

MIT
