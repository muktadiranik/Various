"""Direct test of vector store functionality"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store
from app.services.embedding import embedding_service


def test_vector_store_direct():
    """Test vector store directly"""
    print("\n" + "="*50)
    print("Testing Vector Store Directly")
    print("="*50)
    
    # Clear vector store
    print("\n1. Clearing vector store...")
    vector_store.clear()
    print(f"   Vectors after clear: {vector_store.get_vector_count()}")
    
    # Generate test embeddings
    print("\n2. Generating test embeddings...")
    test_texts = [
        "Artificial intelligence is the future",
        "Machine learning is a subset of AI",
        "Python is a programming language",
        "Cloud computing provides scalable resources",
    ]
    embeddings = embedding_service.embed_texts(test_texts)
    print(f"   Generated {len(embeddings)} embeddings")
    print(f"   Embedding dimension: {len(embeddings[0])}")
    
    # Add to vector store
    print("\n3. Adding vectors to store...")
    ids = [f"test_{i}" for i in range(len(test_texts))]
    metadata = [{"text": text, "index": i} for i, text in enumerate(test_texts)]
    
    added = vector_store.add_vectors(embeddings, ids, metadata)
    print(f"   Added {added} vectors")
    print(f"   Total vectors: {vector_store.get_vector_count()}")
    print(f"   Mappings: {len(vector_store.id_to_index)}")
    
    # Test search
    print("\n4. Testing search...")
    query = "What is AI?"
    query_embedding = embedding_service.embed_query(query)
    
    results = vector_store.search(query_embedding, top_k=2)
    print(f"   Query: '{query}'")
    print(f"   Results: {len(results)}")
    
    for i, result in enumerate(results, 1):
        # Each result is a tuple of (id, score, metadata)
        if len(result) == 3:
            doc_id, score, meta = result
            text = meta.get('text', 'N/A')
            print(f"   {i}. ID: {doc_id}, Score: {score:.3f}")
            print(f"      Text: {text}")
        else:
            # Handle the case where metadata might not be included
            doc_id, score = result
            print(f"   {i}. ID: {doc_id}, Score: {score:.3f}")
    
    # Test search with metadata
    print("\n5. Testing search with metadata retrieval...")
    if results:
        doc_id = results[0][0] if results else None
        if doc_id:
            meta = vector_store.get_metadata(doc_id)
            vector = vector_store.get_vector(doc_id)
            print(f"   Document ID: {doc_id}")
            print(f"   Metadata: {meta}")
            print(f"   Vector dimension: {len(vector) if vector else 0}")
    
    # Test stats
    print("\n6. Vector store stats:")
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Direct vector store test passed!")


if __name__ == "__main__":
    test_vector_store_direct()