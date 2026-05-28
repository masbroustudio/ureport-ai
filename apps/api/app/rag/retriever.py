from __future__ import annotations

from dataclasses import dataclass

from app.rag.embedder import embed_query
from app.rag.vector_store import VectorStore


@dataclass
class RetrievalResult:
    text: str
    score: float
    document_name: str
    page: int | None
    section: str | None
    document_id: str


async def retrieve(
    user_id: str,
    query: str,
    top_k: int = 8,
    document_ids: list[str] | None = None,
) -> list[RetrievalResult]:
    """Embed query and search Qdrant for relevant chunks."""
    query_vector = embed_query(query)

    vector_store = VectorStore()
    results = vector_store.search(
        user_id=user_id,
        query_vector=query_vector,
        top_k=top_k,
        document_ids=document_ids,
    )

    return [
        RetrievalResult(
            text=r["text"],
            score=r["score"],
            document_name=r["document_name"],
            page=r["page"],
            section=r["section"],
            document_id=r["document_id"],
        )
        for r in results
    ]
