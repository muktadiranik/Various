"""Test script for file upload functionality"""

from app.schemas.document import DocumentCreate
from app.services.knowledge_base import knowledge_base_service
from app.core.database import AsyncSessionLocal, init_database
from app.services.file_processor import file_processor
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_file_processor():
    """Test the file processor with different file types"""
    print("\n" + "="*60)
    print("Testing File Processor")
    print("="*60)

    # Test text content
    print("\n1. Processing text content:")
    text_content = b"This is a test document.\nIt has multiple lines.\nAnd some content to process."
    text, file_type, metadata = await file_processor.process_file(
        text_content,
        "test.txt"
    )
    print(f"   File type: {file_type}")
    print(f"   Text length: {len(text)}")
    print(f"   Metadata: {metadata}")

    # Test markdown content
    print("\n2. Processing markdown content:")
    md_content = b"""# Test Markdown
        ## Section 1
        This is a **test** markdown document.

        ## Section 2
        - List item 1
        - List item 2
        """
    text, file_type, metadata = await file_processor.process_file(
        md_content,
        "test.md"
    )
    print(f"   File type: {file_type}")
    print(f"   Extracted text length: {len(text)}")
    print(f"   Preview: {text[:100]}...")

    # Test HTML content
    print("\n3. Processing HTML content:")
    html_content = b"""<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<h1>Welcome</h1>
<p>This is a <strong>test</strong> HTML page.</p>
<ul><li>Item 1</li><li>Item 2</li></ul>
</body>
</html>"""
    text, file_type, metadata = await file_processor.process_file(
        html_content,
        "test.html"
    )
    print(f"   File type: {file_type}")
    print(f"   Extracted text: {text[:100]}...")
    print(f"   Metadata: {metadata}")

    # Test JSON content
    print("\n4. Processing JSON content:")
    json_content = b'{"name": "test", "data": [1, 2, 3], "nested": {"key": "value"}}'
    text, file_type, metadata = await file_processor.process_file(
        json_content,
        "test.json"
    )
    print(f"   File type: {file_type}")
    print(f"   Extracted text (first 100 chars): {text[:100]}...")

    # Test CSV content
    print("\n5. Processing CSV content:")
    csv_content = b"Name,Age,City\nAlice,30,NYC\nBob,25,LA\nCharlie,35,SF"
    text, file_type, metadata = await file_processor.process_file(
        csv_content,
        "test.csv"
    )
    print(f"   File type: {file_type}")
    print(f"   Extracted text:\n{text}")

    print("\n✅ File processor tests passed!")


async def test_file_to_knowledge_base():
    """Test uploading files to the knowledge base"""
    print("\n" + "="*60)
    print("Testing File Upload to Knowledge Base")
    print("="*60)

    await init_database()

    # Test documents
    test_files = [
        {
            "filename": "AI_Overview.txt",
            "content": """
            Artificial Intelligence Overview
            
            Artificial Intelligence (AI) is the simulation of human intelligence in machines.
            It encompasses various subfields including:
            - Machine Learning
            - Deep Learning
            - Natural Language Processing
            - Computer Vision
            
            Machine learning algorithms learn from data to make predictions or decisions.
            Deep learning uses neural networks with multiple layers.
            Natural language processing enables machines to understand human language.
            Computer vision allows machines to interpret visual information.
            """
        },
        {
            "filename": "Python_Guide.md",
            "content": """
            # Python Programming Guide
            
            Python is a versatile programming language used in:
            - Web Development
            - Data Science
            - Automation
            - Artificial Intelligence
            
            ## Key Features
            - Easy to learn syntax
            - Dynamic typing
            - Extensive standard library
            - Large ecosystem of packages
            """
        },
    ]

    print("\n1. Processing and uploading files:")
    async with AsyncSessionLocal() as db:
        for file_data in test_files:
            # Process file
            text, file_type, metadata = await file_processor.process_file(
                file_data["content"].encode('utf-8'),
                file_data["filename"]
            )

            # Create document
            doc = DocumentCreate(
                title=file_data["filename"].replace(
                    "_", " ").replace(".txt", "").replace(".md", ""),
                content=text,
                source=f"Test upload: {file_data['filename']}",
            )

            result = await knowledge_base_service.create_document(db, doc)
            print(f"   ✅ Uploaded: {file_data['filename']} -> {result.id[:8]}")

    # Test search after upload
    print("\n2. Testing search after upload:")
    queries = [
        "What is artificial intelligence?",
        "Python programming",
        "machine learning",
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

    print("\n✅ File upload tests passed!")


async def main():
    """Run all tests"""
    try:
        await test_file_processor()
        await test_file_to_knowledge_base()
        print("\n" + "="*60)
        print("🎉 All file upload tests passed!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
