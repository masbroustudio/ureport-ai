from typing import AsyncGenerator

from app.settings import Settings, settings


async def get_db() -> AsyncGenerator:
    # TODO: implement actual database session
    yield None


async def get_current_user() -> dict:
    # TODO: implement JWT verification
    raise NotImplementedError("Auth not implemented yet")


def get_settings() -> Settings:
    return settings
