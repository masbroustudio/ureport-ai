from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
