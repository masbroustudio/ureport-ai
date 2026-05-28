from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ReportCreate(BaseModel):
    title: str
    template_id: str = "business_report_v1"
    file_ids: list[str] | None = None
    kb_document_ids: list[str] | None = None
    custom_instructions: str | None = None
    conversation_id: str | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    conversation_id: uuid.UUID | None
    title: str
    subtitle: str | None
    author: str | None
    template_id: str
    outline_json: dict | None
    status: str
    progress_pct: int
    error_message: str | None
    pdf_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    progress_pct: int
    template_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutlineUpdate(BaseModel):
    outline_json: dict


class SectionResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    chapter_number: str
    chapter_title: str
    section_order: int
    section_title: str
    content_markdown: str | None
    status: str
    word_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportStartResponse(BaseModel):
    report_id: str
    pdf_path: str | None = None
