# 手動テストコマンド

アップロード機能を手動でテストするためのcurlコマンド集です。

## 前提条件

```bash
# APIが起動していることを確認
curl http://localhost:8000/health

# 環境変数を設定（必要に応じて）
export API_BASE="http://localhost:8000/api"
```

## ステップ1: ストアを作成

```bash
# ストアを作成
curl -X POST http://localhost:8000/api/stores \
  -H "Content-Type: application/json" \
  -d '{"displayName": "Manual Test Store"}' \
  | jq .

# レスポンスから "name" フィールドをコピーして、STORE_ID を抽出
# 例: "fileSearchStores/abc123" から "abc123" を取得
export STORE_ID="abc123"  # ← 実際のIDに置き換える
```

## ステップ2: ファイルをアップロード

### 基本的なアップロード

```bash
curl -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample1.txt" \
  -F "display_name=Test Document" \
  -v

# または詳細なレスポンスを見る
curl -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample1.txt" \
  -F "display_name=Test Document" \
  -w "\nHTTP Status: %{http_code}\n" \
  | jq .
```

### 異なるファイルタイプでテスト

```bash
# Markdownファイル
curl -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample2.md" \
  -F "display_name=Markdown Document"

# JSONファイル
curl -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample3.json" \
  -F "display_name=JSON Document"
```

## ステップ3: ドキュメントを確認

```bash
# ドキュメント一覧を取得
curl http://localhost:8000/api/stores/${STORE_ID}/documents | jq .

# 特定のドキュメントを取得（DOC_IDを置き換える）
export DOC_ID="xyz789"  # ← 実際のIDに置き換える
curl http://localhost:8000/api/stores/${STORE_ID}/documents/${DOC_ID} | jq .
```

## ステップ4: オペレーション状態を確認

```bash
# アップロードレスポンスから "name" を取得した場合
export OPERATION_NAME="operations/abc123xyz"  # ← 実際の名前に置き換える

curl http://localhost:8000/api/operations/${OPERATION_NAME} | jq .
```

## ステップ5: クリーンアップ

```bash
# ドキュメントを削除
curl -X DELETE http://localhost:8000/api/stores/${STORE_ID}/documents/${DOC_ID}?force=true

# ストアを削除（全ドキュメント含む）
curl -X DELETE http://localhost:8000/api/stores/${STORE_ID}?force=true
```

## デバッグコマンド

### 詳細なエラー情報を表示

```bash
# -v オプションで詳細なHTTPヘッダーを表示
curl -v -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample1.txt" \
  -F "display_name=Test Document"
```

### レスポンスヘッダーのみ確認

```bash
curl -I http://localhost:8000/api/stores
```

### タイムアウトを延長

```bash
# 60秒のタイムアウト
curl --max-time 60 -X POST http://localhost:8000/api/stores/${STORE_ID}/upload \
  -F "file=@samples/sample1.txt"
```

## トラブルシューティング

### エラー: "Cannot find field"

これは通常、リクエストボディのフィールド名が間違っている場合に発生します。

```bash
# サーバーログを確認
docker compose logs -f app

# または
tail -f /var/log/app.log
```

### エラー: "API Key not configured"

```bash
# .env ファイルを確認
cat .env | grep GOOGLE_API_KEY

# 環境変数が読み込まれているか確認
docker compose config | grep GOOGLE_API_KEY
```

### エラー: "Connection refused"

```bash
# アプリが起動しているか確認
curl http://localhost:8000/health

# ポートが正しいか確認
netstat -an | grep 8000
```

## 自動テストスクリプト

すべてのステップを自動実行：

```bash
./test_upload.sh
```

環境変数でカスタマイズ：

```bash
# 異なるAPIベースURL
API_BASE=http://localhost:8001/api ./test_upload.sh

# 異なるテストファイル
TEST_FILE=path/to/myfile.txt ./test_upload.sh
```

## 期待される結果

### 成功時のレスポンス（ステップ2）

```json
{
  "name": "operations/abc123xyz",
  "done": false,
  "metadata": {
    "@type": "type.googleapis.com/google.api.OperationMetadata",
    "progressPercent": 0
  }
}
```

HTTPステータス: `202 Accepted`

### 失敗時のレスポンス

```json
{
  "detail": "Upload error: 400 - {...}"
}
```

HTTPステータス: `500 Internal Server Error`

---

エラーが発生した場合は、レスポンスの全文とサーバーログを確認してください。
