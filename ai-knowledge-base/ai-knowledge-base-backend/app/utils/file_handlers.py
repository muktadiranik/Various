"""File handling utilities for document processing"""

import os
from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks with overlap for context

    Args:
        text: Input text to chunk
        chunk_size: Size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of chunks
    """
    if not text:
        return []
    
    if len(text) < chunk_size:
        return [text]
    
    chunks = []
    start = 0

    while start < len(text):
        # Find the end of chunk
        end = min(start + chunk_size, len(text))

        # If not at the end, try to break at a space or newline
        if end < len(text):
            # Look for a space or newline within the last 50 characters
            for i in range(end - 1, end - 50, -1):
                if i > 0 and text[i] in [' ', '\n', '\r', '\t']:
                    end = i + 1
                    break

        # Add the chunk
        chunks.append(text[start:end].strip())

        # Move start position with overlap
        start = end - overlap if end < len(text) else end

    return chunks


def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename

    Args:
        filename: Input filename

    Returns:
        File extension
    """
    return os.path.splitext(filename)[1].lower()


def is_valid_text_file(filename: str) -> bool:
    """Check if a file is a valid text file

    Args:
        filename: Input filename

    Returns:
        True if file is a valid text file, False otherwise
    """
    valid_extensions = {'.txt', '.md', '.rst', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'}
    return get_file_extension(filename) in valid_extensions