"""Text chunking service for document processing"""

from typing import List, Optional
import re
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service for splitting text into chunks for embedding and retrieval.
    
    Features:
    - Multiple chunking strategies
    - Smart splitting on sentence boundaries
    - Overlap for context preservation
    """
    
    def __init__(self):
        """Initialize chunking service with settings"""
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        
        # Sentence boundary patterns
        self.sentence_pattern = re.compile(r'(?<=[.!?])\s+')
        self.paragraph_pattern = re.compile(r'\n\s*\n')
    
    def chunk_by_size(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None,
        preserve_sentences: bool = True,
    ) -> List[str]:
        """
        Split text into chunks by size with overlap.
        
        Args:
            text: Input text to split
            chunk_size: Maximum size of each chunk (default: from settings)
            overlap: Number of characters to overlap (default: from settings)
            preserve_sentences: Try to preserve sentence boundaries
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        # If text is short enough, return as single chunk
        if len(text) <= chunk_size:
            return [text.strip()]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Determine end position
            end = min(start + chunk_size, len(text))
            
            if preserve_sentences and end < len(text):
                # Try to break at sentence boundary
                end = self._find_sentence_boundary(text, end)
            
            # Add the chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            if end >= len(text):
                break
            
            next_start = max(start + chunk_size - overlap, end - overlap)

            # Ensure forward progress
            if next_start <= start:
                next_start = start + chunk_size

            start = next_start
        
        return chunks
    
    def chunk_by_paragraph(
        self,
        text: str,
        max_chunk_size: Optional[int] = None,
    ) -> List[str]:
        """
        Split text by paragraphs, optionally merging small paragraphs.
        
        Args:
            text: Input text to split
            max_chunk_size: Maximum size before splitting further
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        max_chunk_size = max_chunk_size or self.chunk_size
        
        # Split by paragraphs
        paragraphs = self.paragraph_pattern.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return []
        
        # Merge small paragraphs
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # If a single paragraph is too large, split it further
            if para_size > max_chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Split the large paragraph by size
                sub_chunks = self.chunk_by_size(
                    para,
                    chunk_size=max_chunk_size,
                    preserve_sentences=True,
                )
                chunks.extend(sub_chunks)
                continue
            
            # Check if adding this paragraph exceeds max size
            if current_size + para_size + 2 > max_chunk_size:  # +2 for newline
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size + 2  # +2 for newline
        
        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def chunk_by_sentence(
        self,
        text: str,
        max_sentences: int = 5,
        overlap_sentences: int = 1,
    ) -> List[str]:
        """
        Split text by sentences with sliding window.
        
        Args:
            text: Input text to split
            max_sentences: Maximum sentences per chunk
            overlap_sentences: Number of overlapping sentences
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Split into sentences
        sentences = self.sentence_pattern.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        if len(sentences) <= max_sentences:
            return [" ".join(sentences)]
        
        # Create sliding window chunks
        chunks = []
        step = max_sentences - overlap_sentences
        
        for i in range(0, len(sentences), step):
            end = min(i + max_sentences, len(sentences))
            chunk_sentences = sentences[i:end]
            chunks.append(" ".join(chunk_sentences))
            
            if end >= len(sentences):
                break
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, position: int) -> int:
        """
        Find the nearest sentence boundary near the given position.
        
        Args:
            text: The full text
            position: Target position
            
        Returns:
            Position of sentence boundary
        """
        # Look for sentence-ending punctuation in the last 50 characters
        search_start = max(0, position - 50)
        search_text = text[search_start:position]
        
        # Find last sentence boundary
        sentence_endings = ['.', '!', '?']
        last_boundary = -1
        
        for i, char in enumerate(search_text):
            if char in sentence_endings:
                # Check if it's actually a sentence ending
                if i + 1 < len(search_text) and search_text[i + 1] == ' ':
                    last_boundary = i + 1
        
        if last_boundary != -1:
            return search_start + last_boundary
        
        # If no sentence boundary found, try to break at a space
        last_space = text.rfind(' ', search_start, position)
        if last_space != -1:
            return last_space + 1
        
        # If still no boundary found, break at the original position
        return position
    
    def chunk_document(
        self,
        text: str,
        strategy: str = "size",
        **kwargs,
    ) -> List[str]:
        """
        Chunk a document using the specified strategy.
        
        Args:
            text: Document text to chunk
            strategy: "size", "paragraph", or "sentence"
            **kwargs: Additional arguments for specific strategies
            
        Returns:
            List of text chunks
        """
        strategies = {
            "size": self.chunk_by_size,
            "paragraph": self.chunk_by_paragraph,
            "sentence": self.chunk_by_sentence,
        }

        if strategy not in strategies:
            logger.warning(f"Unknown chunking strategy: {strategy}, using 'size'")
            strategy = "size"
        
        chunk_method = strategies[strategy]
        chunks = chunk_method(text, **kwargs)
        
        logger.info(f"Chunked document into {len(chunks)} chunks using '{strategy}' strategy")
        return chunks


# Create a global instance
chunking_service = ChunkingService()