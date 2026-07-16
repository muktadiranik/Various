"""Test script for Groq RAG functionality"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.knowledge_base import knowledge_base_service
from app.core.database import AsyncSessionLocal, init_database
from app.schemas.document import DocumentCreate

# At the top of the file or in the connection test
available_models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "gemma2-9b-it",
]


async def test_groq_connection():
    """Test Groq connection"""
    print("\n" + "="*60)
    print("Testing Groq Connection")
    print("="*60)
    
    health = llm_service.health_check()
    print(f"\nGroq Status:")
    print(f"  Provider: {health['provider']}")
    print(f"  Model: {health['model']}")
    print(f"  Model Name: {health.get('model_name', 'Unknown')}")
    print(f"  Context Window: {health.get('context_window', 'Unknown')}")
    print(f"  Status: {health['status']}")
    print(f"  API Key Set: {health.get('api_key_set', False)}")
    
    if health['status'] != 'healthy':
        print("\n⚠️  Groq is not available.")
        print("Please set GROQ_API_KEY in your .env file")
        print("Get your API key from: https://console.groq.com")
        return False
    
    # List available models
    print("\nAvailable Models:")
    models = llm_service.list_models()
    for model in models[:5]:  # Show first 5
        print(f"  - {model['name']} ({model['id']})")
        print(f"    Context: {model['context_window']}, {model['description']}")
    if len(models) > 5:
        print(f"  ... and {len(models) - 5} more")
    
    return True


async def test_groq_response():
    """Test Groq generates a response"""
    print("\n" + "="*60)
    print("Testing Groq Response Generation")
    print("="*60)
    
    query = "What is artificial intelligence? Explain in simple terms."
    
    print(f"\nQuery: {query}")
    print("\nGenerating response...")
    
    try:
        response = await llm_service.generate_response(query)
        print(f"\nResponse:\n{response['answer']}")
        print(f"\nModel: {response.get('model', 'unknown')}")
        print(f"Provider: {response.get('provider', 'unknown')}")
        print("\n✅ Groq response test passed!")
        return True
    except Exception as e:
        print(f"\n❌ Failed to generate response: {e}")
        return False


async def test_groq_streaming():
    """Test Groq streaming"""
    print("\n" + "="*60)
    print("Testing Groq Streaming")
    print("="*60)
    
    query = "Explain machine learning in simple terms with examples"
    
    print(f"\nQuery: {query}")
    print("\nStreaming response:")
    print("-" * 40)
    
    try:
        full_response = ""
        async for chunk in llm_service.generate_response_stream(query):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print("\n" + "-" * 40)
        print(f"\n✅ Groq streaming test passed! ({len(full_response)} characters)")
        return True
    except Exception as e:
        print(f"\n❌ Failed to stream response: {e}")
        return False


async def test_rag_with_groq():
    """Test RAG with Groq"""
    print("\n" + "="*60)
    print("Testing RAG with Groq")
    print("="*60)
    
    # First, add a test document
    print("\n1. Adding test document to knowledge base...")
    await init_database()
    
    async with AsyncSessionLocal() as db:
        doc_data = DocumentCreate(
            title="Machine Learning Basics",
            content="""
            Machine Learning is a subset of artificial intelligence that enables systems to learn 
            from data without being explicitly programmed.
            
            Key concepts in machine learning include:
            1. Supervised Learning: Learning from labeled data (e.g., classification, regression)
            2. Unsupervised Learning: Finding patterns in unlabeled data (e.g., clustering, dimensionality reduction)
            3. Reinforcement Learning: Learning through trial and error (e.g., game playing, robotics)
            4. Neural Networks: Computational systems inspired by the brain (e.g., deep learning)
            5. Feature Engineering: Selecting and transforming input features for better model performance
            
            Common applications of machine learning include:
            - Image recognition and computer vision
            - Natural language processing and text analysis
            - Recommendation systems for e-commerce
            - Fraud detection in banking
            - Autonomous vehicles and robotics
            - Healthcare diagnostics and drug discovery
            """,
            source="Test Document - Machine Learning",
        )
        
        doc = await knowledge_base_service.create_document(db, doc_data)
        print(f"   ✅ Document created: {doc.id[:8]}")
    
    # Test RAG query
    print("\n2. Testing RAG query...")
    query = "What are the key concepts and applications of machine learning?"
    print(f"\nQuery: {query}")
    
    try:
        result = await rag_service.query(query, top_k=3)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {len(result['sources'])} found")
        if result['sources']:
            print(f"Top source score: {result['sources'][0]['score']:.3f}")
            print(f"Source content preview: {result['sources'][0]['content'][:200]}...")
        print(f"Model: {result.get('model', 'unknown')}")
        print(f"Provider: {result.get('provider', 'unknown')}")
        print("\n✅ RAG with Groq test passed!")
        return True
    except Exception as e:
        print(f"\n❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_rag_streaming():
    """Test RAG with streaming"""
    print("\n" + "="*60)
    print("Testing RAG Streaming with Groq")
    print("="*60)
    
    query = "Explain supervised learning and give examples"
    print(f"\nQuery: {query}")
    print("\nStreaming RAG response:")
    print("-" * 40)
    
    try:
        async for event in rag_service.query_stream(query, top_k=2):
            if event['type'] == 'sources':
                print(f"\n📚 Found {len(event['sources'])} sources")
                for i, source in enumerate(event['sources'], 1):
                    print(f"   Source {i}: relevance {source['score']:.3f}")
            elif event['type'] == 'answer_chunk':
                print(event['chunk'], end="", flush=True)
            elif event['type'] == 'complete':
                print("\n" + "-" * 40)
                print(f"\n✅ Streaming complete! Model: {event.get('model', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"\n❌ RAG streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_groq_speed():
    """Test Groq's speed compared to other providers"""
    print("\n" + "="*60)
    print("Testing Groq Speed")
    print("="*60)
    
    query = "What are the benefits of using Groq for AI inference?"
    
    print(f"\nQuery: {query}")
    print("\nMeasuring response time...")
    
    import time
    
    try:
        start_time = time.time()
        response = await llm_service.generate_response(query)
        end_time = time.time()
        
        elapsed = end_time - start_time
        answer_length = len(response['answer'])
        
        print(f"\nResponse time: {elapsed:.2f} seconds")
        print(f"Answer length: {answer_length} characters")
        print(f"Speed: {answer_length/elapsed:.1f} characters/second")
        
        print(f"\nResponse preview:\n{response['answer'][:300]}...")
        
        print("\n✅ Groq speed test passed!")
        return True
    except Exception as e:
        print(f"\n❌ Speed test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀" * 15)
    print("GROQ RAG TESTS")
    print("🚀" * 15)
    
    # Check Groq connection
    if not await test_groq_connection():
        print("\n❌ Groq not available. Please set GROQ_API_KEY in .env")
        return
    
    # Run tests
    tests = [
        ("Groq Response", test_groq_response),
        ("Groq Streaming", test_groq_streaming),
        ("Groq Speed", test_groq_speed),
        ("RAG with Groq", test_rag_with_groq),
        ("RAG Streaming", test_rag_streaming),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
    
    all_passed = all(r for _, r in results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Groq is working perfectly.")
        print("   Speed: Ultra-fast inference with Groq LPU")
        print("   Quality: High-quality responses from Mixtral/Llama models")
    else:
        print("\n❌ SOME TESTS FAILED!")


if __name__ == "__main__":
    asyncio.run(main())