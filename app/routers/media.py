"""
Media upload router.

Endpoints:
- POST /api/stores/{store_id}/upload - Upload file to store
- POST /api/stores/{store_id}/import - Import existing file
- GET /api/operations/{operation_id} - Get operation status
"""

import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.deps import SettingsDep
from app.models.schemas import ChunkingConfig, Operation
from app.services.file_search import FileSearchAPIError, FileSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["media"])


@router.post("/stores/{store_id}/upload", response_model=Operation, status_code=202)
async def upload_to_store(
    store_id: str,
    settings: SettingsDep,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(default=None),
    max_tokens_per_chunk: int = Form(default=200),
    max_overlap_tokens: int = Form(default=20),
) -> Operation:
    """
    Upload a file to a File Search Store.

    Args:
        store_id: Store ID
        settings: Application settings
        file: File to upload
        display_name: Optional display name
        max_tokens_per_chunk: Maximum tokens per chunk
        max_overlap_tokens: Maximum overlap tokens

    Returns:
        Operation for tracking upload progress

    Raises:
        HTTPException: If upload fails
    """
    try:
        # Validate file extension
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.allowed_extensions_list:
                raise HTTPException(
                    status_code=400,
                    detail=f"File extension {file_ext} not allowed. "
                    f"Allowed: {settings.allowed_extensions_list}",
                )

        # Save file temporarily
        temp_dir = Path("/tmp/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / (file.filename or "upload")

        # Check file size
        content = await file.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {len(content)} exceeds maximum {settings.max_upload_size}",
            )

        # Write to temp file
        temp_file.write_bytes(content)

        try:
            service = FileSearchService(settings)
            store_name = f"fileSearchStores/{store_id}"

            chunking_config = ChunkingConfig(
                max_tokens_per_chunk=max_tokens_per_chunk,
                max_overlap_tokens=max_overlap_tokens,
            )

            operation = await service.upload_to_file_search_store(
                store_name=store_name,
                file_path=temp_file,
                display_name=display_name or file.filename,
                chunking_config=chunking_config,
            )

            logger.info(f"Started upload operation: {operation.name}")
            return operation

        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    except FileSearchAPIError as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stores/{store_id}/import", response_model=Operation, status_code=202)
async def import_file(
    store_id: str,
    settings: SettingsDep,
    file_name: str = Form(...),
    max_tokens_per_chunk: int = Form(default=200),
    max_overlap_tokens: int = Form(default=20),
) -> Operation:
    """
    Import an existing file from the Files service.

    Args:
        store_id: Store ID
        settings: Application settings
        file_name: Name of file in Files service
        max_tokens_per_chunk: Maximum tokens per chunk
        max_overlap_tokens: Maximum overlap tokens

    Returns:
        Operation for tracking import progress

    Raises:
        HTTPException: If import fails
    """
    try:
        service = FileSearchService(settings)
        store_name = f"fileSearchStores/{store_id}"

        chunking_config = ChunkingConfig(
            max_tokens_per_chunk=max_tokens_per_chunk,
            max_overlap_tokens=max_overlap_tokens,
        )

        operation = await service.import_file(
            store_name=store_name,
            file_name=file_name,
            chunking_config=chunking_config,
        )

        logger.info(f"Started import operation: {operation.name}")
        return operation

    except FileSearchAPIError as e:
        logger.error(f"Failed to import file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations/{operation_name:path}", response_model=Operation)
async def get_operation(
    operation_name: str,
    settings: SettingsDep,
) -> Operation:
    """
    Get the status of a long-running operation.

    Args:
        operation_name: Full operation name
        settings: Application settings

    Returns:
        Operation status

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = FileSearchService(settings)
        operation = await service.get_operation(operation_name)
        logger.info(f"Retrieved operation: {operation.name}, done: {operation.done}")
        return operation

    except FileSearchAPIError as e:
        logger.error(f"Failed to get operation {operation_name}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
