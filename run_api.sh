#!/bin/bash

# Activate conda scraper_env environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate scraper_env

# Kill any existing uvicorn processes to avoid port conflicts
pkill -f uvicorn

echo "Starting Search API on port 8001..."
python -m uvicorn app.api.search_api:app --host 0.0.0.0 --port 8001 > logs/search.log 2>&1 &

echo "Service started!"
echo "Search API: http://localhost:8001/docs"
echo "Logs are being written to logs/search.log"
echo "Press Ctrl+C to stop the service."

# Wait for user to press Ctrl+C
trap "kill 0" EXIT
wait
