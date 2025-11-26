"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.deps import Settings, get_settings
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        google_api_key="test_api_key",
        api_timeout=30,
        api_max_retries=3,
        api_retry_delay=0.1,
    )


@pytest.fixture
def override_settings(test_settings: Settings) -> None:
    """Override app settings with test settings."""

    def _get_test_settings() -> Settings:
        return test_settings

    app.dependency_overrides[get_settings] = _get_test_settings
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_settings: None) -> TestClient:
    """Get test client."""
    return TestClient(app)
