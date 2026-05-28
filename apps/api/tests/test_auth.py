import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.deps import get_db
from app.main import app
from app.model.user import User
from app.service.auth import hash_password


@pytest.mark.asyncio
async def test_signup_success(mock_db):
    # Mock: no existing user found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Mock refresh to set attributes on the user
    async def fake_refresh(obj):
        obj.id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        obj.email = "new@example.com"
        obj.name = "New User"
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        obj.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signup",
            json={
                "name": "New User",
                "email": "new@example.com",
                "password": "securepass123",
                "password_confirmation": "securepass123",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_signup_email_taken(mock_db):
    # Mock: existing user found
    existing_user = MagicMock(spec=User)
    existing_user.email = "taken@example.com"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signup",
            json={
                "name": "User",
                "email": "taken@example.com",
                "password": "securepass123",
                "password_confirmation": "securepass123",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_signin_success(mock_db):
    # Create a real password hash
    password_hash = hash_password("securepass123")

    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mock_user.email = "user@example.com"
    mock_user.name = "Test User"
    mock_user.password_hash = password_hash
    mock_user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_user.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signin",
            json={
                "email": "user@example.com",
                "password": "securepass123",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_signin_invalid_password(mock_db):
    password_hash = hash_password("correctpassword")

    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mock_user.email = "user@example.com"
    mock_user.name = "Test User"
    mock_user.password_hash = password_hash
    mock_user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signin",
            json={
                "email": "user@example.com",
                "password": "wrongpassword",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint(client, mock_user):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
