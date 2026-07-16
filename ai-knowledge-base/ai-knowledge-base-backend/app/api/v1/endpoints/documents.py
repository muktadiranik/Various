"""Document management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_database
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.schemas.response import APIResponse, PaginatedResponse
from app.services.knowledge_base import knowledge_base_service
from app.services.file_processor import file_processor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    database: AsyncSession = Depends(get_database),
):
    """
    Create a new document and add it to the knowledge base.

    This will:
    1. Store the document in SQLite
    2. Chunk the document content
    3. Generate embeddings for each chunk
    4. Store embeddings in FAISS vector store
    """
    try:
        result = await knowledge_base_service.create_document(database, document)
        return DocumentResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}",
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    title: Optional[str] = None,
    source: Optional[str] = None,
    database: AsyncSession = Depends(get_database),
):
    """
    Upload a file and add it to the knowledge base.

    Supported file types:
    - Text files: .txt, .md
    - Documents: .pdf, .docx
    - Web: .html, .htm
    - Data: .csv, .json, .xml
    - Code: .py, .js

    The file will be automatically processed, chunked, and indexed.
    """
    try:
        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # Process the file
        try:
            extracted_text, file_type, metadata = await file_processor.process_file(
                content,
                file.filename
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Determine title (use provided or fallback to filename)
        document_title = title or metadata.get('title') or file.filename

        # Determine source
        document_source = source or f"File upload: {file.filename}"

        # Create document
        document_data = DocumentCreate(
            title=document_title,
            content=extracted_text,
            source=document_source,
        )

        # Add to knowledge base
        document = await knowledge_base_service.create_document(database, document_data)

        # Add file metadata to response (optional - can be stored separately)
        # For now, we'll just return the document

        logger.info(
            f"✅ File uploaded successfully: {file.filename} -> {document.id}")

        return DocumentResponse.model_validate(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )


@router.post("/upload-multiple", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = FastAPIFile(...),
    database: AsyncSession = Depends(get_database),
):
    """
    Upload multiple files and add them to the knowledge base.

    This endpoint processes each file and creates a separate document for each.
    """
    results = []
    errors = []

    for file in files:
        try:
            # Read file content
            content = await file.read()

            if not content:
                errors.append(f"File {file.filename} is empty")
                continue

            # Process the file
            try:
                extracted_text, file_type, metadata = await file_processor.process_file(
                    content,
                    file.filename
                )
            except ValueError as e:
                errors.append(f"Failed to process {file.filename}: {str(e)}")
                continue

            # Determine title
            document_title = metadata.get('title') or file.filename

            # Create document
            document_data = DocumentCreate(
                title=document_title,
                content=extracted_text,
                source=f"File upload: {file.filename}",
            )

            # Add to knowledge base
            document = await knowledge_base_service.create_document(database, document_data)
            results.append(document)

            logger.info(f"✅ File uploaded: {file.filename} -> {document.id}")

        except Exception as e:
            errors.append(f"Failed to process {file.filename}: {str(e)}")
            logger.error(f"❌ Failed to upload {file.filename}: {e}")

    # Return results (even if some failed)
    return [DocumentResponse.model_validate(doc) for doc in results]


@router.get("/", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum records to return"),
    database: AsyncSession = Depends(get_database),
):
    """
    List all documents with pagination.
    """
    try:
        documents, total = await knowledge_base_service.list_documents(database, skip, limit)

        # Calculate total pages
        total_pages = (total + limit - 1) // limit if total > 0 else 0

        return PaginatedResponse(
            items=[DocumentResponse.model_validate(doc) for doc in documents],
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    database: AsyncSession = Depends(get_database),
):
    """
    Get a specific document by ID.
    """
    document = await knowledge_base_service.get_document(database, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    return DocumentResponse.model_validate(document)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    database: AsyncSession = Depends(get_database),
):
    """
    Update an existing document.

    If content is updated, the document will be reprocessed:
    - Old chunks and embeddings will be deleted
    - New chunks and embeddings will be generated
    """
    document = await knowledge_base_service.update_document(
        database, document_id, document_update
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    database: AsyncSession = Depends(get_database),
):
    """
    Delete a document and its associated chunks and embeddings.
    """
    deleted = await knowledge_base_service.delete_document(database, document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    return None
