# 検索機能のドキュメント

## 概要

Gemini File Search API の検索機能を実装しました。この機能を使用すると、アップロードしたドキュメントに対して自然言語で質問し、AIが関連情報を検索して回答を生成します。

## 技術仕様

### アーキテクチャ

検索機能は以下の技術スタックを使用しています：

1. **Gemini generateContent API**: Google の生成AIモデル
2. **FileSearch ツール**: File Search Store からの情報検索
3. **Grounding Metadata**: 回答の根拠となるドキュメントの引用情報

### API エンドポイント

```
POST /api/search
```

**リクエスト:**
```json
{
  "query": "What are the key features?",
  "storeIds": ["store_id_1", "store_id_2"],
  "model": "gemini-2.0-flash-exp",
  "metadataFilter": "optional filter"
}
```

**レスポンス:**
```json
{
  "answer": "AI-generated answer based on your documents",
  "groundingChunks": [...],
  "sources": ["source1", "source2"]
}
```

## 使用方法

### Web UI から

1. **Searchタブ**を開く
2. 検索したい**ストア**を選択（複数選択可）
3. **質問**を入力
4. 使用する**モデル**を選択（デフォルト: Gemini 2.0 Flash）
5. **Search**ボタンをクリック

### cURL から

```bash
# ストアIDを取得
STORE_ID="your_store_id"

# 検索実行
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is File Search?",
    "storeIds": ["'$STORE_ID'"],
    "model": "gemini-2.0-flash-exp"
  }' | jq .
```

### Python から

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/search",
    json={
        "query": "What are the key features?",
        "storeIds": ["store_id_here"],
        "model": "gemini-2.0-flash-exp"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

## サポートされているモデル

- **gemini-2.0-flash-exp** (推奨): 最新の高速モデル
- **gemini-1.5-pro**: 高精度モデル
- **gemini-1.5-flash**: バランス型モデル

## 機能

### 1. 複数ストア検索

複数のFile Search Storeを同時に検索できます。

```javascript
{
  "storeIds": ["store1", "store2", "store3"]
}
```

### 2. メタデータフィルタリング

特定のメタデータでフィルタリングできます。

```javascript
{
  "query": "...",
  "metadataFilter": "category=product AND version=2.0"
}
```

### 3. 引用情報（Grounding）

回答の根拠となるドキュメントの情報が自動的に取得されます。

## テスト

### 自動テストスクリプト

```bash
./test_search.sh
```

このスクリプトは以下を実行します：
1. テストストアを作成
2. サンプルドキュメントをアップロード
3. 検索クエリを実行
4. 結果を表示
5. クリーンアップ

### 手動テスト

```bash
# 1. ストアとドキュメントを準備
# (Web UIまたはアップロードスクリプトを使用)

# 2. 検索実行
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the pricing tiers",
    "storeIds": ["your_store_id"]
  }' | jq .
```

## ベストプラクティス

### 効果的な質問の仕方

✅ **良い例:**
- "What are the key features of File Search?"
- "How much does the Pro tier cost?"
- "Explain how chunking works"
- "What file types are supported?"

❌ **悪い例:**
- "Tell me everything" (範囲が広すぎる)
- "Yes or no" (コンテキストが不明)
- "Page 5" (ページ番号では検索できない)

### ストアの整理

- 関連するドキュメントを同じストアにまとめる
- トピックごとにストアを分ける
- メタデータを活用して分類する

### パフォーマンス

- 小さなストア（< 1GB）の方が高速
- 具体的な質問の方が精度が高い
- 必要なストアのみを選択する

## トラブルシューティング

### エラー: "No answer found"

**原因:**
- ドキュメントが処理中（STATE_PENDING）
- 質問が曖昧すぎる
- 関連するドキュメントが存在しない

**解決方法:**
1. ドキュメントが`STATE_ACTIVE`になるまで待つ
2. より具体的な質問にする
3. 正しいストアを選択しているか確認

### エラー: "Search failed: 401"

**原因:** APIキーが無効

**解決方法:**
```bash
# .envファイルを確認
cat .env | grep GOOGLE_API_KEY

# 正しいAPIキーを設定
echo "GOOGLE_API_KEY=your_actual_key" >> .env
```

### エラー: "Model not found"

**原因:** 指定したモデルが利用不可

**解決方法:**
利用可能なモデルに変更：
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### 回答の精度が低い

**対策:**
1. ドキュメントの品質を向上させる
   - 明確な見出しを使用
   - 適切にフォーマット
   - 重複を避ける

2. より具体的な質問をする
   - "What is X?" → "Explain how X works with Y"

3. メタデータフィルタを使用
   - 特定のカテゴリやバージョンに絞る

## 制限事項

1. **レスポンスタイム**: 検索には2-10秒かかる場合があります
2. **ドキュメント数**: 大量のドキュメントがある場合、レスポンスが遅くなります
3. **コンテキスト長**: 非常に長いドキュメントは分割されます
4. **言語**: 英語と日本語で最良の結果が得られます

## API料金

- **検索クエリ**: Gemini APIの料金が適用されます
- **ストレージ**: File Search Storeの料金が適用されます
- **埋め込み**: インデックス作成時に$0.15/百万トークン

詳細は [公式価格ページ](https://ai.google.dev/pricing) を参照してください。

## サンプルクエリ

以下は、サンプルドキュメント（samples/）に対するクエリ例です：

```bash
# 機能について
"What are the key features of File Search?"

# 価格について
"How much does the Pro tier cost?"

# 技術的な質問
"What is the default chunk size?"

# ファイル形式について
"What file types are supported?"

# 制限について
"What is the maximum file size?"
```

## 参考資料

- [Gemini API File Search ガイド](https://ai.google.dev/gemini-api/docs/file-search?hl=ja)
- [generateContent API](https://ai.google.dev/api/generate-content)
- [FileSearch Tool](https://ai.google.dev/api/caching#Tool)

---

最終更新: 2025-11-23
