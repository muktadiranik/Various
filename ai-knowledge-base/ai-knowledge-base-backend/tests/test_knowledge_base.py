"""Test script for the knowledge base service"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal, init_database
from app.services.knowledge_base import knowledge_base_service
from app.schemas.document import DocumentCreate


async def test_knowledge_base():
    """Test the knowledge base service"""
    print("\n" + "="*50)
    print("Testing Knowledge Base Service")
    print("="*50)
    
    # Initialize database
    await init_database()
    
    # Test document content
    test_documents = [
        {
            "title": "Introduction to Artificial Intelligence",
            "content": """
            Artificial Intelligence (AI) is the simulation of human intelligence in machines.
            It encompasses various subfields including machine learning, deep learning,
            natural language processing, and computer vision.
            
            Machine learning is a subset of AI that enables systems to learn and improve
            from experience without being explicitly programmed.
            
            Deep learning uses neural networks with multiple layers to progressively
            extract higher-level features from raw input.
            """,
            "source": "AI Textbook"
        },
        {
            "title": "Getting Started with Python",
            "content": """
            Python is a high-level, interpreted programming language known for its
            simplicity and readability. It's widely used in data science, web development,
            and automation.
            
            Key features of Python include dynamic typing, automatic memory management,
            and a large standard library.
            
            Python's popularity in data science is driven by libraries like NumPy,
            Pandas, and Scikit-learn.
            """,
            "source": "Python Documentation"
        },
        {
            "title": "Cloud Computing Basics",
            "content": """
            Cloud computing delivers computing services over the internet, including
            storage, processing, and networking.
            
            The main service models are:
            - Infrastructure as a Service (IaaS)
            - Platform as a Service (PaaS)
            - Software as a Service (SaaS)
            
            Major cloud providers include AWS, Azure, and Google Cloud Platform.
            """,
            "source": "Cloud Computing Guide"
        }
    ]
    
    # Create test documents
    print("\n1. Creating documents:")
    created_docs = []
    async with AsyncSessionLocal() as db:
        for doc_data in test_documents:
            doc_create = DocumentCreate(**doc_data)
            doc = await knowledge_base_service.create_document(db, doc_create)
            created_docs.append(doc)
            print(f"   Created: {doc.title[:30]}... (ID: {doc.id[:8]})")
    
    # List documents
    print("\n2. Listing documents:")
    async with AsyncSessionLocal() as db:
        docs, total = await knowledge_base_service.list_documents(db, 0, 10)
        print(f"   Total documents: {total}")
        for doc in docs:
            print(f"   - {doc.title[:40]} ({doc.created_at.strftime('%Y-%m-%d')})")
    
    # Test search
    print("\n3. Testing search:")
    queries = [
        "What is artificial intelligence?",
        "Python programming language",
        "cloud services",
    ]
    
    for query in queries:
        print(f"\n   Query: '{query}'")
        results = await knowledge_base_service.search(query, top_k=2)
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. Score: {result.score:.3f}")
                print(f"      {result.content[:100]}...")
        else:
            print("   No results found")
    
    # Test search with context
    print("\n4. Testing search with context:")
    async with AsyncSessionLocal() as db:
        query = "machine learning"
        results = await knowledge_base_service.search_with_context(
            db, query, top_k=1, include_full_document=True
        )
        if results:
            result = results[0]
            print(f"   Query: '{query}'")
            print(f"   Score: {result['relevance_score']:.3f}")
            if result.get('document'):
                print(f"   Document: {result['document'].title}")
                print(f"   Full content preview: {result['document'].content[:150]}...")
        else:
            print("   No results found")
    
    # Get statistics
    print("\n5. Statistics:")
    stats = knowledge_base_service.get_stats()
    print(f"   Vector store: {stats['vector_store']['total_vectors']} vectors")
    print(f"   Cache hit rate: {stats['embedding_cache']['hit_rate']:.2%}")
    print(f"   Chunk size: {stats['chunk_size']}")
    
    # Health check
    print("\n6. Health check:")
    health = await knowledge_base_service.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Embedding: {health['embedding']['status']}")
    print(f"   Vector store: {health['vector_store']['status']}")
    
    print("\n✅ All knowledge base tests passed!")


async def main():
    """Run tests"""
    try:
        await test_knowledge_base()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())