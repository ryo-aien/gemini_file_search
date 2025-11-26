"""
Pydantic models for File Search API.

Reference: https://ai.google.dev/api/file-search/
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class DocumentState(str, Enum):
    """Document lifecycle states."""

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_PENDING = "STATE_PENDING"
    STATE_ACTIVE = "STATE_ACTIVE"
    STATE_FAILED = "STATE_FAILED"


class CustomMetadataValue(BaseModel):
    """Custom metadata value union type."""

    string_value: Optional[str] = Field(None, alias="stringValue")
    string_list_value: Optional[list[str]] = Field(None, alias="stringListValue")
    numeric_value: Optional[float] = Field(None, alias="numericValue")


class CustomMetadata(BaseModel):
    """Custom metadata key-value pair."""

    key: str
    value: Union[str, list[str], float]


class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""

    max_tokens_per_chunk: int = Field(default=200, alias="maxTokensPerChunk")
    max_overlap_tokens: int = Field(default=20, alias="maxOverlapTokens")


# File Search Store Schemas


class FileSearchStoreCreate(BaseModel):
    """Request to create a new File Search Store."""

    display_name: Optional[str] = Field(None, max_length=512, alias="displayName")


class FileSearchStore(BaseModel):
    """File Search Store resource."""

    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    create_time: datetime = Field(alias="createTime")
    update_time: datetime = Field(alias="updateTime")
    active_documents_count: int = Field(default=0, alias="activeDocumentsCount")
    pending_documents_count: int = Field(default=0, alias="pendingDocumentsCount")
    failed_documents_count: int = Field(default=0, alias="failedDocumentsCount")
    size_bytes: int = Field(default=0, alias="sizeBytes")


class FileSearchStoreList(BaseModel):
    """List of File Search Stores with pagination."""

    file_search_stores: list[FileSearchStore] = Field(default_factory=list, alias="fileSearchStores")
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")


# Document Schemas


class Document(BaseModel):
    """Document resource in a File Search Store."""

    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    custom_metadata: list[dict[str, Any]] = Field(default_factory=list, alias="customMetadata")
    create_time: datetime = Field(alias="createTime")
    update_time: datetime = Field(alias="updateTime")
    state: DocumentState
    size_bytes: int = Field(alias="sizeBytes")
    mime_type: Optional[str] = Field(None, alias="mimeType")


class DocumentList(BaseModel):
    """List of Documents with pagination."""

    documents: list[Document] = Field(default_factory=list)
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")


# Upload Schemas


class UploadRequest(BaseModel):
    """Request to upload a document to a File Search Store."""

    display_name: Optional[str] = Field(None, alias="displayName")
    custom_metadata: Optional[list[dict[str, Any]]] = Field(None, alias="customMetadata")
    chunking_config: Optional[ChunkingConfig] = Field(None, alias="chunkingConfig")
    mime_type: Optional[str] = Field(None, alias="mimeType")


class ImportFileRequest(BaseModel):
    """Request to import an existing file into a File Search Store."""

    file_name: str = Field(alias="fileName")
    custom_metadata: Optional[list[dict[str, Any]]] = Field(None, alias="customMetadata")
    chunking_config: Optional[ChunkingConfig] = Field(None, alias="chunkingConfig")


# Operation Schemas


class OperationMetadata(BaseModel):
    """Metadata for long-running operations."""

    progress_percent: Optional[int] = Field(None, alias="progressPercent")
    status_message: Optional[str] = Field(None, alias="statusMessage")


class OperationError(BaseModel):
    """Error from a failed operation."""

    code: int
    message: str
    details: Optional[list[dict[str, Any]]] = None


class Operation(BaseModel):
    """Long-running operation resource."""

    name: str
    done: Optional[bool] = False  # Default to False if not provided
    metadata: Optional[dict[str, Any]] = None
    error: Optional[OperationError] = None
    response: Optional[dict[str, Any]] = None

    model_config = {"extra": "allow"}  # Allow extra fields from API


# Search Schemas (using Gemini generateContent API)


class FileSearchTool(BaseModel):
    """FileSearch tool configuration for Gemini."""

    file_search_store_names: list[str] = Field(alias="fileSearchStoreNames")
    metadata_filter: Optional[str] = Field(None, alias="metadataFilter")


class Tool(BaseModel):
    """Tool configuration for Gemini API."""

    file_search: FileSearchTool = Field(alias="fileSearch")


class ContentPart(BaseModel):
    """Content part for Gemini request."""

    text: str


class Content(BaseModel):
    """Content for Gemini request."""

    parts: list[ContentPart]
    role: str = "user"


class GenerateContentRequest(BaseModel):
    """Request to Gemini generateContent API with FileSearch."""

    contents: list[Content]
    tools: list[Tool]


class GroundingChunk(BaseModel):
    """A grounding chunk from File Search."""

    web: Optional[dict[str, Any]] = None
    retrieved_context: Optional[dict[str, Any]] = Field(None, alias="retrievedContext")


class GroundingSupport(BaseModel):
    """Grounding support information."""

    grounding_chunk_indices: Optional[list[int]] = Field(None, alias="groundingChunkIndices")
    confidence_scores: Optional[list[float]] = Field(None, alias="confidenceScores")
    segment: Optional[dict[str, Any]] = None


class GroundingMetadata(BaseModel):
    """Grounding metadata from File Search."""

    grounding_chunks: Optional[list[GroundingChunk]] = Field(None, alias="groundingChunks")
    grounding_supports: Optional[list[GroundingSupport]] = Field(None, alias="groundingSupports")
    web_search_queries: Optional[list[str]] = Field(None, alias="webSearchQueries")

    model_config = {"extra": "allow"}


class Candidate(BaseModel):
    """A candidate response from Gemini."""

    content: dict[str, Any]
    finish_reason: Optional[str] = Field(None, alias="finishReason")
    grounding_metadata: Optional[GroundingMetadata] = Field(None, alias="groundingMetadata")
    index: int = 0

    model_config = {"extra": "allow"}


class GenerateContentResponse(BaseModel):
    """Response from Gemini generateContent API."""

    candidates: list[Candidate]
    prompt_feedback: Optional[dict[str, Any]] = Field(None, alias="promptFeedback")
    usage_metadata: Optional[dict[str, Any]] = Field(None, alias="usageMetadata")

    model_config = {"extra": "allow"}


class SearchRequest(BaseModel):
    """Simplified search request for UI."""

    query: str
    store_ids: list[str] = Field(alias="storeIds")
    metadata_filter: Optional[str] = Field(None, alias="metadataFilter")
    model: str = "gemini-2.5-flash"  # Default model (file_search supported)


class SearchResult(BaseModel):
    """Simplified search result for UI."""

    answer: str
    grounding_chunks: list[dict[str, Any]] = Field(default_factory=list, alias="groundingChunks")
    sources: list[str] = Field(default_factory=list)
