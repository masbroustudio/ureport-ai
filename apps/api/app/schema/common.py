from typing import Any

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    next_cursor: str | None = None
    has_more: bool = False
    limit: int = 50


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: PaginationMeta | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
