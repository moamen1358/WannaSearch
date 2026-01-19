# WannaSearch

A news search tool that searches Google News RSS feeds with CLI and API interfaces. Features company-focused search, time range filtering, and automatic log saving with Cairo timezone timestamps.

## Features

- **Google News RSS Search**: Search news via Google News RSS feeds (no API key required)
- **Company-Focused Search**: Combine company name with search queries
- **Time Range Filtering**: Filter results by days (e.g., last 30, 90, 365 days)
- **Automatic Logging**: Saves search results to `logs/{company}_{timestamp}.log` (Cairo timezone)
- **REST API**: FastAPI service for programmatic access
- **Docker Support**: Easy deployment with Docker and docker-compose

## Project Structure

```
WannaSearch/
├── app/
│   ├── services/
│   │   └── news_search.py    # News search service
│   ├── providers/
│   │   ├── base.py           # Base provider interface
│   │   └── google_news.py    # Google News RSS provider
│   └── api/
│       └── search_api.py     # FastAPI endpoint
├── main.py                   # CLI entry point
├── logs/                     # Search logs (gitignored)
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
python main.py -c "Tactful" -q "AI customer service" -t 365 -l 10
python main.py -q "cybersecurity news" -t 30 -l 10
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-c, --company` | Company name to search for |
| `-q, --query` | Search query/keywords |
| `-t, --time` | Time range in days (e.g., 365 for last year) |
| `-l, --limit` | Max results (default: 10) |

**Note:** At least one of `-c` (company) or `-q` (query) must be provided.

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
    "query": "data breach",
    "time_days": 365,
    "limit": 10
  }'
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | No | Company name to search |
| `query` | string | No | Search keywords |
| `time_days` | int | No | Time range in days (1-3650) |
| `limit` | int | No | Max results (1-100, default: 10) |

**Note:** At least one of `company_name` or `query` must be provided.

### Response Format

```json
[
  {
    "title": "Article Title",
    "link": "https://example.com/article",
    "published": "2026-01-18T10:30:00Z",
    "source": "Source Name"
  }
]
```

## Running the API Locally

```bash
# Start the API server
uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001

# Or with auto-reload for development
uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001 --reload
```

## Verification

Test your setup:

```bash
# Test CLI
python main.py -c "Test" -q "news" -t 30 -l 3

# Test API (if running)
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Test", "query": "news", "time_days": 30, "limit": 3}'
```

## License

MIT
