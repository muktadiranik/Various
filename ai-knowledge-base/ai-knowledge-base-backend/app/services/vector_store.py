"""FAISS vector store service for efficient similarity search"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import logging
import json
from datetime import datetime

from app.core.config import settings
from app.services.embedding import embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for document embeddings.
    
    Features:
    - Persistent storage with FAISS indexes
    - Batch insertion and deletion
    - Similarity search with scores
    - Metadata tracking
    - Index type selection (flat, IVF, HNSW)
    """
    
    def __init__(self, dimension: Optional[int] = None):
        """
        Initialize the vector store.
        
        Args:
            dimension: Embedding dimension (auto-detected if not provided)
        """
        self.dimension = dimension or embedding_service.get_dimension()
        self.index_path = Path(settings.VECTOR_STORE_PATH)
        self.metadata_path = self.index_path / "metadata.json"
        self.index_file = self.index_path / "faiss.index"
        
        # Ensure the directory exists
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index = None
        self.id_to_index = {}  # Maps external IDs to FAISS indices
        self.index_to_id = {}  # Maps FAISS indices to external IDs
        self.metadata = {}  # Additional metadata for each vector
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"Vector store initialized with dimension {self.dimension}")
    
    def _create_index(self, index_type: str = "flat") -> faiss.Index:
        """
        Create a new FAISS index.
        
        Args:
            index_type: Type of index ("flat", "ivf", "hnsw")
            
        Returns:
            FAISS index instance
        """
        if index_type == "flat":
            # Simple flat index (exact search)
            index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            
        elif index_type == "ivf":
            # IVF index for faster search with large datasets
            quantizer = faiss.IndexFlatIP(self.dimension)
            nlist = min(100, max(10, self.get_size() // 10))  # Number of clusters
            index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist, faiss.METRIC_INNER_PRODUCT)
            index.nprobe = 10  # Number of clusters to search
            
        elif index_type == "hnsw":
            # HNSW index for fast approximate search
            index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors
            index.hnsw.efSearch = 64  # Search accuracy
            
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        return index
    
    def _load_index(self) -> bool:
        """
        Load existing FAISS index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.index_file.exists() and self.metadata_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load metadata
                with open(self.metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.id_to_index = metadata.get('id_to_index', {})
                    # Rebuild index_to_id from id_to_index
                    self.index_to_id = {int(v): k for k, v in self.id_to_index.items()}
                    self.metadata = metadata.get('metadata', {})
                
                # Verify index size matches metadata
                if self.index.ntotal != len(self.id_to_index):
                    logger.warning(f"Index size mismatch: FAISS has {self.index.ntotal} vectors, metadata has {len(self.id_to_index)}")
                    # If they don't match, rebuild metadata from index
                    self._rebuild_metadata_from_index()
                
                logger.info(f" Loaded existing index with {self.index.ntotal} vectors")
                return True
            else:
                logger.info("No existing index found, creating new one")
                self.index = self._create_index()
                self.id_to_index = {}
                self.index_to_id = {}
                self.metadata = {}
                return False
                
        except Exception as e:
            logger.error(f" Failed to load index: {e}")
            # Create fresh index
            self.index = self._create_index()
            self.id_to_index = {}
            self.index_to_id = {}
            self.metadata = {}
            return False
    
    def _rebuild_metadata_from_index(self):
        """
        Rebuild metadata from the FAISS index.
        This is a recovery method when metadata is corrupted.
        """
        logger.warning("Rebuilding metadata from FAISS index...")
        # This is a best-effort recovery
        # Since we can't recover IDs from the index, we'll create new ones
        total = self.index.ntotal
        self.id_to_index = {}
        self.index_to_id = {}
        self.metadata = {}
        
        for i in range(total):
            # Generate a temporary ID
            temp_id = f"recovered_{i}"
            self.id_to_index[temp_id] = i
            self.index_to_id[i] = temp_id
            self.metadata[temp_id] = {"recovered": True, "original_index": i}
        
        logger.info(f"Rebuilt metadata for {total} vectors")
        self.save()
    
    def save(self) -> None:
        """
        Save FAISS index and metadata to disk.
        """
        try:
            if self.index is None:
                logger.warning("No index to save")
                return
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            metadata = {
                'id_to_index': self.id_to_index,
                'metadata': self.metadata,
                'dimension': self.dimension,
                'created_at': datetime.now().isoformat(),
                'total_vectors': self.index.ntotal,
            }
            
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Saved index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f" Failed to save index: {e}")
            raise
    
    def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Add vectors to the index.
        
        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs for each vector
            metadata: Optional metadata for each vector
            
        Returns:
            Number of vectors added
        """
        if not vectors or not ids:
            return 0
        
        if len(vectors) != len(ids):
            raise ValueError("Number of vectors and IDs must match")
        
        # Convert to numpy array
        vectors_np = np.array(vectors).astype(np.float32)
        
        # Normalize vectors (cosine similarity)
        faiss.normalize_L2(vectors_np)
        
        # Add to index
        start_idx = self.index.ntotal
        self.index.add(vectors_np)
        
        # Update mappings and metadata
        added_count = 0
        for i, vector_id in enumerate(ids):
            idx = start_idx + i
            self.id_to_index[vector_id] = idx
            self.index_to_id[idx] = vector_id
            
            # Store metadata if provided
            if metadata and i < len(metadata):
                self.metadata[vector_id] = metadata[i]
            else:
                self.metadata[vector_id] = {"index": idx}
            added_count += 1
        
        # Save after adding
        self.save()
        
        logger.info(f"Added {added_count} vectors to index (total: {self.index.ntotal})")
        return added_count
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_ids: Optional[List[str]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            filter_ids: Optional list of IDs to search within
            
        Returns:
            List of (id, score, metadata) tuples
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Convert query to numpy and normalize
        query_np = np.array([query_vector]).astype(np.float32)
        faiss.normalize_L2(query_np)
        
        # If we have filter_ids, we need to handle differently
        if filter_ids:
            # Map filter IDs to indices
            filter_indices = []
            for fid in filter_ids:
                if fid in self.id_to_index:
                    filter_indices.append(self.id_to_index[fid])
            
            if not filter_indices:
                return []
            
            # Create a subset index or search all and filter
            # For simplicity, search all and filter
            all_results = self._search_all(query_np, min(top_k * 2, self.index.ntotal))
            
            # Filter results
            filtered_results = [(id_, score, self.metadata.get(id_, {})) 
                              for id_, score in all_results if id_ in filter_ids]
            
            return filtered_results[:top_k]
        
        # Regular search
        return self._search_all(query_np, top_k)
    
    def _search_all(
        self,
        query_np: np.ndarray,
        top_k: int,
    ) -> List[Tuple[str, float]]:
        """
        Search all vectors in the index.
        
        Args:
            query_np: Normalized query vector
            top_k: Number of results to return
            
        Returns:
            List of (id, score) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Search with FAISS
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_np, k)
        
        # Convert results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # FAISS returns -1 for padding
                continue
            
            # Get ID from mapping
            vector_id = self.index_to_id.get(int(idx))
            if vector_id is None:
                logger.warning(f"Found index {idx} without mapping - attempting recovery")
                # Try to recover by creating a temporary ID
                temp_id = f"recovered_{idx}"
                self.index_to_id[int(idx)] = temp_id
                self.id_to_index[temp_id] = int(idx)
                vector_id = temp_id
            
            # FAISS returns inner product, higher is better for normalized vectors
            score = float(distances[0][i])
            results.append((vector_id, score))
        
        return results
    
    def delete_vectors(self, ids: List[str]) -> int:
        """
        Delete vectors from the index by ID.
        
        Note: FAISS doesn't support direct deletion, so we rebuild the index.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Number of vectors deleted
        """
        if not ids:
            return 0
        
        # Find indices to remove
        indices_to_remove = []
        for vector_id in ids:
            if vector_id in self.id_to_index:
                indices_to_remove.append(self.id_to_index[vector_id])
        
        if not indices_to_remove:
            return 0
        
        # Create new index with remaining vectors
        new_index = self._create_index()
        new_id_to_index = {}
        new_index_to_id = {}
        new_metadata = {}
        
        # Get all vectors from current index
        if self.index.ntotal > 0:
            all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
            
            # Collect vectors to keep
            indices_to_remove_set = set(indices_to_remove)
            keep_indices = [i for i in range(self.index.ntotal) if i not in indices_to_remove_set]
            
            if keep_indices:
                # Keep only vectors not in remove list
                vectors_to_keep = all_vectors[keep_indices]
                new_index.add(vectors_to_keep)
                
                # Update mappings
                for new_idx, old_idx in enumerate(keep_indices):
                    vector_id = self.index_to_id[old_idx]
                    new_id_to_index[vector_id] = new_idx
                    new_index_to_id[new_idx] = vector_id
                    if vector_id in self.metadata:
                        new_metadata[vector_id] = self.metadata[vector_id]
        
        # Replace index
        self.index = new_index
        self.id_to_index = new_id_to_index
        self.index_to_id = new_index_to_id
        self.metadata = new_metadata
        
        # Save after deletion
        self.save()
        
        logger.info(f"Deleted {len(indices_to_remove)} vectors from index")
        return len(indices_to_remove)
    
    def update_vector(
        self,
        vector_id: str,
        new_vector: List[float],
        new_metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a vector in the index.
        
        Args:
            vector_id: ID of vector to update
            new_vector: New embedding vector
            new_metadata: Optional new metadata
            
        Returns:
            True if updated successfully
        """
        if vector_id not in self.id_to_index:
            logger.warning(f"Vector ID {vector_id} not found in index")
            return False
        
        # Delete and re-add
        self.delete_vectors([vector_id])
        self.add_vectors([new_vector], [vector_id], [new_metadata] if new_metadata else None)
        
        return True
    
    def get_vector_count(self) -> int:
        """Get total number of vectors in the index"""
        return self.index.ntotal if self.index else 0
    
    def get_size(self) -> int:
        """Alias for get_vector_count"""
        return self.get_vector_count()
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """
        Retrieve a vector by ID.
        
        Args:
            vector_id: Vector ID to retrieve
            
        Returns:
            Vector as list of floats, or None if not found
        """
        if vector_id not in self.id_to_index:
            return None
        
        idx = self.id_to_index[vector_id]
        if idx >= self.index.ntotal:
            return None
        
        vector = self.index.reconstruct(idx)
        return vector.tolist()
    
    def get_metadata(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a vector"""
        return self.metadata.get(vector_id)
    
    def clear(self) -> None:
        """Clear all vectors from the index"""
        self.index = self._create_index()
        self.id_to_index = {}
        self.index_to_id = {}
        self.metadata = {}
        self.save()
        logger.info("Cleared all vectors from index")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "total_vectors": self.get_vector_count(),
            "dimension": self.dimension,
            "metadata_count": len(self.metadata),
            "mapping_count": len(self.id_to_index),
            "index_type": type(self.index).__name__,
            "index_file": str(self.index_file),
            "metadata_file": str(self.metadata_path),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the vector store"""
        try:
            # Check if index is accessible
            count = self.get_vector_count()
            mapping_count = len(self.id_to_index)
            
            # Check consistency
            is_consistent = (count == mapping_count)
            
            # Try a search with a random vector
            if count > 0:
                test_vector = np.random.randn(self.dimension).astype(np.float32)
                faiss.normalize_L2(test_vector.reshape(1, -1))
                results = self._search_all(test_vector.reshape(1, -1), 1)
            
            status = "healthy" if is_consistent else "degraded"
            
            return {
                "status": status,
                "total_vectors": count,
                "mapping_count": mapping_count,
                "is_consistent": is_consistent,
                "dimension": self.dimension,
                "index_exists": self.index_file.exists(),
                "metadata_exists": self.metadata_path.exists(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "total_vectors": self.get_vector_count(),
            }


# Create a global instance
vector_store = VectorStore()