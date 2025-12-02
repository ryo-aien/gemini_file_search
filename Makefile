.PHONY: help setup install run test lint format type-check docker-build docker-up docker-down clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup         - Initial project setup"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run the application locally"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-e2e      - Run E2E tests (requires API key)"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo "  make type-check    - Run type checker"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make clean         - Clean up temporary files"

setup:
	@echo "Setting up project..."
	cp -n .env.example .env || true
	@echo "Please edit .env and add your GOOGLE_API_KEY"

install:
	pip install -r requirements.txt

run:
	PORT=$${PORT:-$${APP_PORT:-8000}} uvicorn app.main:app --reload --host 0.0.0.0 --port $$PORT

test:
	pytest -v

test-unit:
	pytest tests/unit -v

test-e2e:
	pytest tests/e2e -v -s

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	black .
	ruff check --fix .

type-check:
	mypy app/

docker-build:
	docker compose build

docker-up:
	docker compose up -d
	@echo "Application is running at http://localhost:$${APP_PORT:-8000}"
	@echo "API docs at http://localhost:$${APP_PORT:-8000}/api/docs"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf /tmp/uploads/* 2>/dev/null || true
	@echo "Cleanup complete"
