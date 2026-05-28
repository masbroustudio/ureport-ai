import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.model.conversation import Conversation
from app.model.message import Message


@pytest.fixture
def mock_conversation():
    conv = MagicMock(spec=Conversation)
    conv.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    conv.user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    conv.title = "Test Conversation"
    conv.model_provider = "groq"
    conv.model_name = "llama-3.3-70b-versatile"
    conv.pinned = False
    conv.archived = False
    conv.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    conv.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return conv


@pytest.fixture
def mock_user_message():
    msg = MagicMock(spec=Message)
    msg.id = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    msg.conversation_id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    msg.role = "user"
    msg.content = "What is AI?"
    msg.status = "done"
    msg.model = None
    msg.tokens_in = None
    msg.tokens_out = None
    msg.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return msg


@pytest.mark.asyncio
class TestRagChat:
    @patch("app.router.conversations.retrieve", new_callable=AsyncMock)
    @patch("app.router.conversations.stream_chat_completion")
    async def test_message_with_kb_document_ids_includes_rag_context(
        self, mock_stream, mock_retrieve, client, mock_db,
        mock_conversation, mock_user_message
    ):
        """When kb_document_ids are provided, RAG context is injected into the LLM messages."""
        # Setup retriever mock
        rag_result = MagicMock()
        rag_result.text = "AI is artificial intelligence."
        rag_result.score = 0.92
        rag_result.document_name = "ai_intro.pdf"
        rag_result.page = 3
        rag_result.section = None
        rag_result.document_id = "doc-abc"
        mock_retrieve.return_value = [rag_result]

        # Setup streaming mock
        async def fake_stream(messages, model, settings):
            # Verify RAG context is in the system message
            system_msgs = [m for m in messages if m["role"] == "system"]
            assert len(system_msgs) > 0
            assert "knowledge base context" in system_msgs[0]["content"]
            assert "ai_intro.pdf" in system_msgs[0]["content"]
            yield {"type": "token", "text": "AI stands for"}
            yield {"type": "token", "text": " artificial intelligence."}
            yield {"type": "done", "usage": {"tokens_in": 10, "tokens_out": 5}}

        mock_stream.side_effect = fake_stream

        # Mock DB calls
        conv_result = MagicMock()
        conv_result.scalar_one_or_none.return_value = mock_conversation

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = [mock_user_message]

        mock_db.execute = AsyncMock(side_effect=[conv_result, history_result])
        mock_db.commit = AsyncMock()

        async def fake_refresh(obj):
            obj.id = uuid.uuid4()
            obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            f"/api/v1/conversations/{mock_conversation.id}/messages",
            json={
                "content": "What is AI?",
                "kb_document_ids": ["doc-abc"],
            },
        )

        assert response.status_code == 200
        mock_retrieve.assert_called_once()
        call_kwargs = mock_retrieve.call_args.kwargs
        assert call_kwargs["document_ids"] == ["doc-abc"]

    @patch("app.router.conversations.stream_chat_completion")
    async def test_message_without_kb_document_ids_no_rag(
        self, mock_stream, client, mock_db,
        mock_conversation, mock_user_message
    ):
        """Without kb_document_ids, no RAG retrieval occurs."""
        async def fake_stream(messages, model, settings):
            # No system message should be present for RAG
            system_msgs = [m for m in messages if m["role"] == "system"]
            for msg in system_msgs:
                assert "knowledge base context" not in msg.get("content", "")
            yield {"type": "token", "text": "Hello!"}
            yield {"type": "done", "usage": {"tokens_in": 5, "tokens_out": 2}}

        mock_stream.side_effect = fake_stream

        conv_result = MagicMock()
        conv_result.scalar_one_or_none.return_value = mock_conversation

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = [mock_user_message]

        mock_db.execute = AsyncMock(side_effect=[conv_result, history_result])
        mock_db.commit = AsyncMock()

        async def fake_refresh(obj):
            obj.id = uuid.uuid4()
            obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            f"/api/v1/conversations/{mock_conversation.id}/messages",
            json={"content": "Hello there"},
        )

        assert response.status_code == 200

    @patch("app.router.conversations.retrieve", new_callable=AsyncMock)
    @patch("app.router.conversations.stream_chat_completion")
    async def test_rag_citation_format_in_context(
        self, mock_stream, mock_retrieve, client, mock_db,
        mock_conversation, mock_user_message
    ):
        """RAG context includes citation markers like [^1]."""
        rag_result = MagicMock()
        rag_result.text = "Knowledge content here."
        rag_result.score = 0.88
        rag_result.document_name = "report.pdf"
        rag_result.page = 5
        rag_result.section = None
        rag_result.document_id = "doc-xyz"
        mock_retrieve.return_value = [rag_result]

        captured_messages = []

        async def fake_stream(messages, model, settings):
            captured_messages.extend(messages)
            yield {"type": "token", "text": "Answer"}
            yield {"type": "done", "usage": {"tokens_in": 10, "tokens_out": 1}}

        mock_stream.side_effect = fake_stream

        conv_result = MagicMock()
        conv_result.scalar_one_or_none.return_value = mock_conversation

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = [mock_user_message]

        mock_db.execute = AsyncMock(side_effect=[conv_result, history_result])
        mock_db.commit = AsyncMock()

        async def fake_refresh(obj):
            obj.id = uuid.uuid4()
            obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            f"/api/v1/conversations/{mock_conversation.id}/messages",
            json={
                "content": "Tell me about the report",
                "kb_document_ids": ["doc-xyz"],
            },
        )

        assert response.status_code == 200
        # Find the system message with RAG context
        system_msgs = [m for m in captured_messages if m["role"] == "system"]
        assert len(system_msgs) > 0
        rag_msg = system_msgs[0]["content"]
        assert "[^1]" in rag_msg
        assert "report.pdf" in rag_msg
        assert "Page 5" in rag_msg
