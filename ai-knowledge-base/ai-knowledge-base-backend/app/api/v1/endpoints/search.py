"""Search endpoints for the knowledge base"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database
from app.schemas.document import DocumentChunkResponse
from app.services.knowledge_base import knowledge_base_service

router = APIRouter()


class SearchQuery(BaseModel):
    """Search query model"""
    query: str
    top_k: int = 5
    filter_document_ids: Optional[List[str]] = None


@router.post("/", response_model=List[DocumentChunkResponse])
async def search_knowledge_base(
    search_query: SearchQuery,
    database: AsyncSession = Depends(get_database),
):
    """
    Search the knowledge base using semantic similarity.
    
    This will:
    1. Generate embedding for the query
    2. Search FAISS for similar document chunks
    3. Return the most relevant chunks with scores
    """
    try:
        results = await knowledge_base_service.search(
            query=search_query.query,
            top_k=search_query.top_k,
            filter_document_ids=search_query.filter_document_ids,
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get("/")
async def search_get(
    q: str = Query(..., description="Search query", min_length=1),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
    include_full: bool = Query(False, description="Include full document content"),
    database: AsyncSession = Depends(get_database),
):
    """
    Search the knowledge base using GET method (simpler for testing).
    """
    try:
        if include_full:
            results = await knowledge_base_service.search_with_context(
                database, q, top_k, include_full_document=True
            )
        else:
            results = await knowledge_base_service.search(database, q, top_k)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )