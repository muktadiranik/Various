"""Test script for the embedding service"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.embedding import embedding_service
from app.services.chunking import chunking_service


def test_embedding_service():
    """Test the embedding service functionality"""
    print("\n" + "="*50)
    print("Testing Embedding Service")
    print("="*50)
    
    # Test health check
    print("\n1. Health Check:")
    health = embedding_service.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Model: {health['model']}")
    print(f"   Dimension: {health['dimension']}")
    print(f"   Cache Size: {health['cache_size']}")
    
    # Test single text embedding
    print("\n2. Single Text Embedding:")
    text = "This is a test sentence for embedding."
    embedding = embedding_service.embed_text(text)
    print(f"   Text: '{text}'")
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    print("\n3. Batch Text Embedding:")
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is transforming the world.",
        "Machine learning algorithms learn from data.",
    ]
    embeddings = embedding_service.embed_texts(texts)
    print(f"   Number of texts: {len(texts)}")
    print(f"   Number of embeddings: {len(embeddings)}")
    for i, emb in enumerate(embeddings):
        print(f"   Text {i+1} dimension: {len(emb)}")
    
    # Test caching
    print("\n4. Cache Test:")
    stats1 = embedding_service.get_cache_stats()
    print(f"   Initial cache size: {stats1['cache_size']}")
    
    # Second call should use cache
    embedding_service.embed_text(text)  # Cache hit
    stats2 = embedding_service.get_cache_stats()
    print(f"   Cache size after second call: {stats2['cache_size']}")
    print(f"   Cache hits: {stats2['cache_hits']}")
    print(f"   Cache misses: {stats2['cache_misses']}")
    print(f"   Hit rate: {stats2['hit_rate']:.2%}")
    
    print("\n✅ All embedding tests passed!")


def test_chunking_service():
    """Test the chunking service functionality"""
    print("\n" + "="*50)
    print("Testing Chunking Service")
    print("="*50)
    
    # Test text
    text = """This is the first paragraph of our test document. It contains multiple sentences. Here's another one!
    
    This is the second paragraph. It has a different topic. We need to ensure chunking works properly.
    
    Finally, this is the third paragraph. It concludes the test document. Goodbye!"""
    
    # Test size-based chunking
    print("\n1. Size-based Chunking:")
    chunks = chunking_service.chunk_by_size(text, chunk_size=50, overlap=10)
    print(f"   Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"   Chunk {i+1}: {chunk[:50]}...")
    
    # Test paragraph-based chunking
    print("\n2. Paragraph-based Chunking:")
    chunks = chunking_service.chunk_by_paragraph(text)
    print(f"   Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"   Chunk {i+1}: {chunk[:50]}...")
    
    # Test sentence-based chunking
    print("\n3. Sentence-based Chunking:")
    chunks = chunking_service.chunk_by_sentence(text, max_sentences=2)
    print(f"   Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"   Chunk {i+1}: {chunk[:50]}...")
    
    # Test document chunking with strategy
    print("\n4. Document Chunking (size strategy):")
    chunks = chunking_service.chunk_document(text, strategy="size", chunk_size=50)
    print(f"   Number of chunks: {len(chunks)}")
    
    print("\n✅ All chunking tests passed!")


def main():
    """Run all tests"""
    try:
        test_embedding_service()
        test_chunking_service()
        print("\n" + "="*50)
        print("✅ All tests completed successfully!")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()