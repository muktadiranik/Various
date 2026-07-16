"""Vector store management CLI tool"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store
from app.services.embedding import embedding_service
import argparse


def show_stats():
    """Show vector store statistics"""
    stats = vector_store.get_stats()
    print("\n📊 Vector Store Statistics:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Dimension: {stats['dimension']}")
    print(f"   Index type: {stats['index_type']}")
    print(f"   Metadata count: {stats['metadata_count']}")
    print(f"   Index file: {stats['index_file']}")
    print(f"   Metadata file: {stats['metadata_file']}")


def clear_store(confirm: bool = False):
    """Clear all vectors from the store"""
    if not confirm:
        response = input("⚠️  Are you sure you want to clear all vectors? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled")
            return
    
    vector_store.clear()
    print("✅ Vector store cleared successfully")


def health_check():
    """Run health check"""
    health = vector_store.health_check()
    print("\n🏥 Vector Store Health Check:")
    print(f"   Status: {health['status']}")
    if health['status'] == 'unhealthy':
        print(f"   Error: {health.get('error', 'Unknown error')}")
    print(f"   Total vectors: {health.get('total_vectors', 0)}")
    print(f"   Dimension: {health.get('dimension', 'N/A')}")
    print(f"   Index exists: {health.get('index_exists', False)}")
    print(f"   Metadata exists: {health.get('metadata_exists', False)}")


def test_search(query: str = "artificial intelligence", top_k: int = 5):
    """Test search functionality"""
    print(f"\n🔍 Searching for: '{query}'")
    
    # Generate query embedding
    query_vector = embedding_service.embed_text(query)
    
    # Search
    results = vector_store.search(query_vector, top_k=top_k)
    
    if not results:
        print("   No results found")
        return
    
    print(f"   Found {len(results)} results:")
    for i, (doc_id, score, meta) in enumerate(results, 1):
        text = meta.get('text', 'N/A')[:50]
        print(f"   {i}. ID: {doc_id}, Score: {score:.3f}")
        print(f"      Text: {text}...")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Vector Store Management Tool")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Stats command
    subparsers.add_parser('stats', help='Show vector store statistics')
    
    # Health check command
    subparsers.add_parser('health', help='Run health check')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all vectors')
    clear_parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Test search')
    search_parser.add_argument('--query', default='artificial intelligence', help='Search query')
    search_parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        show_stats()
    elif args.command == 'health':
        health_check()
    elif args.command == 'clear':
        clear_store(args.yes)
    elif args.command == 'search':
        test_search(args.query, args.top_k)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()