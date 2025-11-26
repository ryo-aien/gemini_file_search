"""
Search router for querying documents using Gemini.

Endpoints:
- POST /api/search - Search documents in File Search Stores
- GET /api/models - List available Gemini models
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.deps import SettingsDep
from app.models.schemas import SearchRequest, SearchResult
from app.services.file_search import FileSearchAPIError, FileSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResult)
async def search_documents(
    request: SearchRequest,
    settings: SettingsDep,
) -> SearchResult:
    """
    Search documents using Gemini with FileSearch tool.

    This endpoint uses Gemini's generateContent API with FileSearch tool
    to search across File Search Stores and return AI-generated answers
    with grounding information.

    Args:
        request: Search request with query and store IDs
        settings: Application settings

    Returns:
        Search result with answer and source information

    Raises:
        HTTPException: If search fails
    """
    try:
        service = FileSearchService(settings)

        # Convert store IDs to full store names
        store_names = [f"fileSearchStores/{store_id}" for store_id in request.store_ids]

        logger.info(f"Searching in stores: {store_names}")
        logger.info(f"Query: {request.query}")

        # Call Gemini API with FileSearch tool
        response = await service.search_with_gemini(
            query=request.query,
            store_names=store_names,
            model=request.model,
            metadata_filter=request.metadata_filter,
        )

        # Log response for debugging
        logger.debug(f"Gemini API response: {response}")

        # Extract answer from response
        answer = ""
        grounding_chunks: list[dict[str, Any]] = []
        sources: list[str] = []

        # Check if response has expected structure
        if not isinstance(response, dict):
            logger.error(f"Unexpected response type: {type(response)}")
            raise ValueError(f"Invalid API response type: {type(response)}")

        # Check for API errors in response
        if "error" in response:
            error_info = response["error"]
            error_message = error_info.get("message", "Unknown API error")
            logger.error(f"Gemini API returned error: {error_message}")
            raise FileSearchAPIError(f"Gemini API error: {error_message}")

        # Check if prompt was blocked
        if "promptFeedback" in response:
            feedback = response["promptFeedback"]
            if feedback.get("blockReason"):
                block_reason = feedback["blockReason"]
                logger.error(f"Prompt was blocked: {block_reason}")
                raise ValueError(f"Search query was blocked: {block_reason}")

        if "candidates" in response and len(response["candidates"]) > 0:
            candidate = response["candidates"][0]

            # Extract text answer
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                answer = " ".join([part.get("text", "") for part in parts if "text" in part])

            # Extract grounding metadata
            if "groundingMetadata" in candidate:
                grounding_metadata = candidate["groundingMetadata"]

                # Extract grounding chunks (source documents)
                if "groundingChunks" in grounding_metadata:
                    grounding_chunks = grounding_metadata["groundingChunks"]

                    # Extract unique sources
                    for chunk in grounding_chunks:
                        if "retrievedContext" in chunk:
                            context = chunk["retrievedContext"]
                            if "uri" in context:
                                sources.append(context["uri"])
                            elif "title" in context:
                                sources.append(context["title"])
        else:
            # No candidates in response
            logger.warning(f"No candidates in Gemini API response. Response keys: {response.keys()}")

        # Remove duplicate sources
        sources = list(dict.fromkeys(sources))

        logger.info(f"Search completed. Answer length: {len(answer)}, Sources: {len(sources)}")

        return SearchResult(
            answer=answer or "No answer found.",
            grounding_chunks=grounding_chunks,
            sources=sources,
        )

    except FileSearchAPIError as e:
        error_msg = str(e) if str(e) else "Unknown API error"
        logger.error(f"Search failed: {error_msg}", exc_info=True)

        # Check if it's a quota/rate limit error (429)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail=error_msg
            )

        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = str(e) if str(e) else f"Unexpected error: {type(e).__name__}"
        logger.error(f"Unexpected error during search: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/models")
async def list_models(
    settings: SettingsDep,
) -> list[dict[str, Any]]:
    """
    List available Gemini models that support generateContent.

    Args:
        settings: Application settings

    Returns:
        List of available models

    Raises:
        HTTPException: If listing fails
    """
    try:
        service = FileSearchService(settings)
        models = await service.list_models()
        logger.info(f"Listed {len(models)} available models")
        return models
    except FileSearchAPIError as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
