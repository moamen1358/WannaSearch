# Website Scraper & API (Enhanced Anti-Ban Edition)

Production-ready article scraper and FastAPI service designed to extract clean content from dynamic websites while avoiding bot detection. Features **full anti-detection suite**, **fingerprint randomization**, **human behavior simulation**, **smart proxy management**, and **comprehensive error logging**.

## What's New (Latest Update)

### Anti-Detection Suite
- **Human Behavior Simulation**: Random mouse movements, scrolling like reading, human-like delays (bell curve distribution)
- **Browser Fingerprint Randomization**: Random viewport sizes, timezone/locale matching, canvas noise injection, WebGL spoofing
- **Smart Proxy Manager**: Health tracking, automatic cooldown for failed proxies, minimum intervals between reuse
- **Rate Limiting**: Configurable delays between requests to avoid triggering rate limits
- **Enhanced Cloudflare Handling**: Extended 45-second timeout, better challenge detection

### Debugging & Monitoring
- **Screenshot on Failure**: Automatically captures screenshots when scraping fails (bans, blocks, extraction failures)
- **Detailed Error Logging**: Comprehensive logs with error classification, proxy info, user-agent, and recommendations
- **Error Classification**: Automatic detection of rate limits, bans, bot detection, Cloudflare challenges, paywalls

### Performance
- **Resource Blocking**: Blocks images, media, and fonts to save bandwidth (ideal for proxy usage)

## Key Features

### Anti-Ban Protection
| Feature | Description |
|---------|-------------|
| Proxy Rotation | Smart proxy manager with health tracking and cooldown |
| User-Agent Rotation | Pool of modern user agents (Chrome, Firefox, Safari) |
| Stealth Mode | `playwright-stealth` to mask automation signals |
| Human Behavior | Mouse movements, scrolling, bell-curve delays |
| Fingerprint Noise | Canvas/WebGL randomization, viewport/timezone rotation |
| Rate Limiting | Configurable minimum delay between requests |

### Smart Error Handling
| Feature | Description |
|---------|-------------|
| Screenshot Capture | Saves PNG + JSON metadata on failures |
| Error Classification | Identifies ban type (rate limit, block, CAPTCHA, Cloudflare) |
| Proxy Health | Marks failed proxies, applies cooldown, auto-recovery |
| Detailed Logging | Full context: URL, proxy, user-agent, page title, recommendations |

## Project Structure

```
website_scraper/
├── app/
│   ├── services/
│   │   ├── scraper.py        # Core scraper with anti-detection suite
│   │   └── news_search.py    # News search with multiple providers
│   ├── providers/            # News provider implementations
│   │   ├── base.py           # Base provider interface
│   │   ├── google_news_rss.py
│   │   ├── bing_news_rss.py
│   │   └── newsapi.py
│   └── api/
│       ├── scraper_api.py    # FastAPI endpoint for scraping
│       └── search_api.py     # FastAPI endpoint for news search
├── config/
│   ├── config.json           # Your configuration (gitignored)
│   ├── config.json.example   # Example configuration
│   └── proxies.txt           # Your proxy list (gitignored)
├── main.py                   # CLI entry point
├── logs/                     # Log files (gitignored)
├── screenshots/              # Failure screenshots (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run_api.sh
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

2. **Configure**:
   ```bash
   cp config/config.json.example config/config.json
   # Edit config/config.json with your settings
   # Add proxies to config/proxies.txt (format: IP:PORT:USER:PASS)
   ```

## Configuration (`config/config.json`)

```json
{
    "proxies": {
        "enabled": true,
        "proxy_file": "proxies.txt"
    },
    "browser": {
        "headless": true,
        "slow_mo": 200,
        "timeout": 60000
    },
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    ],
    "anti_detection": {
        "min_request_interval": 5,
        "simulate_human_behavior": true,
        "randomize_viewport": true,
        "randomize_timezone": true,
        "inject_fingerprint_noise": true
    },
    "proxy_manager": {
        "min_proxy_interval": 30,
        "max_failures_before_cooldown": 3,
        "cooldown_seconds": 120
    }
}
```

## Running the API

### Local Development
```bash
# Start both APIs
./run_api.sh

# Or run individually
uvicorn app.api.scraper_api:app --host 0.0.0.0 --port 8000
uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001
```

### Docker
```bash
docker-compose up -d
```

### Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Scraper API | `http://localhost:8000` | Article extraction |
| Search API | `http://localhost:8001` | Google News search |

## CLI Usage

The CLI provides a simple way to search news from multiple providers directly from the terminal.

### List Available Providers
```bash
python main.py --list-providers
```

Output:
```
  google_news_rss: Search news via Google News RSS feeds
  bing_news_rss: Search news via Bing News RSS feeds
  newsapi: Search news via NewsAPI.org (100 req/day free)
```

### Search News

```bash
# Basic search (uses default provider: google_news_rss)
python main.py -q "Tesla"

# Specify provider and limit results
python main.py -q "Apple" -p newsapi -l 5

# Search with Bing News
python main.py -q "Microsoft" -p bing_news_rss -l 3
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-q, --query` | Search query (required) |
| `-p, --provider` | News provider: `google_news_rss`, `bing_news_rss`, `newsapi` |
| `-l, --limit` | Maximum number of results (default: 10) |
| `--list-providers` | List all available providers |

### News Providers

| Provider | Description | API Key Required |
|----------|-------------|------------------|
| `google_news_rss` | Google News RSS feeds | No |
| `bing_news_rss` | Bing News RSS feeds | No |
| `newsapi` | NewsAPI.org (100 req/day free tier) | Yes |

### NewsAPI Configuration

To use the NewsAPI provider, add your API key to `config/config.json`:

```json
{
    "newsapi": {
        "api_key": "your_api_key_here"
    }
}
```

Get a free API key at: https://newsapi.org/register

### Example Output

```json
[
  {
    "title": "Tesla Announces New Model",
    "link": "https://example.com/article",
    "published": "2026-01-18T10:30:00Z",
    "source": "TechNews"
  }
]
```

## API Usage

### Scrape a URL
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

**Response**:
```json
[{
    "title": "Article Title",
    "date": "2024-01-15",
    "source": "example.com",
    "text": "Full article content..."
}]
```

### Search Google News
```bash
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "limit": 5}'
```

## Debugging Failed Scrapes

When scraping fails, check:

1. **Screenshots**: `screenshots/YYYY-MM-DD/` contains PNG + JSON metadata
2. **Logs**: `logs/scraper.log` has detailed error blocks:
   ```
   === BAN/BLOCK DETECTED ===
   URL: https://example.com
   Proxy: http://1.2.3.4:8080 (user: abc***)
   Error Type: access_denied
   Details: Access denied - IP or proxy may be blocked
   ===========================
   ```

3. **Error Types**:
   - `rate_limit`: Too many requests, increase delays
   - `access_denied`: IP/proxy blocked, rotate proxy
   - `bot_detection`: CAPTCHA triggered, slow down
   - `cloudflare_challenge`: Wait longer or use different proxy
   - `paywall`: Content requires subscription

## Anti-Detection Features Explained

### Human Behavior Simulation
- **Mouse Movement**: 3-6 random cursor movements before extraction
- **Scrolling**: Scrolls down in chunks (150-400px) like reading
- **Delays**: Normal distribution (bell curve) instead of uniform random

### Fingerprint Randomization
- **Viewport**: Randomly selects from 7 common screen sizes
- **Location**: Matches timezone, locale, and geolocation (5 profiles)
- **Canvas**: Injects imperceptible noise to change fingerprint
- **WebGL**: Spoofs GPU renderer string (NVIDIA/Intel/AMD variations)

### Smart Proxy Management
- **Health Tracking**: Counts failures per proxy
- **Cooldown**: Failed proxies get 2-3 minute cooldown
- **Rotation Interval**: Minimum 30 seconds between using same proxy
- **Auto-Recovery**: Resets counters when all proxies exhausted

## Testing Bot Detection

Test your setup against these sites:
- https://bot.sannysoft.com/ - Automation detection
- https://browserleaks.com/canvas - Canvas fingerprint
- https://browserleaks.com/webgl - WebGL fingerprint
- https://www.browserscan.net/ - Comprehensive bot check

## Limitations

- **Hard Paywalls**: Cannot bypass subscription-only content (WSJ, FT, etc.)
- **Advanced CAPTCHAs**: hCaptcha/reCAPTCHA v3 may still block
- **Rate Limits**: Keep requests reasonable (<30/hour per domain)

## License

MIT
# WannaSearch
