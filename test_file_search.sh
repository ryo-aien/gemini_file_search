#!/bin/bash
# Test file search API directly

if [ -z "$1" ]; then
    echo "Usage: $0 <store_id>"
    echo "Example: $0 abc123"
    exit 1
fi

STORE_ID="$1"
API_KEY=$(grep "GOOGLE_API_KEY=" .env | cut -d'=' -f2)

if [ -z "$API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY not found in .env"
    exit 1
fi

echo "======================================"
echo "Testing Gemini File Search"
echo "======================================"
echo ""
echo "Store ID: fileSearchStores/$STORE_ID"
echo "Model: gemini-2.0-flash-exp"
echo ""

# Test with snake_case (current implementation)
echo "Test 1: Using snake_case (file_search, file_search_store_names)"
echo "--------------------------------------"

curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${API_KEY}" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
        "contents": [{
            "parts": [{"text": "What is this document about?"}]
        }],
        "tools": [{
            "file_search": {
                "file_search_store_names": ["fileSearchStores/'$STORE_ID'"]
            }
        }]
    }' | python3 -m json.tool 2>/dev/null || echo "Failed"

echo ""
echo ""

# Test with camelCase
echo "Test 2: Using camelCase (fileSearch, fileSearchStoreNames)"
echo "--------------------------------------"

curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${API_KEY}" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
        "contents": [{
            "parts": [{"text": "What is this document about?"}]
        }],
        "tools": [{
            "fileSearch": {
                "fileSearchStoreNames": ["fileSearchStores/'$STORE_ID'"]
            }
        }]
    }' | python3 -m json.tool 2>/dev/null || echo "Failed"

echo ""
echo "======================================"
