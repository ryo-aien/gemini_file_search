# クイックスタートガイド

最速でGemini File Search APIを動かすためのガイドです。

## 方法1: Docker（推奨・最も簡単）

環境依存がなく、Python のインストールも不要です。

### ステップ

```bash
# 1. Google AI API キーを取得
# https://ai.google.dev/ にアクセスしてAPIキーを取得

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. .envファイルを編集してAPIキーを設定
# GOOGLE_API_KEY=あなたのAPIキー

# 4. Dockerで起動
docker compose up --build

# 5. ブラウザで開く
open http://localhost:8000
```

**完了！** たった5ステップで動作します。

### トラブルシューティング

- **ポート8000が使用中の場合:**
  ```bash
  APP_PORT=8001 docker compose up
  ```

- **M1/M2/M3 Mac で問題が発生した場合:**
  ```bash
  docker compose build --build-arg BUILDPLATFORM=linux/arm64
  ```

## 方法2: ローカルPython（開発者向け）

より細かい制御が必要な場合や、コードを編集しながら開発する場合。

### 前提条件

- Python 3.11, 3.12, または 3.13

### ステップ

```bash
# 1. 仮想環境を作成
python3 -m venv venv

# 2. 仮想環境を有効化
source venv/bin/activate  # Mac/Linux
# または
venv\Scripts\activate  # Windows

# 3. pipを最新版に更新
pip install --upgrade pip

# 4. 依存関係をインストール
pip install -r requirements.txt

# 5. 環境変数を設定
cp .env.example .env
# .envを編集してGOOGLE_API_KEYを設定

# 6. アプリケーションを起動
uvicorn app.main:app --reload

# 7. ブラウザで開く
open http://localhost:8000
```

### トラブルシューティング

**インストールエラーが発生した場合:**

```bash
# 1. 仮想環境をクリーンアップ
rm -rf venv

# 2. 推奨バージョンのPythonを使用
python3.11 -m venv venv
source venv/bin/activate

# 3. 再度インストール
pip install --upgrade pip
pip install -r requirements.txt
```

詳細は [TROUBLESHOOTING.md](TROUBLESHOOTING.md) を参照してください。

## 方法3: Makefileを使用（便利）

Makefileで簡単にタスクを実行できます。

```bash
# セットアップ
make setup

# 依存関係をインストール
make install

# アプリケーションを起動
make run

# または Docker で起動
make docker-up
```

## 初めての操作

### 1. ストアを作成

Web UI（http://localhost:8000）で：
1. 「Stores」タブを開く
2. 「Display Name」を入力（例: "My First Store"）
3. 「Create Store」ボタンをクリック

### 2. ファイルをアップロード

1. 「Upload」タブを開く
2. 作成したストアを選択
3. ファイルを選択（samples/sample1.txt など）
4. 「Upload File」ボタンをクリック

### 3. ドキュメントを確認

1. 「Documents」タブを開く
2. ストアを選択
3. 「Refresh List」ボタンをクリック
4. アップロードされたドキュメントが表示されます

## APIを試す

### cURLで試す

```bash
# ストア作成
curl -X POST http://localhost:8000/api/stores \
  -H "Content-Type: application/json" \
  -d '{"displayName": "Test Store"}'

# ストア一覧
curl http://localhost:8000/api/stores

# ファイルアップロード
curl -X POST http://localhost:8000/api/stores/{store_id}/upload \
  -F "file=@samples/sample1.txt" \
  -F "display_name=Test Document"
```

### Swagger UIで試す

ブラウザで http://localhost:8000/api/docs を開くと、対話的にAPIを試せます。

## サンプルファイル

`samples/` ディレクトリに以下のサンプルファイルがあります：

- `sample1.txt` - プレーンテキスト
- `sample2.md` - Markdown
- `sample3.json` - JSON

これらをアップロードして動作を確認できます。

## 次のステップ

- [README.md](README.md) で詳細な機能を確認
- [API ドキュメント](http://localhost:8000/api/docs) で全エンドポイントを確認
- [CONTRIBUTING.md](CONTRIBUTING.md) で開発に参加する方法を確認

## ヘルプが必要な場合

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - よくある問題と解決方法
- [GitHub Issues](https://github.com/yourusername/gemini-file-search/issues) - バグ報告や質問

---

**楽しんでください！** 🚀
