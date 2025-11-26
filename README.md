# Gemini File Search API - Full Implementation

完全機能実装版のGemini API Google File Search システムです。FastAPIバックエンド、シンプルなWeb UI、Docker対応、包括的なテストを含みます。

## 📋 概要

このプロジェクトは、Google の Gemini API File Search 機能の完全な実装です。以下の公式ドキュメントに準拠しています：

- [File Search ガイド](https://ai.google.dev/gemini-api/docs/file-search?hl=ja)
- [File Search Stores API](https://ai.google.dev/api/file-search/file-search-stores?hl=ja)
- [Documents API](https://ai.google.dev/api/file-search/documents?hl=ja)

## ✨ 主要機能

### API機能（全エンドポイント対応）

#### File Search Stores
- ✅ `POST /api/stores` - ストア作成
- ✅ `GET /api/stores` - ストア一覧（ページネーション対応）
- ✅ `GET /api/stores/{store_id}` - ストア取得
- ✅ `DELETE /api/stores/{store_id}` - ストア削除（force パラメータ対応）

#### Documents
- ✅ `GET /api/stores/{store_id}/documents` - ドキュメント一覧（ページネーション対応）
- ✅ `GET /api/stores/{store_id}/documents/{document_id}` - ドキュメント取得
- ✅ `DELETE /api/stores/{store_id}/documents/{document_id}` - ドキュメント削除

#### Media Upload
- ✅ `POST /api/stores/{store_id}/upload` - ファイルアップロード（`media.uploadToFileSearchStore`）
- ✅ `POST /api/stores/{store_id}/import` - 既存ファイルのインポート
- ✅ `GET /api/operations/{operation_name}` - 長時間実行オペレーションのステータス取得

### Web UI機能

- ストア管理（作成・一覧・削除）
- ファイルアップロード（ローカルファイル選択）
- ドキュメント管理（一覧・削除）
- チャンク設定（max_tokens_per_chunk, max_overlap_tokens）
- レスポンシブデザイン
- トースト通知
- リアルタイム状態表示

### 運用機能

- ✅ エラーハンドリングとロギング
- ✅ リトライ機構（指数バックオフ）
- ✅ タイムアウト設定
- ✅ ファイルサイズ制限（最大100MB）
- ✅ 拡張子バリデーション
- ✅ ヘルスチェックエンドポイント
- ✅ OpenAPI/Swagger ドキュメント自動生成

## 🏗️ プロジェクト構造

```
.
├── app/
│   ├── main.py              # FastAPI エントリーポイント
│   ├── deps.py              # 設定・依存性
│   ├── models/
│   │   └── schemas.py       # Pydantic モデル
│   ├── routers/
│   │   ├── stores.py        # Stores API
│   │   ├── documents.py     # Documents API
│   │   └── media.py         # Upload/Import API
│   ├── services/
│   │   ├── file_search.py   # File Search サービス
│   │   └── retry.py         # リトライユーティリティ
│   └── ui/
│       ├── templates/       # Jinja2 テンプレート
│       └── static/          # CSS/JavaScript
├── tests/
│   ├── unit/               # ユニットテスト
│   └── e2e/                # E2Eテスト
├── samples/                # サンプルファイル
├── Dockerfile              # Docker イメージ定義
├── docker-compose.yml      # Docker Compose 設定
├── requirements.txt        # Python 依存関係
├── pyproject.toml          # プロジェクト設定
└── README.md              # このファイル
```

## 🚀 セットアップ手順

### 前提条件

- Docker & Docker Compose
- Google AI API キー（[こちら](https://ai.google.dev/)で取得）

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd gemini-file-search
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して、API キーを設定：

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Docker で起動

```bash
docker compose up --build
```

アプリケーションが起動したら、ブラウザで開く：

- **Web UI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🛠️ ローカル開発（Python直接実行）

### 1. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. アプリケーションの起動

```bash
uvicorn app.main:app --reload
```

## 🧪 テスト

### ユニットテスト実行

```bash
pytest tests/unit -v
```

### E2Eテスト実行（API キー必要）

```bash
GOOGLE_API_KEY=your_key pytest tests/e2e -v -s
```

### カバレッジレポート

```bash
pytest --cov=app --cov-report=html
```

### コード品質チェック

```bash
# リンター
ruff check .

# フォーマッター
black --check .

# 型チェック
mypy app/
```

## 📖 API エンドポイント対応表

| エンドポイント | HTTPメソッド | 説明 | 公式ドキュメント参照 |
|-------------|------------|------|-------------------|
| `/api/stores` | POST | ストア作成 | [fileSearchStores.create](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.create) |
| `/api/stores` | GET | ストア一覧 | [fileSearchStores.list](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.list) |
| `/api/stores/{id}` | GET | ストア取得 | [fileSearchStores.get](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.get) |
| `/api/stores/{id}` | DELETE | ストア削除 | [fileSearchStores.delete](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.delete) |
| `/api/stores/{id}/upload` | POST | ファイルアップロード | [media.uploadToFileSearchStore](https://ai.google.dev/api/file-search/file-search-stores#method:-media.uploadtofilesearchstore) |
| `/api/stores/{id}/import` | POST | ファイルインポート | [fileSearchStores.importFile](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.importfile) |
| `/api/stores/{id}/documents` | GET | ドキュメント一覧 | [documents.list](https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.list) |
| `/api/stores/{id}/documents/{doc_id}` | GET | ドキュメント取得 | [documents.get](https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.get) |
| `/api/stores/{id}/documents/{doc_id}` | DELETE | ドキュメント削除 | [documents.delete](https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.delete) |
| `/api/operations/{name}` | GET | オペレーション状態取得 | [Operations](https://ai.google.dev/api/file-search/file-search-stores#Operation) |

## 🎯 使用例

### cURLでの例

#### ストア作成
```bash
curl -X POST http://localhost:8000/api/stores \
  -H "Content-Type: application/json" \
  -d '{"displayName": "My First Store"}'
```

#### ファイルアップロード
```bash
curl -X POST http://localhost:8000/api/stores/{store_id}/upload \
  -F "file=@samples/sample1.txt" \
  -F "display_name=Sample Document" \
  -F "max_tokens_per_chunk=200" \
  -F "max_overlap_tokens=20"
```

#### ドキュメント一覧
```bash
curl http://localhost:8000/api/stores/{store_id}/documents
```

### Pythonでの例

```python
import httpx

API_BASE = "http://localhost:8000/api"

# ストア作成
response = httpx.post(f"{API_BASE}/stores", json={"displayName": "Test Store"})
store = response.json()
store_id = store["name"].split("/")[-1]

# ファイルアップロード
with open("sample.txt", "rb") as f:
    files = {"file": f}
    data = {"display_name": "Test Doc", "max_tokens_per_chunk": 200}
    response = httpx.post(f"{API_BASE}/stores/{store_id}/upload", files=files, data=data)

# ドキュメント一覧
response = httpx.get(f"{API_BASE}/stores/{store_id}/documents")
documents = response.json()["documents"]
```

## 🔧 設定

環境変数で以下を設定可能：

| 変数名 | デフォルト | 説明 |
|-------|---------|------|
| `GOOGLE_API_KEY` | - | Google AI API キー（必須） |
| `APP_HOST` | 0.0.0.0 | ホストアドレス |
| `APP_PORT` | 8000 | ポート番号 |
| `LOG_LEVEL` | INFO | ログレベル |
| `MAX_UPLOAD_SIZE` | 104857600 | 最大アップロードサイズ（バイト、100MB） |
| `ALLOWED_EXTENSIONS` | .txt,.pdf,... | 許可する拡張子 |
| `API_TIMEOUT` | 60 | APIタイムアウト（秒） |
| `API_MAX_RETRIES` | 3 | 最大リトライ回数 |

## 📦 対応ファイル形式

- Plain text (`.txt`)
- Markdown (`.md`)
- PDF (`.pdf`)
- HTML (`.html`)
- CSV (`.csv`)
- JSON (`.json`)
- Microsoft Word (`.doc`, `.docx`)

## ⚠️ 制約・既知の問題

1. **ファイルサイズ制限**: 最大100MBまで（Google API制限）
2. **ストレージ制限**:
   - Free tier: 1GB
   - Pro tier: 100GB
   - Enterprise: 1TB
3. **推奨ストアサイズ**: 個別ストアは20GB以下が推奨
4. **検索機能**: 現在の実装では検索エンドポイントは含まれていません（Gemini モデルとの統合が必要）

## 🔐 セキュリティ

- API キーはサーバーサイドでのみ管理
- ファイル拡張子・サイズのバリデーション
- CORS設定（ローカル開発用に最小限）
- 入力検証（Pydantic使用）

## 🤝 貢献

プルリクエスト歓迎です！

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 ライセンス

MIT License

## 🙏 謝辞

- [Google Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)

## 📞 サポート

問題が発生した場合：

1. [Issues](https://github.com/yourusername/gemini-file-search/issues)で既存の問題を確認
2. 新しいissueを作成して詳細を報告

## 🗺️ ロードマップ

- [ ] 検索エンドポイントの実装（Gemini モデル統合）
- [ ] メタデータフィルタリング機能
- [ ] バッチアップロード機能
- [ ] ドキュメント更新機能
- [ ] より詳細な分析・統計機能
- [ ] Streamlit代替UI

---

**注意**: このプロジェクトは教育・開発目的です。本番環境で使用する場合は、適切なセキュリティレビューを実施してください。
