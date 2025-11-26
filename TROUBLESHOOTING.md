# トラブルシューティング

## インストールエラー

### Python 3.13 で pydantic-core のビルドエラー

**症状:**
```
ERROR: Failed building wheel for pydantic-core
```

**原因:**
Python 3.13 は比較的新しく、一部の古いパッケージバージョンではビルド済みホイールが提供されていません。

**解決方法:**

1. **パッケージを再インストール（推奨）:**
   ```bash
   # 仮想環境をクリーンアップ
   rm -rf venv

   # 新しい仮想環境を作成
   python3 -m venv venv
   source venv/bin/activate  # Mac/Linux

   # pipを最新版に更新
   pip install --upgrade pip

   # 依存関係をインストール
   pip install -r requirements.txt
   ```

2. **Python 3.11 または 3.12 を使用（最も安定）:**
   ```bash
   # Homebrewでインストール（Mac）
   brew install python@3.11

   # 仮想環境を作成
   python3.11 -m venv venv
   source venv/bin/activate

   # 依存関係をインストール
   pip install -r requirements.txt
   ```

3. **Dockerを使用（最も簡単）:**
   ```bash
   # Dockerなら環境依存なし
   docker compose up --build
   ```

### Google API キーが設定されていない

**症状:**
```
GOOGLE_API_KEY not set. API calls will fail.
```

**解決方法:**

1. `.env` ファイルを作成:
   ```bash
   cp .env.example .env
   ```

2. `.env` を編集してAPIキーを設定:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. Google AI Studio でAPIキーを取得: https://ai.google.dev/

### Docker ビルドエラー

**症状:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**解決方法:**

1. **Dockerキャッシュをクリア:**
   ```bash
   docker compose down
   docker system prune -a
   docker compose build --no-cache
   ```

2. **Apple Silicon (M1/M2/M3) の場合:**
   ```bash
   # プラットフォームを明示的に指定
   docker compose build --build-arg BUILDPLATFORM=linux/arm64
   ```

## 実行時エラー

### ポート 8000 が既に使用されている

**症状:**
```
ERROR: address already in use
```

**解決方法:**

1. **別のポートを使用:**
   ```bash
   # .env ファイルを編集
   APP_PORT=8001

   # または環境変数で指定
   APP_PORT=8001 docker compose up
   ```

2. **既存のプロセスを停止:**
   ```bash
   # ポートを使用しているプロセスを確認
   lsof -i :8000

   # プロセスを終了
   kill -9 <PID>
   ```

### API呼び出しがタイムアウトする

**症状:**
```
TimeoutException: Request timed out
```

**解決方法:**

1. **タイムアウト時間を延長:**
   `.env` ファイルで設定:
   ```env
   API_TIMEOUT=120  # デフォルト60秒 → 120秒に延長
   ```

2. **ネットワーク接続を確認:**
   ```bash
   # Google APIへの接続テスト
   curl -I https://generativelanguage.googleapis.com
   ```

### ファイルアップロードが失敗する

**症状:**
```
413 Payload Too Large
```

**解決方法:**

1. **ファイルサイズを確認:**
   - 最大サイズ: 100MB（Google API制限）

2. **許可される拡張子:**
   - .txt, .pdf, .md, .doc, .docx, .html, .csv, .json

3. **設定を変更（必要に応じて）:**
   ```env
   MAX_UPLOAD_SIZE=52428800  # 50MBに制限
   ```

## テストエラー

### E2Eテストが失敗する

**症状:**
```
pytest tests/e2e -v
SKIPPED - GOOGLE_API_KEY not set
```

**解決方法:**

```bash
# APIキーを環境変数で渡す
GOOGLE_API_KEY=your_key pytest tests/e2e -v
```

### 型チェックエラー

**症状:**
```
mypy: error: Incompatible types
```

**解決方法:**

1. **mypy キャッシュをクリア:**
   ```bash
   rm -rf .mypy_cache
   mypy app/
   ```

2. **型アノテーションを確認:**
   - すべての関数に型ヒントが必要
   - `Optional[T]` や `Union[T1, T2]` の使用

## よくある質問

### Q: Python 3.10 でも動作しますか？

A: いいえ、Python 3.11以上が必要です。以下の機能を使用しているためです：
- PEP 604: `X | Y` 型ユニオン構文
- 改善されたエラーメッセージ
- パフォーマンス向上

### Q: 検索機能はどこにありますか？

A: 現在のバージョンでは、ドキュメントの管理（アップロード・削除）のみ実装されています。検索機能は Gemini モデルとの統合が必要なため、今後の拡張として予定されています。

### Q: プロダクション環境で使用できますか？

A: はい、ただし以下を確認してください：
- 適切なセキュリティレビュー
- APIキーの安全な管理
- レート制限の設定
- エラー監視の実装
- バックアップ戦略

### Q: 他のクラウドプロバイダーで動作しますか？

A: はい、Dockerコンテナとして動作するため、以下で実行可能：
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Kubernetes

## サポート

それでも問題が解決しない場合：

1. **ログを確認:**
   ```bash
   # Docker の場合
   docker compose logs -f

   # ローカルの場合
   # ログは stdout に出力されます
   ```

2. **Issueを作成:**
   - https://github.com/yourusername/gemini-file-search/issues
   - エラーメッセージの全文
   - 環境情報（OS、Pythonバージョン）
   - 再現手順

3. **デバッグモードで実行:**
   ```bash
   LOG_LEVEL=DEBUG uvicorn app.main:app --reload
   ```
