"""RAG (Retrieval-Augmented Generation) Service with Ollama"""

import logging
from typing import List, Dict, Any, Optional, AsyncGenerator

from app.services.knowledge_base import knowledge_base_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG Service for combining retrieval and generation using GROQ.
    
    Features:
    - Retrieve relevant documents from knowledge base
    - Generate responses using Ollama LLM
    - Stream responses
    - Track sources
    - Local, free inference
    """
    
    def __init__(
        self,
        top_k: int = 5,
        include_sources: bool = True,
    ):
        """
        Initialize the RAG service.
        
        Args:
            top_k: Number of documents to retrieve
            include_sources: Whether to include sources in response
        """
        self.top_k = top_k
        self.include_sources = include_sources
        logger.info(f"RAG Service initialized with top_k={top_k}")
    
    async def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_document_ids: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filter_document_ids: Filter search to specific documents
            system_prompt: Custom system prompt
            stream: Whether to stream (ignored for this method)
            
        Returns:
            Response with answer and sources
        """
        try:
            # 1. Retrieve relevant documents
            k = top_k or self.top_k
            search_results = await knowledge_base_service.search(
                query=query,
                top_k=k,
                filter_document_ids=filter_document_ids,
            )
            
            # 2. Prepare context
            context = []
            for result in search_results:
                context.append({
                    "content": result.content,
                    "score": result.score,
                    "document_id": result.document_id,
                    "chunk_id": result.id,
                })
            
            # 3. Generate response using GROQ
            response = await llm_service.generate_response(
                query=query,
                context=context if context else None,
                system_prompt=system_prompt,
                stream=False,
            )
            
            # 4. Format response
            result = {
                "answer": response["answer"],
                "sources": response["sources"] if self.include_sources else [],
                "query": query,
                "model": response.get("model", "ollama"),
            }
            
            # Add search metadata
            if context:
                result["retrieval"] = {
                    "num_documents": len(context),
                    "top_score": context[0]["score"] if context else 0,
                }
            else:
                result["retrieval"] = {
                    "num_documents": 0,
                    "top_score": 0,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise
    
    async def query_stream(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_document_ids: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Query the RAG system with streaming.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filter_document_ids: Filter search to specific documents
            system_prompt: Custom system prompt
            
        Yields:
            Stream events with answer chunks and sources
        """
        try:
            # 1. Retrieve relevant documents
            k = top_k or self.top_k
            search_results = await knowledge_base_service.search(
                query=query,
                top_k=k,
                filter_document_ids=filter_document_ids,
            )
            
            # 2. Prepare context
            context = []
            for result in search_results:
                context.append({
                    "content": result.content,
                    "score": result.score,
                    "document_id": result.document_id,
                    "chunk_id": result.id,
                })
            
            # 3. Send sources first (if enabled)
            if self.include_sources and context:
                yield {
                    "type": "sources",
                    "sources": [
                        {
                            "content": item["content"][:200] + "...",  # Truncate for display
                            "score": item["score"],
                            "document_id": item["document_id"],
                        }
                        for item in context
                    ],
                }
            
            # 4. Stream the response from Ollama
            answer_chunks = []
            async for chunk in llm_service.generate_response_stream(
                query=query,
                context=context if context else None,
                system_prompt=system_prompt,
            ):
                answer_chunks.append(chunk)
                yield {
                    "type": "answer_chunk",
                    "chunk": chunk,
                }
            
            # 5. Send completion event
            yield {
                "type": "complete",
                "full_answer": "".join(answer_chunks),
                "sources": context if self.include_sources else [],
                "model": llm_service.model,
            }
            
        except Exception as e:
            logger.error(f"RAG streaming query failed: {e}")
            yield {
                "type": "error",
                "error": str(e),
            }
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        top_k: Optional[int] = None,
        filter_document_ids: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chat with the RAG system using conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            top_k: Number of documents to retrieve
            filter_document_ids: Filter search to specific documents
            system_prompt: Custom system prompt
            
        Returns:
            Response with answer and sources
        """
        try:
            # Get the last user message
            user_messages = [m for m in messages if m.get("role") == "user"]
            if not user_messages:
                raise ValueError("No user message found")
            
            query = user_messages[-1]["content"]
            
            # Retrieve documents
            k = top_k or self.top_k
            search_results = await knowledge_base_service.search(
                query=query,
                top_k=k,
                filter_document_ids=filter_document_ids,
            )
            
            # Prepare context
            context = []
            for result in search_results:
                context.append({
                    "content": result.content,
                    "score": result.score,
                    "document_id": result.document_id,
                })
            
            # Generate response with conversation context
            response = await llm_service.generate_response(
                query=query,
                context=context if context else None,
                system_prompt=system_prompt,
                stream=False,
            )
            
            return {
                "answer": response["answer"],
                "sources": response["sources"] if self.include_sources else [],
                "query": query,
                "model": response.get("model", "ollama"),
            }
            
        except Exception as e:
            logger.error(f"RAG chat failed: {e}")
            raise


# Create a global instance
rag_service = RAGService()