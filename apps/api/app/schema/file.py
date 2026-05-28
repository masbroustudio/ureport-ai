import uuid
from datetime import datetime

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    conversation_id: uuid.UUID | None
    name: str
    mime: str
    size_bytes: int
    kind: str
    status: str
    profile_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FilePreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict]
    total_rows: int
