"""Test script for the vector store service"""

import sys
import random
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store
from app.services.embedding import embedding_service


def generate_test_data(num_vectors: int = 10):
    """Generate test vectors and metadata"""
    texts = [
        "Artificial intelligence is transforming the world",
        "Machine learning algorithms learn from data",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing handles text and speech",
        "Computer vision enables machines to see and understand images",
        "Reinforcement learning learns through trial and error",
        "Data science combines statistics and programming",
        "Big data refers to massive datasets",
        "Cloud computing provides scalable computing resources",
        "The future of AI is bright and full of possibilities",
    ]
    
    # Generate embeddings for test texts
    test_texts = texts[:num_vectors]
    embeddings = embedding_service.embed_texts(test_texts)
    
    # Create IDs and metadata
    ids = [f"doc_{i:03d}" for i in range(num_vectors)]
    metadata = [
        {
            "text": text,
            "length": len(text),
            "words": len(text.split()),
        }
        for text in test_texts
    ]
    
    return embeddings, ids, metadata


def test_vector_store():
    """Test the vector store functionality"""
    print("\n" + "="*50)
    print("Testing Vector Store Service")
    print("="*50)
    
    # Test health check
    print("\n1. Health Check:")
    health = vector_store.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Total vectors: {health['total_vectors']}")
    print(f"   Dimension: {health['dimension']}")
    
    # Clear any existing data
    print("\n2. Clearing existing data:")
    vector_store.clear()
    print(f"   Vectors after clear: {vector_store.get_vector_count()}")
    
    # Generate test data
    print("\n3. Generating test data:")
    embeddings, ids, metadata = generate_test_data(10)
    print(f"   Generated {len(embeddings)} vectors")
    print(f"   Embedding dimension: {len(embeddings[0])}")
    
    # Add vectors
    print("\n4. Adding vectors:")
    added = vector_store.add_vectors(embeddings, ids, metadata)
    print(f"   Added {added} vectors")
    print(f"   Total vectors: {vector_store.get_vector_count()}")
    
    # Test search
    print("\n5. Searching vectors:")
    query_text = "What is artificial intelligence?"
    query_vector = embedding_service.embed_text(query_text)
    
    results = vector_store.search(query_vector, top_k=3)
    print(f"   Query: '{query_text}'")
    print(f"   Results: {len(results)}")
    
    for i, (doc_id, score, meta) in enumerate(results, 1):
        text = meta.get('text', 'N/A')[:50]
        print(f"   {i}. ID: {doc_id}, Score: {score:.3f}")
        print(f"      Text: {text}...")
    
    # Test metadata retrieval
    print("\n6. Retrieving metadata:")
    if ids:
        first_id = ids[0]
        meta = vector_store.get_metadata(first_id)
        vector = vector_store.get_vector(first_id)
        print(f"   ID: {first_id}")
        print(f"   Metadata: {meta}")
        print(f"   Vector dimension: {len(vector) if vector else 0}")
    
    # Test deletion
    print("\n7. Deleting vectors:")
    delete_ids = ids[:3] if ids else []
    deleted = vector_store.delete_vectors(delete_ids)
    print(f"   Deleted {deleted} vectors")
    print(f"   Remaining vectors: {vector_store.get_vector_count()}")
    
    # Verify deletion
    if ids:
        remaining_ids = ids[3:] if len(ids) > 3 else []
        print(f"   Remaining IDs: {remaining_ids[:5]}")
    
    # Test stats
    print("\n8. Store statistics:")
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test health check after operations
    print("\n9. Final health check:")
    health = vector_store.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Total vectors: {health['total_vectors']}")
    
    print("\n✅ All vector store tests passed!")


def test_batch_operations():
    """Test batch operations on the vector store"""
    print("\n" + "="*50)
    print("Testing Batch Operations")
    print("="*50)
    
    # Clear existing data
    vector_store.clear()
    
    # Generate more test data
    print("\n1. Generating batch data:")
    num_batches = 3
    batch_size = 5
    
    total_added = 0
    for batch_num in range(num_batches):
        embeddings, ids, metadata = generate_test_data(batch_size)
        
        # Add batch
        added = vector_store.add_vectors(embeddings, ids, metadata)
        total_added += added
        print(f"   Batch {batch_num + 1}: Added {added} vectors")
    
    print(f"   Total added: {total_added}")
    print(f"   Total in store: {vector_store.get_vector_count()}")
    
    # Test search with filter
    print("\n2. Testing filtered search:")
    query_text = "neural networks deep learning"
    query_vector = embedding_service.embed_text(query_text)
    
    # Get some IDs to filter by
    all_ids = list(vector_store.id_to_index.keys())
    filter_ids = all_ids[:10] if len(all_ids) > 10 else all_ids
    
    results = vector_store.search(query_vector, top_k=3, filter_ids=filter_ids)
    print(f"   Query: '{query_text}'")
    print(f"   Results: {len(results)}")
    
    for i, (doc_id, score, meta) in enumerate(results, 1):
        text = meta.get('text', 'N/A')[:50]
        print(f"   {i}. ID: {doc_id}, Score: {score:.3f}")
        print(f"      Text: {text}...")
    
    print("\n✅ Batch operation tests passed!")


def main():
    """Run all tests"""
    try:
        test_vector_store()
        test_batch_operations()
        print("\n" + "="*50)
        print("✅ All vector store tests completed successfully!")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()