#!/bin/bash
# Health check script for the application

set -e

HOST="${1:-localhost}"
PORT="${2:-8000}"
URL="http://${HOST}:${PORT}/health"

echo "Checking application health at: $URL"

response=$(curl -s -w "\n%{http_code}" "$URL")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP Status: $http_code"
echo "Response: $body"

if [ "$http_code" -eq 200 ]; then
    echo "✓ Application is healthy"
    exit 0
else
    echo "✗ Application is unhealthy"
    exit 1
fi
