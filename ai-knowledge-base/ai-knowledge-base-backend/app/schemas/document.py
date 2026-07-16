"""Document-related Pydantic models for API requests and responses"""


from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentCreate(BaseModel):
    """Model for creating a new document"""

    title: str = Field(..., description="Document title", min_length=1, max_length=255)
    content: str = Field(..., description="Document content", min_length=1)
    source: Optional[str] = Field(..., description="Source of the document (e.g., file name, URL)")


class DocumentUpdate(BaseModel):
    """Model for updating a document"""

    title: Optional[str] = Field(None, description="Document title", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="Document content", min_length=1)
    source: Optional[str] = Field(None, description="Source of the document (e.g., file name, URL)")


class DocumentResponse(BaseModel):
    """Model for document responses"""

    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title", min_length=1, max_length=255)
    content: str = Field(..., description="Document content", min_length=1)
    source: Optional[str] = Field(None, description="Source of the document (e.g., file name, URL)")
    created_at: datetime = Field(..., description="Date and time the document was created")
    updated_at: datetime = Field(..., description="Date and time the document was last updated")


class DocumentChunkResponse(BaseModel):
    """Model for document chunk responses (used in search results)"""

    id: str = Field(..., description="Chunk unique indetifier")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Chunk index in the document")
    score: Optional[float] = Field(..., description="Relevance score from vector search")