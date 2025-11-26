"""
Unit tests for Pydantic schemas.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    ChunkingConfig,
    Document,
    DocumentState,
    FileSearchStore,
    FileSearchStoreCreate,
)


def test_file_search_store_create_valid() -> None:
    """Test valid FileSearchStoreCreate."""
    store = FileSearchStoreCreate(display_name="Test Store")
    assert store.display_name == "Test Store"


def test_file_search_store_create_no_display_name() -> None:
    """Test FileSearchStoreCreate without display name."""
    store = FileSearchStoreCreate()
    assert store.display_name is None


def test_file_search_store_create_max_length() -> None:
    """Test FileSearchStoreCreate display name max length."""
    with pytest.raises(ValidationError):
        FileSearchStoreCreate(display_name="a" * 513)


def test_chunking_config_defaults() -> None:
    """Test ChunkingConfig default values."""
    config = ChunkingConfig()
    assert config.max_tokens_per_chunk == 200
    assert config.max_overlap_tokens == 20


def test_chunking_config_custom() -> None:
    """Test ChunkingConfig with custom values."""
    config = ChunkingConfig(max_tokens_per_chunk=500, max_overlap_tokens=50)
    assert config.max_tokens_per_chunk == 500
    assert config.max_overlap_tokens == 50


def test_file_search_store_valid() -> None:
    """Test valid FileSearchStore."""
    now = datetime.now()
    store = FileSearchStore(
        name="fileSearchStores/test123",
        displayName="Test Store",
        createTime=now,
        updateTime=now,
        activeDocumentsCount=5,
        pendingDocumentsCount=2,
        failedDocumentsCount=1,
        sizeBytes=1024,
    )
    assert store.name == "fileSearchStores/test123"
    assert store.display_name == "Test Store"
    assert store.active_documents_count == 5


def test_document_state_enum() -> None:
    """Test DocumentState enum values."""
    assert DocumentState.STATE_ACTIVE == "STATE_ACTIVE"
    assert DocumentState.STATE_PENDING == "STATE_PENDING"
    assert DocumentState.STATE_FAILED == "STATE_FAILED"


def test_document_valid() -> None:
    """Test valid Document."""
    now = datetime.now()
    doc = Document(
        name="fileSearchStores/store123/documents/doc456",
        displayName="Test Document",
        customMetadata=[],
        createTime=now,
        updateTime=now,
        state=DocumentState.STATE_ACTIVE,
        sizeBytes=2048,
        mimeType="text/plain",
    )
    assert doc.name == "fileSearchStores/store123/documents/doc456"
    assert doc.state == DocumentState.STATE_ACTIVE
