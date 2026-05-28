import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.deps import get_current_user, get_db
from app.main import app
from app.model.user import User


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    user.email = "test@example.com"
    user.name = "Test User"
    user.password_hash = "hashed"
    user.preferences = None
    user.monthly_budget_usd = 2.00
    user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session


@pytest.fixture
async def client(mock_db, mock_user):
    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def unauthed_client(mock_db):
    """Client without auth override - for testing auth endpoints."""

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
