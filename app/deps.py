"""
Dependencies and configuration for the application.
"""

import logging
import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google AI API
    google_api_key: str = ""

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    log_level: str = "INFO"

    # File Upload
    max_upload_size: int = 104857600  # 100MB
    allowed_extensions: str = ".txt,.pdf,.md,.doc,.docx,.html,.csv,.json"

    # API Configuration
    api_timeout: int = 60
    api_max_retries: int = 3
    api_retry_delay: float = 1.0
    api_base_url: str = "https://generativelanguage.googleapis.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Get allowed extensions as a list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging(settings: Settings) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


SettingsDep = Annotated[Settings, Depends(get_settings)]
