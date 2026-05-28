from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.model.user import User  # noqa: E402
from app.model.conversation import Conversation  # noqa: E402
from app.model.message import Message  # noqa: E402
from app.model.usage_log import UsageLog  # noqa: E402
from app.model.file import File  # noqa: E402
from app.model.knowledge_document import KnowledgeDocument  # noqa: E402
from app.model.kb_chunk import KBChunk  # noqa: E402

__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "UsageLog",
    "File",
    "KnowledgeDocument",
    "KBChunk",
]
