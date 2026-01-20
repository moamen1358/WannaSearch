# WannaSearch API Documentation

## Overview

WannaSearch is a news search API that aggregates results from Google News RSS feeds. It provides a fast, cached, and rate-limited interface for searching news articles.

**Base URL:** `http://localhost:8001`

**Version:** 3.0.0

---

## Authentication

Currently, the API does not require authentication. Rate limiting is applied per IP address.

---

## Endpoints

### Health Check

Check the API health status and available providers.

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "providers": ["google_news_rss"],
  "cache_size": 42
}
```

---

### List Providers

Get a list of available search providers.

```
GET /providers
```

**Response:**
```json
{
  "providers": [
    {
      "id": "google_news_rss",
      "name": "Google News RSS",
      "description": "Search news via Google News RSS feeds"
    }
  ]
}
```

---

### Search News

Search for news articles.

```
POST /search
```

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | No* | `""` | Search keywords (max 500 chars) |
| `company_name` | string | No* | `null` | Company name to search for (max 200 chars) |
| `country` | string | No | `null` | Country/location filter (max 100 chars) |
| `time_days` | integer | No | `null` | Filter results to last N days (1-3650) |
| `provider` | string | No | `"google_news_rss"` | Search provider ID |
| `limit` | integer | No | `10` | Maximum results to return (1-100) |

*\* At least one of `query` or `company_name` must be provided.*

**Example Request:**
```json
{
  "query": "artificial intelligence",
  "company_name": "OpenAI",
  "country": "USA",
  "time_days": 30,
  "limit": 20
}
```

**Response:**
```json
{
  "query": "OpenAI AND (artificial intelligence) location:USA after:2025-12-21",
  "company_name": "OpenAI",
  "provider": "google_news_rss",
  "results": [
    {
      "title": "OpenAI Announces New AI Model",
      "link": "https://example.com/article",
      "published": "Mon, 20 Jan 2026 10:00:00 GMT",
      "source": "Tech News"
    }
  ],
  "total": 1,
  "duration": 0.523,
  "cached": false
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The actual query sent to the provider |
| `company_name` | string | The company name from the request |
| `provider` | string | The provider used for the search |
| `results` | array | List of search results |
| `total` | integer | Total number of results |
| `duration` | float | Search duration in seconds |
| `cached` | boolean | Whether results were served from cache |

**Result Object:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Article title |
| `link` | string | URL to the article |
| `published` | string | Publication date |
| `source` | string | News source name |

---

### Clear Cache

Clear the search results cache.

```
DELETE /cache
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Error Responses

### 400 Bad Request

Returned when the request is invalid.

```json
{
  "detail": "Either 'query' or 'company_name' must be provided"
}
```

```json
{
  "detail": "Unknown provider: invalid_provider"
}
```

### 422 Validation Error

Returned when request validation fails.

```json
{
  "detail": [
    {
      "loc": ["body", "limit"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 429 Too Many Requests

Returned when rate limit is exceeded.

```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error

Returned when an unexpected error occurs.

```json
{
  "detail": "Error message"
}
```

---

## Rate Limiting

- **Limit:** 100 requests per 60 seconds per IP address
- Rate limit resets automatically after the time window

---

## Caching

- **TTL:** 300 seconds (5 minutes)
- **Max Size:** 1000 cached responses
- Cache key: `{provider}:{query}:{company_name}:{country}:{time_days}:{limit}`

Cached responses are indicated by `"cached": true` in the response.

---

## Search Logging

Every search is logged to a file in the `logs/` directory with the format:
```
{company_name}_{YYYY-MM-DD_HH-MM-SS}.log
```

Log files contain:
- Search timestamp (Cairo timezone)
- Company name
- Full query
- Request URL
- All results with metadata

---

## Query Building

The API builds search queries using the following format:

```
{company_name} AND ({query}) location:{country} after:{date}
```

**Examples:**

| Input | Generated Query |
|-------|-----------------|
| `company_name="Microsoft"` | `Microsoft` |
| `query="data breach"` | `data breach` |
| `company_name="Microsoft", query="security"` | `Microsoft AND (security)` |
| `query="news", country="USA"` | `news location:USA` |
| `query="news", time_days=30` | `news after:2025-12-21` |

---

## Usage Examples

### cURL

**Basic search:**
```bash
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "technology news"}'
```

**Company search with filters:**
```bash
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tesla",
    "country": "USA",
    "time_days": 7,
    "limit": 50
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8001/search",
    json={
        "query": "artificial intelligence",
        "company_name": "Google",
        "time_days": 30,
        "limit": 20
    }
)

data = response.json()
for result in data["results"]:
    print(f"{result['title']} - {result['source']}")
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8001/search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "climate change",
    time_days: 14,
    limit: 10
  })
});

const data = await response.json();
data.results.forEach(r => console.log(r.title));
```

---

## OpenAPI / Swagger

Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8001/docs`
- **ReDoc:** `http://localhost:8001/redoc`
- **OpenAPI JSON:** `http://localhost:8001/openapi.json`
