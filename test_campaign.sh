#!/bin/bash

# Email Campaign Test Script
# ==========================
# This script runs the email campaign test

cd "$(dirname "$0")"

echo "========================================"
echo "🚀 Starting Email Campaign Test..."
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with SMTP configuration"
    exit 1
fi

# Run the test
python test_campaign_email.py "$@"
