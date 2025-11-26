#!/bin/bash
# 検索機能をテストするスクリプト

set -e

API_BASE="${API_BASE:-http://localhost:8000/api}"

echo "======================================"
echo "Search Functionality Test"
echo "======================================"
echo ""

# 1. ストアを作成してファイルをアップロード
echo "1. Creating test store and uploading documents..."
STORE_RESPONSE=$(curl -s -X POST "${API_BASE}/stores" \
    -H "Content-Type: application/json" \
    -d '{"displayName": "Search Test Store"}')

STORE_NAME=$(echo "$STORE_RESPONSE" | jq -r '.name')
STORE_ID=$(echo "$STORE_NAME" | awk -F'/' '{print $NF}')
echo "✓ Created store: $STORE_ID"

# サンプルファイルをアップロード
echo ""
echo "2. Uploading sample documents..."
for file in samples/sample*.{txt,md,json}; do
    if [ -f "$file" ]; then
        echo "Uploading: $file"
        curl -s -X POST "${API_BASE}/stores/${STORE_ID}/upload" \
            -F "file=@${file}" \
            -F "display_name=$(basename $file)" > /dev/null
    fi
done

# ドキュメント処理を待機
echo ""
echo "3. Waiting 10 seconds for document processing..."
sleep 10

# ドキュメント数を確認
DOCS_RESPONSE=$(curl -s "${API_BASE}/stores/${STORE_ID}/documents")
DOC_COUNT=$(echo "$DOCS_RESPONSE" | jq -r '.documents | length')
echo "✓ Documents processed: $DOC_COUNT"

# 検索実行
echo ""
echo "4. Testing search functionality..."
echo ""

# テストクエリ1
echo "Query 1: What are the key features of File Search?"
SEARCH_RESPONSE=$(curl -s -X POST "${API_BASE}/search" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"What are the key features of File Search?\",
        \"storeIds\": [\"$STORE_ID\"],
        \"model\": \"gemini-2.0-flash-exp\"
    }")

echo "Answer:"
echo "$SEARCH_RESPONSE" | jq -r '.answer' | head -5
echo "..."
echo ""

# テストクエリ2
echo "Query 2: How much does the Pro tier cost?"
SEARCH_RESPONSE2=$(curl -s -X POST "${API_BASE}/search" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"How much does the Pro tier cost?\",
        \"storeIds\": [\"$STORE_ID\"],
        \"model\": \"gemini-2.0-flash-exp\"
    }")

echo "Answer:"
echo "$SEARCH_RESPONSE2" | jq -r '.answer' | head -5
echo "..."
echo ""

# クリーンアップ
echo "5. Cleaning up..."
curl -s -X DELETE "${API_BASE}/stores/${STORE_ID}?force=true" > /dev/null
echo "✓ Test store deleted"
echo ""

echo "======================================"
echo "Search test completed!"
echo "======================================"
