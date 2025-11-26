# アップロード機能の修正

## 問題

ファイルアップロード時に以下のエラーが発生していました：

```
Upload error: 400 - Invalid JSON payload received. Unknown name "metadata": Cannot bind query parameter.
```

## 原因

Google Gemini API のファイルアップロードは、単純な1段階のアップロードではなく、以下の2段階のプロセスが必要でした：

1. **Files API** にファイルをアップロード（resumable upload protocol使用）
2. アップロードしたファイルを **File Search Store** にインポート

## 修正内容

### 1. Files API へのアップロード実装

Resumable Upload Protocol を使用した正しいアップロード実装：

```python
# Step 1: Start resumable upload (メタデータ送信)
POST https://generativelanguage.googleapis.com/upload/v1beta/files
Headers:
  - X-Goog-Api-Key: {api_key}
  - X-Goog-Upload-Protocol: resumable
  - X-Goog-Upload-Command: start
  - X-Goog-Upload-Header-Content-Length: {file_size}
  - X-Goog-Upload-Header-Content-Type: {mime_type}
  - Content-Type: application/json
Body: {"file": {"displayName": "..."}}

Response Headers:
  - X-Goog-Upload-URL: {upload_uri}

# Step 2: Upload file content
POST {upload_uri}
Headers:
  - X-Goog-Upload-Command: upload, finalize
  - X-Goog-Upload-Offset: 0
  - Content-Length: {file_size}
Body: {file_binary_content}
```

### 2. 2段階アップロードフロー

`upload_to_file_search_store` メソッドを以下のように変更：

1. `upload_file_to_files_api()` - Files API にファイルをアップロード
2. `import_file()` - File Search Store にインポート

## 使用方法

変更はバックエンドのみで、UIからの使い方は変わりません：

```javascript
// Web UI から（変更なし）
const formData = new FormData();
formData.append('file', file);
formData.append('display_name', 'Sample Document');

fetch(`/api/stores/${storeId}/upload`, {
  method: 'POST',
  body: formData
});
```

```bash
# cURL から（変更なし）
curl -X POST http://localhost:8000/api/stores/{store_id}/upload \
  -F "file=@sample.txt" \
  -F "display_name=Test Document"
```

## テスト方法

1. **Dockerを再起動**（推奨）:
   ```bash
   docker compose down
   docker compose up --build
   ```

2. **または ローカル環境を再起動**:
   ```bash
   # アプリを停止（Ctrl+C）
   # 再起動
   uvicorn app.main:app --reload
   ```

3. **Web UI でテスト**:
   - http://localhost:8000 にアクセス
   - Stores タブでストアを作成
   - Upload タブでファイルを選択
   - Upload File ボタンをクリック
   - エラーなく成功すればOK

## 技術的詳細

### Resumable Upload Protocol

Google APIs で使用される標準的なアップロードプロトコル：

- **利点**: 大きなファイルの中断/再開が可能
- **セキュリティ**: 署名付きURLで安全にアップロード
- **効率**: チャンク分割アップロード対応（将来の拡張に備えて）

### 実装の変更点

**修正前（エラーが発生）:**
```python
# メタデータをクエリパラメータとして送信（サポートされていない）
params = {"metadata": json.dumps(metadata)}
response = await client.post(url, files=files, params=params)
```

**修正後（正しい方法）:**
```python
# 1. Files API にアップロード（resumable protocol）
file_resource = await upload_file_to_files_api(file_path)

# 2. File Search Store にインポート
operation = await import_file(store_name, file_resource["file"]["name"])
```

## 参考資料

- [Files API Documentation](https://ai.google.dev/api/files)
- [File Search Guide](https://ai.google.dev/gemini-api/docs/file-search?hl=ja)
- [Resumable Upload Protocol](https://cloud.google.com/storage/docs/resumable-uploads)

## トラブルシューティング

### エラー: "No upload URL returned"

**原因**: Start リクエストが失敗している

**解決方法**:
- API キーが正しいか確認
- ログを確認: `docker compose logs -f`

### エラー: "File upload error: 401"

**原因**: API キーが無効または期限切れ

**解決方法**:
- `.env` ファイルで API キーを確認
- [Google AI Studio](https://ai.google.dev/) で新しいキーを生成

### エラー: "Import failed"

**原因**: Files API へのアップロードは成功したが、インポートが失敗

**解決方法**:
- ストアが存在するか確認
- ファイル形式が対応しているか確認（.txt, .pdf, .md, etc.）
- ログでエラー詳細を確認

## 今後の改善案

1. **進捗表示**: Resumable upload の進捗をリアルタイムで表示
2. **チャンク分割**: 大きなファイル（100MB以上）の分割アップロード
3. **並列アップロード**: 複数ファイルの同時アップロード
4. **リトライ**: ネットワークエラー時の自動リトライ強化

---

修正日: 2025-11-23
