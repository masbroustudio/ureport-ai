from __future__ import annotations

from qdrant_client import QdrantClient, models

from app.rag.embedder import EMBEDDING_DIM
from app.settings import settings

_instance: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _instance
    if _instance is None:
        _instance = VectorStore()
    return _instance


class VectorStore:
    def __init__(self, qdrant_url: str | None = None):
        self._client = QdrantClient(url=qdrant_url or settings.QDRANT_URL)

    def _collection_name(self, user_id: str) -> str:
        return f"kb_{user_id}"

    def ensure_collection(self, user_id: str) -> None:
        """Create collection if it does not exist."""
        collection_name = self._collection_name(user_id)
        collections = self._client.get_collections().collections
        existing_names = [c.name for c in collections]
        if collection_name not in existing_names:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert_chunks(self, user_id: str, chunks: list[dict]) -> None:
        """Upsert points with payload and vectors.

        Each chunk dict should have: point_id, vector, chunk_id, document_id,
        document_name, text, page, section, chunk_index.
        """
        collection_name = self._collection_name(user_id)
        points = []
        for chunk in chunks:
            points.append(
                models.PointStruct(
                    id=chunk["point_id"],
                    vector=chunk["vector"],
                    payload={
                        "chunk_id": chunk["chunk_id"],
                        "document_id": chunk["document_id"],
                        "document_name": chunk["document_name"],
                        "text": chunk["text"],
                        "page": chunk.get("page"),
                        "section": chunk.get("section"),
                        "chunk_index": chunk.get("chunk_index"),
                    },
                )
            )
        self._client.upsert(collection_name=collection_name, points=points)

    def search(
        self,
        user_id: str,
        query_vector: list[float],
        top_k: int = 8,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        """Search for similar vectors with optional document_id filter."""
        collection_name = self._collection_name(user_id)

        query_filter = None
        if document_ids:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchAny(any=document_ids),
                    )
                ]
            )

        results = self._client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "text": point.payload.get("text", "") if point.payload else "",
                "score": point.score,
                "document_name": point.payload.get("document_name", "") if point.payload else "",
                "page": point.payload.get("page") if point.payload else None,
                "section": point.payload.get("section") if point.payload else None,
                "document_id": point.payload.get("document_id", "") if point.payload else "",
                "chunk_index": point.payload.get("chunk_index") if point.payload else None,
            }
            for point in results.points
        ]

    def delete_document(self, user_id: str, document_id: str) -> None:
        """Delete all points matching a document_id."""
        collection_name = self._collection_name(user_id)
        self._client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )
