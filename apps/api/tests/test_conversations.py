import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.model.conversation import Conversation


@pytest.mark.asyncio
async def test_list_conversations_empty(client, mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get("/api/v1/conversations/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_conversations_with_items(client, mock_db):
    conv = MagicMock(spec=Conversation)
    conv.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    conv.title = "Test Conv"
    conv.model_provider = "groq"
    conv.model_name = "llama-3.3-70b-versatile"
    conv.pinned = False
    conv.archived = False
    conv.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    conv.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [conv]
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get("/api/v1/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Conv"


@pytest.mark.asyncio
async def test_create_conversation(client, mock_db):
    mock_db.commit = AsyncMock()

    async def fake_refresh(obj):
        obj.id = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
        obj.title = "New Chat"
        obj.model_provider = "groq"
        obj.model_name = "llama-3.3-70b-versatile"
        obj.pinned = False
        obj.archived = False
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        obj.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)

    response = await client.post(
        "/api/v1/conversations/",
        json={"title": "New Chat", "model": "groq/llama-3.3-70b-versatile"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Chat"
    assert data["model_provider"] == "groq"


@pytest.mark.asyncio
async def test_get_conversation(client, mock_db):
    conv_id = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    conv = MagicMock(spec=Conversation)
    conv.id = conv_id
    conv.title = "My Conv"
    conv.model_provider = "groq"
    conv.model_name = "llama-3.3-70b-versatile"
    conv.pinned = False
    conv.archived = False
    conv.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    conv.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conv
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get(f"/api/v1/conversations/{conv_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "My Conv"


@pytest.mark.asyncio
async def test_get_conversation_not_found(client, mock_db):
    conv_id = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get(f"/api/v1/conversations/{conv_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(client, mock_db):
    conv_id = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
    conv = MagicMock(spec=Conversation)
    conv.id = conv_id

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conv
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    response = await client.delete(f"/api/v1/conversations/{conv_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_post_message_sse(client, mock_db):
    conv_id = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
    conv = MagicMock(spec=Conversation)
    conv.id = conv_id
    conv.model_provider = "groq"
    conv.model_name = "llama-3.3-70b-versatile"

    # First call returns conversation (for ownership check),
    # Second call for history query
    mock_conv_result = MagicMock()
    mock_conv_result.scalar_one_or_none.return_value = conv

    mock_history_result = MagicMock()
    mock_history_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_conv_result, mock_history_result])
    mock_db.commit = AsyncMock()

    async def fake_refresh(obj):
        obj.id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        obj.conversation_id = conv_id
        obj.role = "user"
        obj.content = "Hello"
        obj.status = "done"
        obj.model = None
        obj.tokens_in = None
        obj.tokens_out = None
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)

    # Mock litellm stream
    async def mock_stream(*args, **kwargs):
        yield {"type": "token", "text": "Hello"}
        yield {"type": "token", "text": " world"}
        yield {"type": "done", "usage": {"tokens_in": 10, "tokens_out": 5}}

    with patch(
        "app.router.conversations.stream_chat_completion",
        side_effect=mock_stream,
    ):
        response = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "Hello"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Parse SSE events
    body = response.text
    assert "event: token" in body
    assert "event: done" in body
