#!/bin/bash
# Test the models API endpoint

echo "======================================"
echo "Testing Models API"
echo "======================================"
echo ""

# Test health endpoint first
echo "1. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
echo "Health response: $HEALTH"
echo ""

# Test models endpoint
echo "2. Testing models endpoint..."
echo "URL: http://localhost:8000/api/models"
echo ""

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8000/api/models)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"
echo ""
echo "Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✓ Models API is working"

    # Count models
    MODEL_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)
    if [ ! -z "$MODEL_COUNT" ]; then
        echo "✓ Found $MODEL_COUNT models"
    fi
else
    echo "✗ Models API failed with status $HTTP_STATUS"
fi

echo ""
echo "======================================"
