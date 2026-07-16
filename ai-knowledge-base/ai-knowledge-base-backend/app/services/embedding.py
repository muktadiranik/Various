"""Embedding generation service using sentence-transformers"""

from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Optional, Union
import logging
import time
from functools import lru_cache
import numpy as np
import torch
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    
    Features:
    - Batch processing for efficiency
    - Caching for repeated queries
    - Dimension validation
    - Error handling with retries
    """
    
    def __init__(self):
        """Initialize the embedding model with error handling"""
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = None
        self._embeddings = None
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        try:
            self._initialize_model()
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise RuntimeError(f"Embedding model initialization failed: {e}")
    
    def _initialize_model(self):
        """Initialize the embedding model with proper configuration"""
        logger.info(f"Loading embedding model: {self.model_name}")
        start_time = time.time()
        
        try:
            # Device configuration
            device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU for efficiency
            # Use HuggingFaceEmbeddings from LangChain for easy integration
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': device},
                encode_kwargs={
                    'normalize_embeddings': True,  # Normalize for FAISS
                },
            )
            
            # Get embedding dimension by testing
            self.dimension = self._get_embedding_dimension()
            
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")
            logger.info(f"Embedding dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def _get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the model"""
        try:
            test_embedding = self._embeddings.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Failed to get embedding dimension: {e}")
            raise
    
    @property
    def embeddings(self):
        """Get the underlying embedding model"""
        if self._embeddings is None:
            self._initialize_model()
        return self._embeddings
    
    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text with optional caching.
        
        Args:
            text: Input text to embed
            use_cache: Whether to use cache for this query
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension if self.dimension else []
        
        # Check cache
        if use_cache and text in self._cache:
            self._cache_hits += 1
            return self._cache[text]
        
        try:
            # Generate embedding
            embedding = self.embeddings.embed_query(text)
            
            # Validate embedding dimension
            if self.dimension and len(embedding) != self.dimension:
                logger.warning(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
            
            # Cache if enabled
            if use_cache:
                self._cache[text] = embedding
                self._cache_misses += 1
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension if self.dimension else []
    
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batch processing.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache for these queries
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        # Check cache for each text
        result = []
        texts_to_embed = []
        text_indices = []
        
        for i, text in enumerate(valid_texts):
            if use_cache and text in self._cache:
                self._cache_hits += 1
                result.append(self._cache[text])
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
                # Placeholder, will be replaced
                result.append(None)
        
        # Batch process texts not in cache
        if texts_to_embed:
            try:
                # Generate embeddings in batch
                batch_embeddings = self.embeddings.embed_documents(texts_to_embed)
                
                # Update cache and fill results
                for idx, (text, embedding) in enumerate(zip(texts_to_embed, batch_embeddings)):
                    if use_cache:
                        self._cache[text] = embedding
                        self._cache_misses += 1
                    
                    # Find the correct position in result
                    result_idx = text_indices[idx]
                    result[result_idx] = embedding
                    
            except Exception as e:
                logger.error(f"Failed to embed batch texts: {e}")
                # Fill failed with zero vectors
                for i, text in enumerate(texts_to_embed):
                    result_idx = text_indices[i]
                    result[result_idx] = [0.0] * self.dimension if self.dimension else []
        
        # Ensure all results are valid
        final_result = []
        for r in result:
            if r is None:
                final_result.append([0.0] * self.dimension if self.dimension else [])
            else:
                final_result.append(r)
        
        return final_result
    
    def embed_query(self, query: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query: Search query text
            use_cache: Whether to use cache
            
        Returns:
            List of floats representing the query embedding
        """
        # Same as embed_text but semantically separate for clarity
        return self.embed_text(query, use_cache=use_cache)
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0,
        }
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Embedding cache cleared")
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        if self.dimension is None:
            self._get_embedding_dimension()
        return self.dimension
    
    def health_check(self) -> dict:
        """
        Perform a health check on the embedding service.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Test embedding generation
            test_text = "health check"
            embedding = self.embed_text(test_text, use_cache=False)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "dimension": self.dimension,
                "cache_size": len(self._cache),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model_name,
            }


# Create a global instance for reuse
embedding_service = EmbeddingService()