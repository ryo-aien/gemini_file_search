"""
File Search service for interacting with Google's File Search API.

Reference: https://ai.google.dev/api/file-search/
"""

import json
import logging
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, Optional

import httpx
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential

from app.deps import Settings
from app.models.schemas import (
    ChunkingConfig,
    Document,
    DocumentList,
    FileSearchStore,
    FileSearchStoreCreate,
    FileSearchStoreList,
    Operation,
)
from app.services.retry import create_retry_decorator

logger = logging.getLogger(__name__)


class FileSearchAPIError(Exception):
    """Base exception for File Search API errors."""

    pass


class FileSearchService:
    """
    Service for interacting with Google's File Search API.

    Implements all endpoints from:
    - https://ai.google.dev/api/file-search/file-search-stores
    - https://ai.google.dev/api/file-search/documents
    """

    def __init__(self, settings: Settings):
        """
        Initialize the File Search service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.api_base_url
        self.api_key = settings.google_api_key
        self.timeout = settings.api_timeout

        # Create retry decorator for API calls
        self.retry_decorator = create_retry_decorator(
            max_attempts=settings.api_max_retries,
            min_wait=settings.api_retry_delay,
            max_wait=10.0,
            exceptions=(httpx.HTTPStatusError, httpx.TimeoutException),
        )

    def _get_headers(self) -> dict[str, str]:
        """Get common request headers."""
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
        }

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API with retry logic.

        Args:
            method: HTTP method
            path: API path
            json: JSON request body
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            FileSearchAPIError: If the request fails
        """
        url = f"{self.base_url}{path}"

        @self.retry_decorator
        async def make_request() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=json,
                    params=params,
                )
                response.raise_for_status()
                return response.json() if response.content else {}

        try:
            return await make_request()
        except httpx.HTTPStatusError as e:
            logger.error(f"API request failed: {e.response.status_code} - {e.response.text}")
            raise FileSearchAPIError(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise FileSearchAPIError(f"Request failed: {str(e)}")

    # File Search Store Methods

    async def create_store(self, display_name: Optional[str] = None) -> FileSearchStore:
        """
        Create a new File Search Store.

        Reference: https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.create

        Args:
            display_name: Optional display name (max 512 characters)

        Returns:
            Created FileSearchStore
        """
        body = {}
        if display_name:
            body["displayName"] = display_name

        response = await self._request("POST", "/v1beta/fileSearchStores", json=body)
        return FileSearchStore(**response)

    async def list_stores(
        self, page_size: int = 10, page_token: Optional[str] = None
    ) -> FileSearchStoreList:
        """
        List all File Search Stores.

        Reference: https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.list

        Args:
            page_size: Maximum results per page (default 10, max 20)
            page_token: Token for pagination

        Returns:
            List of FileSearchStores with pagination
        """
        params = {"pageSize": min(page_size, 20)}
        if page_token:
            params["pageToken"] = page_token

        response = await self._request("GET", "/v1beta/fileSearchStores", params=params)
        return FileSearchStoreList(**response)

    async def get_store(self, store_name: str) -> FileSearchStore:
        """
        Get information about a specific File Search Store.

        Reference: https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.get

        Args:
            store_name: Store name (format: fileSearchStores/{id})

        Returns:
            FileSearchStore information
        """
        response = await self._request("GET", f"/v1beta/{store_name}")
        return FileSearchStore(**response)

    async def delete_store(self, store_name: str, force: bool = False) -> dict[str, Any]:
        """
        Delete a File Search Store.

        Reference: https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.delete

        Args:
            store_name: Store name (format: fileSearchStores/{id})
            force: If true, deletes associated documents

        Returns:
            Empty response on success
        """
        params = {}
        if force:
            params["force"] = "true"

        return await self._request("DELETE", f"/v1beta/{store_name}", params=params)

    # Document Methods

    async def list_documents(
        self, store_name: str, page_size: int = 10, page_token: Optional[str] = None
    ) -> DocumentList:
        """
        List documents in a File Search Store.

        Reference: https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.list

        Args:
            store_name: Store name (format: fileSearchStores/{id})
            page_size: Maximum results per page (default 10, max 20)
            page_token: Token for pagination

        Returns:
            List of Documents with pagination
        """
        params = {"pageSize": min(page_size, 20)}
        if page_token:
            params["pageToken"] = page_token

        response = await self._request("GET", f"/v1beta/{store_name}/documents", params=params)
        return DocumentList(**response)

    async def get_document(self, document_name: str) -> Document:
        """
        Get information about a specific document.

        Reference: https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.get

        Args:
            document_name: Document name (format: fileSearchStores/{id}/documents/{id})

        Returns:
            Document information
        """
        response = await self._request("GET", f"/v1beta/{document_name}")
        return Document(**response)

    async def delete_document(
        self, document_name: str, force: bool = False
    ) -> dict[str, Any]:
        """
        Delete a document from a File Search Store.

        Reference: https://ai.google.dev/api/file-search/documents#method:-filesearchstores.documents.delete

        Args:
            document_name: Document name (format: fileSearchStores/{id}/documents/{id})
            force: If true, deletes associated chunks; if false, returns error if chunks exist

        Returns:
            Empty response on success
        """
        params = {}
        if force:
            params["force"] = "true"

        return await self._request("DELETE", f"/v1beta/{document_name}", params=params)

    # Upload Methods

    async def upload_file_to_files_api(
        self,
        file_path: Path,
        display_name: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Upload a file to the Files API using resumable upload protocol.

        Reference: https://ai.google.dev/api/files

        Args:
            file_path: Path to file to upload
            display_name: Optional display name
            mime_type: Optional MIME type (auto-detected if not provided)

        Returns:
            File resource
        """
        if not file_path.exists():
            raise FileSearchAPIError(f"File not found: {file_path}")

        # Detect MIME type if not provided
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"

        # Read file content
        file_content = file_path.read_bytes()
        file_size = len(file_content)

        upload_url = f"{self.base_url}/upload/v1beta/files"

        @self.retry_decorator
        async def do_resumable_upload() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                # Step 1: Start resumable upload
                metadata = {"file": {}}
                if display_name:
                    metadata["file"]["displayName"] = display_name

                start_headers = {
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-Upload-Protocol": "resumable",
                    "X-Goog-Upload-Command": "start",
                    "X-Goog-Upload-Header-Content-Length": str(file_size),
                    "X-Goog-Upload-Header-Content-Type": mime_type,
                    "Content-Type": "application/json",
                }

                start_response = await client.post(
                    upload_url,
                    headers=start_headers,
                    json=metadata,
                )
                start_response.raise_for_status()

                # Get upload URL from response headers
                upload_uri = start_response.headers.get("X-Goog-Upload-URL")
                if not upload_uri:
                    raise FileSearchAPIError("No upload URL returned from start request")

                # Step 2: Upload file content
                upload_headers = {
                    "X-Goog-Upload-Command": "upload, finalize",
                    "X-Goog-Upload-Offset": "0",
                    "Content-Length": str(file_size),
                }

                upload_response = await client.post(
                    upload_uri,
                    headers=upload_headers,
                    content=file_content,
                )
                upload_response.raise_for_status()

                return upload_response.json()

        try:
            file_resource = await do_resumable_upload()
            file_name = file_resource.get("file", {}).get("name", "unknown")
            logger.info(f"File uploaded to Files API: {file_name}")
            return file_resource
        except httpx.HTTPStatusError as e:
            logger.error(f"File upload failed: {e.response.status_code} - {e.response.text}")
            raise FileSearchAPIError(
                f"File upload error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise FileSearchAPIError(f"File upload failed: {str(e)}")

    async def upload_to_file_search_store(
        self,
        store_name: str,
        file_path: Path,
        display_name: Optional[str] = None,
        custom_metadata: Optional[list[dict[str, Any]]] = None,
        chunking_config: Optional[ChunkingConfig] = None,
        mime_type: Optional[str] = None,
    ) -> Operation:
        """
        Upload a file to a File Search Store using 2-step process.
        Step 1: Upload file to Files API
        Step 2: Import file into File Search Store

        Reference: https://ai.google.dev/gemini-api/docs/file-search

        Args:
            store_name: Store name (format: fileSearchStores/{id})
            file_path: Path to file to upload
            display_name: Optional display name
            custom_metadata: Optional metadata (max 20 per document)
            chunking_config: Optional chunking configuration
            mime_type: Optional MIME type (auto-detected if not provided)

        Returns:
            Operation for tracking upload progress
        """
        try:
            # Step 1: Upload file to Files API
            logger.info(f"Step 1: Uploading {file_path.name} to Files API")
            file_resource = await self.upload_file_to_files_api(
                file_path=file_path,
                display_name=display_name,
                mime_type=mime_type,
            )

            file_name = file_resource.get("file", {}).get("name") if "file" in file_resource else file_resource.get("name")

            if not file_name:
                raise FileSearchAPIError("Failed to get file name from upload response")

            # Step 2: Import file into File Search Store
            logger.info(f"Step 2: Importing file into File Search Store: {store_name}")
            operation = await self.import_file(
                store_name=store_name,
                file_name=file_name,
                custom_metadata=custom_metadata,
                chunking_config=chunking_config,
            )

            logger.info(f"Upload and import successful for {file_path.name}")
            return operation

        except Exception as e:
            logger.error(f"Upload to File Search Store failed: {e}")
            raise

    async def import_file(
        self,
        store_name: str,
        file_name: str,
        custom_metadata: Optional[list[dict[str, Any]]] = None,
        chunking_config: Optional[ChunkingConfig] = None,
    ) -> Operation:
        """
        Import an existing file from the Files service into a File Search Store.

        Reference: https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.importfile

        Args:
            store_name: Store name (format: fileSearchStores/{id})
            file_name: Name of file in Files service
            custom_metadata: Optional metadata
            chunking_config: Optional chunking configuration (currently not supported, uses defaults)

        Returns:
            Operation for tracking import progress
        """
        body: dict[str, Any] = {"fileName": file_name}
        if custom_metadata:
            body["customMetadata"] = custom_metadata

        # Note: Chunking config is currently disabled due to API field name mismatch
        # The API uses default values: max_tokens_per_chunk=200, max_overlap_tokens=20
        # TODO: Determine correct field names from API documentation
        # if chunking_config:
        #     body["chunkingConfig"] = chunking_config.model_dump(by_alias=True)

        response = await self._request("POST", f"/v1beta/{store_name}:importFile", json=body)
        return Operation(**response)

    async def get_operation(self, operation_name: str) -> Operation:
        """
        Get the status of a long-running operation.

        Args:
            operation_name: Operation name

        Returns:
            Operation status
        """
        response = await self._request("GET", f"/v1beta/{operation_name}")
        return Operation(**response)

    # Model Methods

    async def list_models(self) -> list[dict[str, Any]]:
        """
        List available Gemini models that support generateContent.

        Reference: https://ai.google.dev/api/models

        Returns:
            List of available models with their capabilities
        """
        url = f"{self.base_url}/v1beta/models"

        @self.retry_decorator
        async def fetch_models() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={"key": self.api_key},
                )
                response.raise_for_status()
                return response.json()

        try:
            response = await fetch_models()
            models = response.get("models", [])

            # Filter models that support generateContent
            available_models = []
            for model in models:
                methods = model.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    available_models.append({
                        "name": model.get("name", "").replace("models/", ""),
                        "displayName": model.get("displayName", ""),
                        "description": model.get("description", ""),
                        "supportedMethods": methods,
                    })

            logger.info(f"Found {len(available_models)} models supporting generateContent")
            return available_models

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to list models: {e.response.status_code} - {e.response.text}")
            raise FileSearchAPIError(
                f"Failed to list models: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise FileSearchAPIError(f"Failed to list models: {str(e)}")

    # Search Methods

    async def search_with_gemini(
        self,
        query: str,
        store_names: list[str],
        model: str = "gemini-2.5-flash",
        metadata_filter: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Search documents using Gemini's generateContent API with FileSearch tool.

        Reference: https://ai.google.dev/gemini-api/docs/file-search

        Args:
            query: Search query/question
            store_names: List of File Search Store names (format: fileSearchStores/{id})
            model: Gemini model to use (default: gemini-2.5-flash)
            metadata_filter: Optional metadata filter

        Returns:
            Gemini API response with grounding information
        """
        # Build request body
        # Note: REST API uses snake_case based on official curl examples
        request_body: dict[str, Any] = {
            "contents": [{"parts": [{"text": query}]}],
            "tools": [
                {
                    "file_search": {
                        "file_search_store_names": store_names,
                    }
                }
            ],
        }

        # Add metadata filter if provided
        if metadata_filter:
            request_body["tools"][0]["file_search"]["metadata_filter"] = metadata_filter

        # Make request to Gemini API
        url = f"{self.base_url}/v1beta/models/{model}:generateContent"

        # Log request for debugging
        logger.info(f"Gemini API request URL: {url}")
        logger.info(f"Request body:\n{json.dumps(request_body, indent=2)}")

        @self.retry_decorator
        async def generate_content() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                }

                response = await client.post(
                    url,
                    headers=headers,
                    json=request_body,
                )
                response.raise_for_status()
                return response.json()

        try:
            response = await generate_content()
            logger.info(f"Search completed for query: {query[:50]}...")
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"Search failed: {e.response.status_code} - {e.response.text}")
            raise FileSearchAPIError(f"Search error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise FileSearchAPIError(f"Search failed: {str(e)}")
