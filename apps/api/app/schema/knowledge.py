from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    title: str | None
    tags: list[str] | None
    language: str | None
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 8
    document_ids: list[str] | None = None


class KBSearchResult(BaseModel):
    text: str
    score: float
    document_name: str
    page: int | None
    section: str | None
    document_id: str


class KBSearchResponse(BaseModel):
    results: list[KBSearchResult]
    query: str
