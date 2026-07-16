"""Knowledge Base Service - Orchestrates document management and search"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
from datetime import datetime
import uuid

from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentChunkResponse
from app.services.embedding import embedding_service
from app.services.chunking import chunking_service
from app.services.vector_store import vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Main service orchestrating all knowledge base operations.
    
    This service coordinates:
    - Database operations (SQLite)
    - Text chunking
    - Embedding generation
    - Vector storage (FAISS)
    - Search and retrieval
    """
    
    def __init__(self):
        """Initialize the knowledge base service"""
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        logger.info("Knowledge Base Service initialized")
    
    async def create_document(
        self,
        db: AsyncSession,
        document_data: DocumentCreate,
    ) -> Document:
        """
        Create a new document and add it to the knowledge base.
        
        Process:
        1. Save document metadata to database
        2. Chunk the document content
        3. Generate embeddings for each chunk
        4. Store chunks in database
        5. Store embeddings in vector store
        
        Args:
            db: Database session
            document_data: Document creation data
            
        Returns:
            Created Document instance
        """
        try:
            # 1. Create document in database
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                title=document_data.title,
                content=document_data.content,
                source=document_data.source,
            )
            db.add(document)
            await db.flush()  # Get the ID without committing
            
            logger.info(f"Created document: {doc_id} - {document_data.title}")
            
            # 2. Chunk the document
            chunks = chunking_service.chunk_document(
                document_data.content,
                strategy="size",
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
            
            if not chunks:
                logger.warning(f"Document {doc_id} produced no chunks")
                return document
            
            logger.info(f"Document {doc_id} split into {len(chunks)} chunks")
            
            # 3. Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = embedding_service.embed_texts(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # 4. Create chunk records and prepare for vector store
            chunk_ids = []
            chunk_metadata = []
            
            for idx, chunk_text in enumerate(chunks):
                # Create chunk record
                chunk_id = str(uuid.uuid4())
                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=doc_id,
                    content=chunk_text,
                    chunk_index=idx,
                )
                db.add(chunk)
                chunk_ids.append(chunk_id)
                
                # Prepare metadata for vector store
                chunk_metadata.append({
                    "document_id": doc_id,
                    "chunk_index": idx,
                    "title": document_data.title,
                    "source": document_data.source or "unknown",
                    "text": chunk_text[:200],  # Store preview
                })
            
            # 5. Store embeddings in vector store
            logger.info(f"Adding {len(embeddings)} vectors to vector store...")
            added_count = vector_store.add_vectors(
                vectors=embeddings,
                ids=chunk_ids,
                metadata=chunk_metadata,
            )
            logger.info(f"Added {added_count} vectors to vector store")
            
            # 6. Update chunks with embedding IDs from vector store
            for idx, chunk_id in enumerate(chunk_ids):
                chunk = await db.get(DocumentChunk, chunk_id)
                if chunk:
                    chunk.embedding_id = idx  # Store index in FAISS
            
            # Commit all changes
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"✅ Document {doc_id} processed successfully with {len(chunks)} chunks")
            return document
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to create document: {e}")
            raise
    
    async def get_document(
        self,
        db: AsyncSession,
        document_id: str,
    ) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            Document instance or None if not found
        """
        try:
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if document:
                logger.debug(f"Retrieved document: {document_id}")
            else:
                logger.warning(f"Document not found: {document_id}")
            
            return document
            
        except Exception as e:
            logger.error(f"❌ Failed to get document {document_id}: {e}")
            raise
    
    async def list_documents(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Document], int]:
        """
        List documents with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (documents list, total count)
        """
        try:
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(Document))
            total = count_result.scalar()
            
            # Get documents with pagination
            result = await db.execute(
                select(Document)
                .order_by(Document.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            documents = result.scalars().all()
            
            logger.debug(f"Listed {len(documents)} documents (total: {total})")
            return documents, total
            
        except Exception as e:
            logger.error(f"❌ Failed to list documents: {e}")
            raise
    
    async def update_document(
        self,
        db: AsyncSession,
        document_id: str,
        document_data: DocumentUpdate,
    ) -> Optional[Document]:
        """
        Update an existing document.
        
        Process:
        1. Retrieve existing document
        2. Update document metadata
        3. If content changed, reprocess chunks and embeddings
        4. Update database and vector store
        
        Args:
            db: Database session
            document_id: Document ID to update
            document_data: Updated document data
            
        Returns:
            Updated Document instance or None if not found
        """
        try:
            # 1. Get existing document
            document = await self.get_document(db, document_id)
            if not document:
                logger.warning(f"Document not found for update: {document_id}")
                return None
            
            # 2. Check if content changed
            content_changed = (
                document_data.content is not None and
                document_data.content != document.content
            )
            
            # 3. Update metadata
            if document_data.title is not None:
                document.title = document_data.title
            if document_data.source is not None:
                document.source = document_data.source
            
            # 4. If content changed, reprocess
            if content_changed:
                logger.info(f"Content changed for document {document_id}, reprocessing...")
                
                # Delete old chunks and vectors
                await self._delete_document_chunks(db, document_id)
                
                # Update content
                document.content = document_data.content
                
                # We need to flush to get the updated document
                await db.flush()
                
                # Process new content
                chunks = chunking_service.chunk_document(
                    document_data.content,
                    strategy="size",
                    chunk_size=self.chunk_size,
                    overlap=self.chunk_overlap,
                )
                
                if chunks:
                    # Generate embeddings
                    embeddings = embedding_service.embed_texts(chunks)
                    
                    # Store new chunks
                    chunk_ids = []
                    for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                        chunk = DocumentChunk(
                            id=str(uuid.uuid4()),
                            document_id=document_id,
                            content=chunk_text,
                            chunk_index=idx,
                            embedding_id=idx,
                        )
                        db.add(chunk)
                        chunk_ids.append(chunk.id)
                    
                    # Update vector store
                    # First, delete old vectors (done in _delete_document_chunks)
                    # Then add new vectors
                    vector_store.add_vectors(
                        vectors=embeddings,
                        ids=chunk_ids,
                        metadata=[{
                            "document_id": document_id,
                            "chunk_index": idx,
                            "title": document.title,
                            "source": document.source or "unknown",
                            "text": chunks[idx][:200],
                        } for idx in range(len(chunks))],
                    )
                    
                    logger.info(f"Document {document_id} reprocessed with {len(chunks)} chunks")
            
            # Commit changes
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"✅ Document {document_id} updated successfully")
            return document
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to update document {document_id}: {e}")
            raise
    
    async def delete_document(
        self,
        db: AsyncSession,
        document_id: str,
    ) -> bool:
        """
        Delete a document and all associated data.
        
        Process:
        1. Delete document chunks from database
        2. Delete embeddings from vector store
        3. Delete document from database
        
        Args:
            db: Database session
            document_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # 1. Get document
            document = await self.get_document(db, document_id)
            if not document:
                logger.warning(f"Document not found for deletion: {document_id}")
                return False
            
            # 2. Delete chunks (cascade will handle in DB, but we need vector store)
            await self._delete_document_chunks(db, document_id)
            
            # 3. Delete document
            await db.delete(document)
            await db.commit()
            
            logger.info(f"✅ Document {document_id} deleted successfully")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to delete document {document_id}: {e}")
            raise
    
    async def _delete_document_chunks(
        self,
        db: AsyncSession,
        document_id: str,
    ) -> None:
        """
        Delete all chunks for a document from database and vector store.
        
        Args:
            db: Database session
            document_id: Document ID
        """
        try:
            # Get chunk IDs
            result = await db.execute(
                select(DocumentChunk.id).where(DocumentChunk.document_id == document_id)
            )
            chunk_ids = [row[0] for row in result.all()]
            
            if chunk_ids:
                # Delete from vector store
                vector_store.delete_vectors(chunk_ids)
                
                # Delete from database (cascade will handle if we delete document)
                # But we can also delete explicitly
                await db.execute(
                    select(DocumentChunk).where(DocumentChunk.document_id == document_id)
                )
            
            logger.debug(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to delete chunks for document {document_id}: {e}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_document_ids: Optional[List[str]] = None,
    ) -> List[DocumentChunkResponse]:
        """
        Search the knowledge base using semantic similarity.
        
        Process:
        1. Generate embedding for the query
        2. Search vector store for similar chunks
        3. Retrieve chunk details from database
        4. Return ranked results with scores
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_document_ids: Optional list of document IDs to search within
            
        Returns:
            List of DocumentChunkResponse objects with scores
        """
        try:
            # 1. Generate query embedding
            logger.info(f"Searching for: '{query}'")
            query_vector = embedding_service.embed_query(query)
            
            # 2. Search vector store
            vector_results = vector_store.search(
                query_vector,
                top_k=top_k,
                filter_ids=filter_document_ids,
            )
            
            if not vector_results:
                logger.info(f"No results found for query: '{query}'")
                return []
            
            logger.info(f"Found {len(vector_results)} vector results")
            
            # 3. Build results - handle both 2-tuple and 3-tuple results
            results = []
            for result in vector_results:
                # Check if result has 2 or 3 elements
                if len(result) == 3:
                    chunk_id, score, metadata = result
                else:
                    chunk_id, score = result
                    metadata = {}
                
                results.append(DocumentChunkResponse(
                    id=chunk_id,
                    document_id=metadata.get("document_id", ""),
                    content=metadata.get("text", ""),
                    chunk_index=metadata.get("chunk_index", 0),
                    score=score,
                ))
            
            logger.info(f"Returning {len(results)} results for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search: {e}")
            raise
    
    async def search_with_context(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = 5,
        include_full_document: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search and return results with full context.
        
        Args:
            db: Database session
            query: Search query
            top_k: Number of results
            include_full_document: Whether to include full document content
            
        Returns:
            List of results with context
        """
        try:
            # 1. Get search results
            chunks = await self.search(query, top_k)
            
            if not chunks:
                return []
            
            # 2. Enrich with document information
            results = []
            for chunk in chunks:
                # Get full document if requested
                document = None
                if include_full_document:
                    document = await self.get_document(db, chunk.document_id)
                
                results.append({
                    "chunk": chunk,
                    "document": document,
                    "relevance_score": chunk.score,
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search with context: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "vector_store": vector_store.get_stats(),
            "embedding_cache": embedding_service.get_cache_stats(),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on all services.
        
        Returns:
            Dictionary with health status
        """
        return {
            "status": "healthy",
            "embedding": embedding_service.health_check(),
            "vector_store": vector_store.health_check(),
        }


# Create a global instance
knowledge_base_service = KnowledgeBaseService()