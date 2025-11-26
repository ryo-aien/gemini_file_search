"""
Documents router.

Endpoints:
- GET /api/stores/{store_id}/documents - List documents
- GET /api/stores/{store_id}/documents/{document_id} - Get document
- DELETE /api/stores/{store_id}/documents/{document_id} - Delete document
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.deps import SettingsDep
from app.models.schemas import Document, DocumentList
from app.services.file_search import FileSearchAPIError, FileSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stores/{store_id}/documents", tags=["documents"])


@router.get("", response_model=DocumentList)
async def list_documents(
    store_id: str,
    settings: SettingsDep,
    page_size: int = Query(default=10, ge=1, le=20),
    page_token: Optional[str] = Query(default=None),
) -> DocumentList:
    """
    List documents in a File Search Store.

    Args:
        store_id: Store ID
        settings: Application settings
        page_size: Maximum results per page (1-20)
        page_token: Token for pagination

    Returns:
        List of Documents with next page token

    Raises:
        HTTPException: If listing fails
    """
    try:
        service = FileSearchService(settings)
        store_name = f"fileSearchStores/{store_id}"
        documents = await service.list_documents(
            store_name=store_name, page_size=page_size, page_token=page_token
        )
        logger.info(f"Listed {len(documents.documents)} documents in store {store_id}")
        return documents
    except FileSearchAPIError as e:
        logger.error(f"Failed to list documents in store {store_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=Document)
async def get_document(
    store_id: str,
    document_id: str,
    settings: SettingsDep,
) -> Document:
    """
    Get information about a specific document.

    Args:
        store_id: Store ID
        document_id: Document ID
        settings: Application settings

    Returns:
        Document information

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = FileSearchService(settings)
        document_name = f"fileSearchStores/{store_id}/documents/{document_id}"
        document = await service.get_document(document_name)
        logger.info(f"Retrieved document: {document.name}")
        return document
    except FileSearchAPIError as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    store_id: str,
    document_id: str,
    settings: SettingsDep,
    force: bool = Query(default=False, description="Delete associated chunks"),
) -> None:
    """
    Delete a document from a File Search Store.

    Args:
        store_id: Store ID
        document_id: Document ID
        settings: Application settings
        force: If true, deletes associated chunks

    Raises:
        HTTPException: If deletion fails
    """
    try:
        service = FileSearchService(settings)
        document_name = f"fileSearchStores/{store_id}/documents/{document_id}"
        await service.delete_document(document_name, force=force)
        logger.info(f"Deleted document: {document_name}")
    except FileSearchAPIError as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
