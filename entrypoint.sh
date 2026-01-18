#!/bin/bash

echo "Starting Search API on port 8001..."
uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001 2>&1 | tee -a /app/logs/search.log
