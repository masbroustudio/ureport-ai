from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.kb_chunk import KBChunk
from app.model.knowledge_document import KnowledgeDocument
from app.rag.chunker import chunk_text
from app.rag.embedder import embed_texts
from app.rag.loaders import load_docx, load_pdf, load_txt
from app.rag.vector_store import VectorStore


async def ingest_document(
    db: AsyncSession,
    user_id: str,
    document_id: str,
    file_path: str,
    file_type: str,
) -> None:
    """Ingest a document: load, chunk, embed, store vectors and DB records.

    Updates KnowledgeDocument status to 'ready' on success or 'failed' on error.
    """
    try:
        # 1. Load document based on file_type
        if file_type == "pdf":
            pages = load_pdf(file_path)
        elif file_type == "docx":
            pages = load_docx(file_path)
        else:
            pages = load_txt(file_path)

        if not pages:
            raise ValueError("No text content could be extracted from the document")

        # 2. Chunk the text
        chunks = chunk_text(pages)
        if not chunks:
            raise ValueError("Document produced no chunks after processing")

        # 3. Embed all chunks
        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts)

        # 4. Upsert to Qdrant
        vector_store = VectorStore()
        vector_store.ensure_collection(user_id)

        # Get document name for payload
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == uuid.UUID(document_id))
        )
        doc_record = result.scalar_one()

        qdrant_points = []
        chunk_records = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            qdrant_points.append({
                "point_id": point_id,
                "vector": embedding,
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "document_name": doc_record.name,
                "text": chunk.text,
                "page": chunk.page,
                "section": chunk.section,
                "chunk_index": chunk.chunk_index,
            })

            chunk_records.append(KBChunk(
                document_id=uuid.UUID(document_id),
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                page=chunk.page,
                section=chunk.section,
                token_count=chunk.token_count,
                qdrant_point_id=point_id,
            ))

        vector_store.upsert_chunks(user_id, qdrant_points)

        # 5. Save KBChunk records to database
        db.add_all(chunk_records)

        # 6. Update KnowledgeDocument status
        doc_record.status = "ready"
        doc_record.chunk_count = len(chunks)
        await db.commit()

    except Exception as e:
        await db.rollback()
        # Update document status to failed
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == uuid.UUID(document_id))
        )
        doc_record = result.scalar_one_or_none()
        if doc_record:
            doc_record.status = "failed"
            doc_record.error_message = str(e)[:500]
            await db.commit()
