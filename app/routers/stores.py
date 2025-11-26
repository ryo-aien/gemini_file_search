"""
File Search Stores router.

Endpoints:
- POST /api/stores - Create store
- GET /api/stores - List stores
- GET /api/stores/{store_id} - Get store
- DELETE /api/stores/{store_id} - Delete store
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.deps import Settings, SettingsDep
from app.models.schemas import FileSearchStore, FileSearchStoreCreate, FileSearchStoreList
from app.services.file_search import FileSearchAPIError, FileSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.post("", response_model=FileSearchStore, status_code=201)
async def create_store(
    request: FileSearchStoreCreate,
    settings: SettingsDep,
) -> FileSearchStore:
    """
    Create a new File Search Store.

    Args:
        request: Store creation request
        settings: Application settings

    Returns:
        Created FileSearchStore

    Raises:
        HTTPException: If creation fails
    """
    try:
        service = FileSearchService(settings)
        store = await service.create_store(display_name=request.display_name)
        logger.info(f"Created store: {store.name}")
        return store
    except FileSearchAPIError as e:
        logger.error(f"Failed to create store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=FileSearchStoreList)
async def list_stores(
    settings: SettingsDep,
    page_size: int = Query(default=10, ge=1, le=20),
    page_token: Optional[str] = Query(default=None),
) -> FileSearchStoreList:
    """
    List all File Search Stores with pagination.

    Args:
        settings: Application settings
        page_size: Maximum results per page (1-20)
        page_token: Token for pagination

    Returns:
        List of FileSearchStores with next page token

    Raises:
        HTTPException: If listing fails
    """
    try:
        service = FileSearchService(settings)
        stores = await service.list_stores(page_size=page_size, page_token=page_token)
        logger.info(f"Listed {len(stores.file_search_stores)} stores")
        return stores
    except FileSearchAPIError as e:
        logger.error(f"Failed to list stores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_id}", response_model=FileSearchStore)
async def get_store(
    store_id: str,
    settings: SettingsDep,
) -> FileSearchStore:
    """
    Get information about a specific File Search Store.

    Args:
        store_id: Store ID
        settings: Application settings

    Returns:
        FileSearchStore information

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = FileSearchService(settings)
        store_name = f"fileSearchStores/{store_id}"
        store = await service.get_store(store_name)
        logger.info(f"Retrieved store: {store.name}")
        return store
    except FileSearchAPIError as e:
        logger.error(f"Failed to get store {store_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{store_id}", status_code=204)
async def delete_store(
    store_id: str,
    settings: SettingsDep,
    force: bool = Query(default=False, description="Delete associated documents"),
) -> None:
    """
    Delete a File Search Store.

    Args:
        store_id: Store ID
        settings: Application settings
        force: If true, deletes associated documents

    Raises:
        HTTPException: If deletion fails
    """
    try:
        service = FileSearchService(settings)
        store_name = f"fileSearchStores/{store_id}"
        await service.delete_store(store_name, force=force)
        logger.info(f"Deleted store: {store_name}")
    except FileSearchAPIError as e:
        logger.error(f"Failed to delete store {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
