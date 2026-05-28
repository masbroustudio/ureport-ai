import uuid
from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str | None = None
    model: str | None = None


class ConversationUpdate(BaseModel):
    title: str | None = None
    pinned: bool | None = None
    archived: bool | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    model_provider: str | None
    model_name: str | None
    pinned: bool
    archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str
    model: str | None = None
    file_ids: list[str] | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str | None
    model: str | None
    tokens_in: int | None
    tokens_out: int | None
    status: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
