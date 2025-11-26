#!/bin/bash
# アップロード機能をテストするスクリプト

set -e

API_BASE="${API_BASE:-http://localhost:8000/api}"
TEST_FILE="${TEST_FILE:-samples/sample1.txt}"

echo "======================================"
echo "File Upload Test Script"
echo "======================================"
echo ""

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. ヘルスチェック
echo "1. Checking API health..."
HEALTH_RESPONSE=$(curl -s "${API_BASE}/../health")
echo "Response: $HEALTH_RESPONSE"
API_KEY_CONFIGURED=$(echo "$HEALTH_RESPONSE" | grep -o '"api_key_configured":[^,}]*' | cut -d':' -f2)

if [ "$API_KEY_CONFIGURED" = "true" ]; then
    echo -e "${GREEN}✓ API Key is configured${NC}"
else
    echo -e "${RED}✗ API Key is NOT configured${NC}"
    echo "Please set GOOGLE_API_KEY in .env file"
    exit 1
fi
echo ""

# 2. ストア作成
echo "2. Creating a test File Search Store..."
STORE_RESPONSE=$(curl -s -X POST "${API_BASE}/stores" \
    -H "Content-Type: application/json" \
    -d '{"displayName": "Test Upload Store"}')

echo "Store Response:"
echo "$STORE_RESPONSE" | jq . 2>/dev/null || echo "$STORE_RESPONSE"

# ストアIDを抽出
STORE_NAME=$(echo "$STORE_RESPONSE" | jq -r '.name // empty' 2>/dev/null)
if [ -z "$STORE_NAME" ]; then
    echo -e "${RED}✗ Failed to create store${NC}"
    echo "Response: $STORE_RESPONSE"
    exit 1
fi

STORE_ID=$(echo "$STORE_NAME" | awk -F'/' '{print $NF}')
echo -e "${GREEN}✓ Store created: $STORE_NAME (ID: $STORE_ID)${NC}"
echo ""

# 3. ファイルアップロード
echo "3. Uploading file: $TEST_FILE"
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}✗ Test file not found: $TEST_FILE${NC}"
    exit 1
fi

echo "Sending upload request..."
UPLOAD_RESPONSE=$(curl -s -X POST "${API_BASE}/stores/${STORE_ID}/upload" \
    -F "file=@${TEST_FILE}" \
    -F "display_name=Test Document" \
    -w "\nHTTP_STATUS:%{http_code}" 2>&1)

# HTTPステータスコードを抽出
HTTP_STATUS=$(echo "$UPLOAD_RESPONSE" | grep "HTTP_STATUS:" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$UPLOAD_RESPONSE" | grep -v "HTTP_STATUS:")

echo "HTTP Status: $HTTP_STATUS"
echo "Response Body:"
echo "$RESPONSE_BODY" | jq . 2>/dev/null || echo "$RESPONSE_BODY"

if [ "$HTTP_STATUS" = "202" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Upload initiated successfully${NC}"

    # オペレーション名を抽出
    OPERATION_NAME=$(echo "$RESPONSE_BODY" | jq -r '.name // empty' 2>/dev/null)
    if [ -n "$OPERATION_NAME" ]; then
        echo "Operation: $OPERATION_NAME"
    fi
else
    echo -e "${RED}✗ Upload failed with status $HTTP_STATUS${NC}"

    # エラー詳細を表示
    ERROR_MSG=$(echo "$RESPONSE_BODY" | jq -r '.detail // .error.message // "Unknown error"' 2>/dev/null)
    echo -e "${RED}Error: $ERROR_MSG${NC}"
fi
echo ""

# 4. ドキュメント一覧を確認（5秒待機後）
echo "4. Waiting 5 seconds for processing..."
sleep 5

echo "Checking documents in store..."
DOCS_RESPONSE=$(curl -s "${API_BASE}/stores/${STORE_ID}/documents")
echo "$DOCS_RESPONSE" | jq . 2>/dev/null || echo "$DOCS_RESPONSE"

DOC_COUNT=$(echo "$DOCS_RESPONSE" | jq -r '.documents | length' 2>/dev/null || echo "0")
echo "Documents found: $DOC_COUNT"
echo ""

# 5. クリーンアップ
echo "5. Cleaning up..."
curl -s -X DELETE "${API_BASE}/stores/${STORE_ID}?force=true" > /dev/null
echo -e "${GREEN}✓ Test store deleted${NC}"
echo ""

echo "======================================"
if [ "$HTTP_STATUS" = "202" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}Test completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}Test failed. See error details above.${NC}"
    exit 1
fi
