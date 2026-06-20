#!/bin/bash
# Production startup script for Wynreach Backend

# Exit on any error
set -e

echo "🚀 Starting Wynreach Backend (Production Mode)"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "📋 Copy .env.example to .env and fill in your production values"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$MAIN_DB_URL" ]; then
    echo "❌ ERROR: MAIN_DB_URL not set in .env"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY not set in .env"
    exit 1
fi

echo "✅ Environment variables validated"
echo "✅ Starting Uvicorn server..."

# Start Uvicorn with production settings
# Use gunicorn for production (install with: pip install gunicorn)
# gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 -k uvicorn.workers.UvicornWorker app.main:app

# Or use uvicorn directly with reload disabled
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --loop uvloop

echo "🛑 Server stopped"
