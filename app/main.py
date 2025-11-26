"""
Main FastAPI application for Gemini File Search API.

Reference: https://ai.google.dev/gemini-api/docs/file-search
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.deps import Settings, get_settings, setup_logging
from app.routers import documents, media, search, stores

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()
    setup_logging(settings)
    logger.info("Starting Gemini File Search API application")
    logger.info(f"API Base URL: {settings.api_base_url}")

    # Validate API key
    if not settings.google_api_key:
        logger.warning("GOOGLE_API_KEY not set. API calls will fail.")

    yield

    logger.info("Shutting down Gemini File Search API application")


# Create FastAPI app
app = FastAPI(
    title="Gemini File Search API",
    description="Full-featured implementation of Google's Gemini File Search API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Include routers
app.include_router(stores.router)
app.include_router(documents.router)
app.include_router(media.router)
app.include_router(search.router)

# Setup templates and static files
templates_dir = Path(__file__).parent / "ui" / "templates"
static_dir = Path(__file__).parent / "ui" / "static"

# Create directories if they don't exist
templates_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the main UI page."""
    settings = get_settings()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Gemini File Search",
            "api_key_configured": bool(settings.google_api_key),
        },
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    settings = get_settings()
    return JSONResponse(
        {
            "status": "healthy",
            "api_key_configured": bool(settings.google_api_key),
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs for details."},
    )


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
