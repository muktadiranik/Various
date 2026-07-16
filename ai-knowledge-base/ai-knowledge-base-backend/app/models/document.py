from sqlalchemy import Column, String, Text, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Document(Base):
    """Document model for storing knowledge base documents"""

    __tablename__ = "documents"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Document metadata
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Document id={self.id} title={self.title}>"
    

class DocumentChunk(Base):
    """Document chunk model for storing document fragments with embeddings"""

    __tablename__ = "document_chunks"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to parent document
    document_id = Column(String(255), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    # Chunk content and metadata
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in the document

    # Embedding reference (store FAISS index ID separately)
    embedding_id = Column(Integer, nullable=True)  # ID in FAISS index
    embedding_vector = Column(Text, nullable=True)  # Optional: store as JSON string for debugging

    # Relevance score (populated during search)
    score = Column(Float, nullable=True)  # Not stored in database, used for query results

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    # Indexes for performance
    __table_args__ = (
        Index("document_id_chunk_index", "document_id", "chunk_index", unique=True),
        Index("document_id_embedding_id", "document_id", "embedding_id", unique=True),
        Index("document_id_chunk_index_embedding_id", "document_id", "chunk_index", "embedding_id", unique=True),
    )


    def __repr__(self):
        return f"<DocumentChunk id={self.id} document_id={self.document_id} chunk_index={self.chunk_index}>"
