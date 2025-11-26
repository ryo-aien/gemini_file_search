#!/bin/bash
# Demo script to showcase the API functionality

set -e

API_BASE="${API_BASE:-http://localhost:8000/api}"

echo "======================================"
echo "Gemini File Search API Demo"
echo "======================================"
echo ""

# Check if API is running
echo "1. Checking API health..."
curl -sf "$API_BASE/../health" > /dev/null || {
    echo "Error: API is not running. Start it with: make docker-up"
    exit 1
}
echo "✓ API is healthy"
echo ""

# Create a store
echo "2. Creating a new File Search Store..."
STORE_RESPONSE=$(curl -s -X POST "$API_BASE/stores" \
    -H "Content-Type: application/json" \
    -d '{"displayName": "Demo Store"}')
echo "$STORE_RESPONSE" | jq .
STORE_NAME=$(echo "$STORE_RESPONSE" | jq -r .name)
STORE_ID=$(echo "$STORE_NAME" | awk -F'/' '{print $NF}')
echo "✓ Created store: $STORE_NAME"
echo ""

# Upload a sample file
echo "3. Uploading sample document..."
UPLOAD_RESPONSE=$(curl -s -X POST "$API_BASE/stores/$STORE_ID/upload" \
    -F "file=@samples/sample1.txt" \
    -F "display_name=Sample Document" \
    -F "max_tokens_per_chunk=200" \
    -F "max_overlap_tokens=20")
echo "$UPLOAD_RESPONSE" | jq .
OPERATION_NAME=$(echo "$UPLOAD_RESPONSE" | jq -r .name)
echo "✓ Upload operation started: $OPERATION_NAME"
echo ""

# Wait a bit for processing
echo "4. Waiting for document processing (5 seconds)..."
sleep 5
echo ""

# List documents
echo "5. Listing documents in the store..."
DOCS_RESPONSE=$(curl -s "$API_BASE/stores/$STORE_ID/documents")
echo "$DOCS_RESPONSE" | jq .
echo ""

# Get store details
echo "6. Getting store details..."
curl -s "$API_BASE/stores/$STORE_ID" | jq .
echo ""

# Cleanup
echo "7. Cleaning up (deleting store and documents)..."
curl -s -X DELETE "$API_BASE/stores/$STORE_ID?force=true"
echo "✓ Store deleted"
echo ""

echo "======================================"
echo "Demo completed successfully!"
echo "======================================"
