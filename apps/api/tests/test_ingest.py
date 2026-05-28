import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.ingest import ingest_document


@pytest.fixture
def mock_db_session():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.add_all = MagicMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_doc_record():
    doc = MagicMock()
    doc.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    doc.name = "test_document.pdf"
    doc.status = "processing"
    doc.chunk_count = 0
    doc.error_message = None
    return doc


class TestIngestDocumentSuccess:
    @patch("app.rag.ingest.get_vector_store")
    @patch("app.rag.ingest.embed_texts")
    @patch("app.rag.ingest.chunk_text")
    @patch("app.rag.ingest.load_txt")
    @pytest.mark.asyncio
    async def test_successful_ingestion(
        self, mock_load_txt, mock_chunk_text, mock_embed_texts, mock_get_vs,
        mock_db_session, mock_doc_record
    ):
        # Setup mocks
        mock_load_txt.return_value = [
            {"text": "Sample content here.", "page": None, "section": None}
        ]

        mock_chunk = MagicMock()
        mock_chunk.text = "Sample content here."
        mock_chunk.page = None
        mock_chunk.section = None
        mock_chunk.chunk_index = 0
        mock_chunk.token_count = 5
        mock_chunk_text.return_value = [mock_chunk]

        mock_embed_texts.return_value = [[0.1] * 384]

        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs

        # Mock db.execute for the select query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_doc_record
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await ingest_document(
            db=mock_db_session,
            user_id="user-123",
            document_id=str(mock_doc_record.id),
            file_path="/tmp/test.txt",
            file_type="txt",
        )

        # Verify document status set to ready
        assert mock_doc_record.status == "ready"
        assert mock_doc_record.chunk_count == 1
        mock_db_session.commit.assert_called()

    @patch("app.rag.ingest.get_vector_store")
    @patch("app.rag.ingest.embed_texts")
    @patch("app.rag.ingest.chunk_text")
    @patch("app.rag.ingest.load_txt")
    @pytest.mark.asyncio
    async def test_vector_store_called(
        self, mock_load_txt, mock_chunk_text, mock_embed_texts, mock_get_vs,
        mock_db_session, mock_doc_record
    ):
        mock_load_txt.return_value = [
            {"text": "Content.", "page": None, "section": None}
        ]
        mock_chunk = MagicMock()
        mock_chunk.text = "Content."
        mock_chunk.page = None
        mock_chunk.section = None
        mock_chunk.chunk_index = 0
        mock_chunk.token_count = 3
        mock_chunk_text.return_value = [mock_chunk]
        mock_embed_texts.return_value = [[0.1] * 384]

        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_doc_record
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await ingest_document(
            db=mock_db_session,
            user_id="user-123",
            document_id=str(mock_doc_record.id),
            file_path="/tmp/test.txt",
            file_type="txt",
        )

        mock_vs.ensure_collection.assert_called_once_with("user-123")
        mock_vs.upsert_chunks.assert_called_once()

    @patch("app.rag.ingest.get_vector_store")
    @patch("app.rag.ingest.embed_texts")
    @patch("app.rag.ingest.chunk_text")
    @patch("app.rag.ingest.load_pdf")
    @pytest.mark.asyncio
    async def test_pdf_loading(
        self, mock_load_pdf, mock_chunk_text, mock_embed_texts, mock_get_vs,
        mock_db_session, mock_doc_record
    ):
        mock_load_pdf.return_value = [
            {"text": "PDF content.", "page": 1, "section": None}
        ]
        mock_chunk = MagicMock()
        mock_chunk.text = "PDF content."
        mock_chunk.page = 1
        mock_chunk.section = None
        mock_chunk.chunk_index = 0
        mock_chunk.token_count = 3
        mock_chunk_text.return_value = [mock_chunk]
        mock_embed_texts.return_value = [[0.1] * 384]

        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_doc_record
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await ingest_document(
            db=mock_db_session,
            user_id="user-123",
            document_id=str(mock_doc_record.id),
            file_path="/tmp/test.pdf",
            file_type="pdf",
        )

        mock_load_pdf.assert_called_once_with("/tmp/test.pdf")


class TestIngestDocumentFailure:
    @patch("app.rag.ingest.get_vector_store")
    @patch("app.rag.ingest.load_txt")
    @pytest.mark.asyncio
    async def test_loader_exception_sets_failed_status(
        self, mock_load_txt, mock_get_vs, mock_db_session, mock_doc_record
    ):
        mock_load_txt.side_effect = RuntimeError("File read error")
        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs

        # First call for the error handler select query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_doc_record
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await ingest_document(
            db=mock_db_session,
            user_id="user-123",
            document_id=str(mock_doc_record.id),
            file_path="/tmp/bad.txt",
            file_type="txt",
        )

        assert mock_doc_record.status == "failed"
        assert "File read error" in mock_doc_record.error_message
        mock_db_session.rollback.assert_called()

    @patch("app.rag.ingest.get_vector_store")
    @patch("app.rag.ingest.load_txt")
    @pytest.mark.asyncio
    async def test_empty_document_sets_failed_status(
        self, mock_load_txt, mock_get_vs, mock_db_session, mock_doc_record
    ):
        mock_load_txt.return_value = []
        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_doc_record
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await ingest_document(
            db=mock_db_session,
            user_id="user-123",
            document_id=str(mock_doc_record.id),
            file_path="/tmp/empty.txt",
            file_type="txt",
        )

        assert mock_doc_record.status == "failed"
        assert "No text content" in mock_doc_record.error_message
