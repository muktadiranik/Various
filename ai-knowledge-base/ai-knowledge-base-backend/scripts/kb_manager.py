"""Knowledge Base Management CLI Tool"""

import asyncio
import sys
from pathlib import Path
import argparse
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.services.knowledge_base import knowledge_base_service
from app.services.vector_store import vector_store
from app.services.embedding import embedding_service
from app.schemas.document import DocumentCreate


async def add_document_async(
    title: str,
    content: str,
    source: Optional[str] = None,
):
    """Add a document asynchronously"""
    async with AsyncSessionLocal() as db:
        try:
            doc_data = DocumentCreate(
                title=title,
                content=content,
                source=source,
            )
            document = await knowledge_base_service.create_document(db, doc_data)
            print(f"\n Document created: {document.id}")
            print(f"   Title: {document.title}")
            print(f"   Source: {document.source or 'N/A'}")
            return document
        except Exception as e:
            print(f"Failed to create document: {e}")
            return None


async def list_documents_async(limit: int = 10):
    """List documents asynchronously"""
    async with AsyncSessionLocal() as db:
        try:
            documents, total = await knowledge_base_service.list_documents(db, 0, limit)
            print(f"\n Documents (showing {len(documents)} of {total}):")
            print("-" * 60)
            for doc in documents:
                print(f"  {doc.id[:8]}... | {doc.title[:40]} | {doc.created_at.strftime('%Y-%m-%d')}")
                print(f"    Source: {doc.source or 'N/A'}")
                print(f"    Chunks: {len(doc.chunks) if doc.chunks else 0}")
                print("-" * 60)
            return documents
        except Exception as e:
            print(f"Failed to list documents: {e}")
            return []


async def search_async(query: str, top_k: int = 5):
    """Search knowledge base asynchronously"""
    try:
        results = await knowledge_base_service.search(query, top_k)
        print(f"\n🔍 Search Results for: '{query}'")
        print("=" * 60)
        if not results:
            print("No results found")
            return []
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result.score:.3f}")
            print(f"   Document: {result.document_id[:8]}...")
            print(f"   Content: {result.content[:150]}...")
            print("-" * 60)
        return results
    except Exception as e:
        print(f"Failed to search: {e}")
        return []


async def stats_async():
    """Show knowledge base statistics"""
    print("\n Knowledge Base Statistics:")
    print("=" * 40)
    
    stats = knowledge_base_service.get_stats()
    
    print("\nVector Store:")
    for key, value in stats['vector_store'].items():
        print(f"  {key}: {value}")
    
    print("\nEmbedding Cache:")
    for key, value in stats['embedding_cache'].items():
        print(f"  {key}: {value}")
    
    print(f"\nChunking:")
    print(f"  Chunk Size: {stats['chunk_size']}")
    print(f"  Chunk Overlap: {stats['chunk_overlap']}")


async def health_async():
    """Run health check"""
    health = await knowledge_base_service.health_check()
    print("\n Health Check:")
    print("=" * 40)
    print(f"Overall Status: {health['status']}")
    
    print("\nEmbedding Service:")
    for key, value in health['embedding'].items():
        print(f"  {key}: {value}")
    
    print("\nVector Store:")
    for key, value in health['vector_store'].items():
        print(f"  {key}: {value}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Knowledge Base Management Tool")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add document
    add_parser = subparsers.add_parser('add', help='Add a document')
    add_parser.add_argument('--title', required=True, help='Document title')
    add_parser.add_argument('--content', required=True, help='Document content')
    add_parser.add_argument('--source', help='Document source')
    
    # List documents
    list_parser = subparsers.add_parser('list', help='List documents')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of documents to list')
    
    # Search
    search_parser = subparsers.add_parser('search', help='Search knowledge base')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    
    # Stats
    subparsers.add_parser('stats', help='Show statistics')
    
    # Health
    subparsers.add_parser('health', help='Run health check')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        asyncio.run(add_document_async(args.title, args.content, args.source))
    elif args.command == 'list':
        asyncio.run(list_documents_async(args.limit))
    elif args.command == 'search':
        asyncio.run(search_async(args.query, args.top_k))
    elif args.command == 'stats':
        asyncio.run(stats_async())
    elif args.command == 'health':
        asyncio.run(health_async())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()