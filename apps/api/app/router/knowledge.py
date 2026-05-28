import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.model.kb_chunk import KBChunk
from app.model.knowledge_document import KnowledgeDocument
from app.model.user import User
from app.rag.ingest import ingest_document
from app.rag.retriever import retrieve
from app.rag.vector_store import VectorStore
from app.schema.knowledge import (
    KBSearchRequest,
    KBSearchResponse,
    KBSearchResult,
    KnowledgeDocumentResponse,
)
from app.service.files import save_upload_file
from app.settings import settings

router = APIRouter(prefix="/kb", tags=["knowledge"])

ALLOWED_KB_MIMES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


@router.post(
    "/documents",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile,
    title: str | None = Form(None),
    tags: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mime = file.content_type or ""
    if mime not in ALLOWED_KB_MIMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime}. Allowed: PDF, DOCX, TXT.",
        )

    file_type = ALLOWED_KB_MIMES[mime]

    # Save file to storage
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    try:
        storage_path, size_bytes = await save_upload_file(
            file, current_user.id, settings, max_size_bytes=max_bytes
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # Parse tags
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Create KnowledgeDocument record
    doc = KnowledgeDocument(
        user_id=current_user.id,
        name=file.filename or "upload",
        title=title,
        tags=tag_list,
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Run ingestion synchronously
    full_path = f"{settings.FILE_STORAGE_PATH}/{storage_path}"
    await ingest_document(
        db=db,
        user_id=str(current_user.id),
        document_id=str(doc.id),
        file_path=full_path,
        file_type=file_type,
    )

    # Refresh to get updated status
    await db.refresh(doc)
    return KnowledgeDocumentResponse.model_validate(doc)


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.user_id == current_user.id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    docs = result.scalars().all()
    return [KnowledgeDocumentResponse.model_validate(d) for d in docs]


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return KnowledgeDocumentResponse.model_validate(doc)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Delete vectors from Qdrant
    try:
        vector_store = VectorStore()
        vector_store.delete_document(str(current_user.id), str(document_id))
    except Exception:
        pass  # Qdrant may not be available

    # Delete chunks from DB
    chunk_result = await db.execute(
        select(KBChunk).where(KBChunk.document_id == document_id)
    )
    chunks = chunk_result.scalars().all()
    for chunk in chunks:
        await db.delete(chunk)

    # Delete document
    await db.delete(doc)
    await db.commit()


@router.post("/search", response_model=KBSearchResponse)
async def search_knowledge(
    request: KBSearchRequest,
    current_user: User = Depends(get_current_user),
):
    results = await retrieve(
        user_id=str(current_user.id),
        query=request.query,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )

    return KBSearchResponse(
        results=[
            KBSearchResult(
                text=r.text,
                score=r.score,
                document_name=r.document_name,
                page=r.page,
                section=r.section,
                document_id=r.document_id,
            )
            for r in results
        ],
        query=request.query,
    )
