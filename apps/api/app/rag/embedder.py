from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastembed import TextEmbedding

_model: TextEmbedding | None = None

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384


def _get_model() -> TextEmbedding:
    """Lazy singleton: load model on first call."""
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple texts."""
    model = _get_model()
    embeddings = list(model.embed(texts))
    return [emb.tolist() for emb in embeddings]


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    model = _get_model()
    embeddings = list(model.query_embed(query))
    return embeddings[0].tolist()
