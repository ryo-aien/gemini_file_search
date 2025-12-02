#!/bin/bash
# アプリケーションを起動するスクリプト

echo "======================================"
echo "Starting Gemini File Search API"
echo "======================================"
echo ""

# .envファイルの確認
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please run: cp .env.example .env"
    echo "Then edit .env and set your GOOGLE_API_KEY"
    exit 1
fi

# APIキーの確認
if ! grep -q "GOOGLE_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "Warning: GOOGLE_API_KEY may not be set in .env"
    echo "Please check your .env file"
fi

# Decide which port to use (Cloud Run provides PORT; fall back to .env or 8000)
PORT_FROM_FILE=$(grep -E '^PORT=' .env | tail -n1 | cut -d '=' -f2)
APP_PORT_FROM_FILE=$(grep -E '^APP_PORT=' .env | tail -n1 | cut -d '=' -f2)
export PORT="${PORT:-${APP_PORT:-${PORT_FROM_FILE:-${APP_PORT_FROM_FILE:-8000}}}}"

# Dockerで起動するか、ローカルで起動するか選択
echo "How do you want to start the application?"
echo "1) Docker (recommended)"
echo "2) Local Python"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Starting with Docker..."
        docker compose down 2>/dev/null
        docker compose up --build
        ;;
    2)
        echo ""
        echo "Starting with local Python..."

        # 仮想環境の確認
        if [ ! -d "venv" ]; then
            echo "Virtual environment not found. Creating..."
            python3 -m venv venv
        fi

        echo "Activating virtual environment..."
        source venv/bin/activate

        echo "Installing dependencies..."
        pip install -q --upgrade pip
        pip install -q -r requirements.txt

        echo ""
        echo "Starting application..."
        echo "Access the app at: http://localhost:${PORT}"
        echo "API docs at: http://localhost:${PORT}/api/docs"
        echo ""
        uvicorn app.main:app --reload --host 0.0.0.0 --port "${PORT}"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
