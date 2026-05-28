import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
class TestUploadDocument:
    @patch("app.router.knowledge.ingest_document", new_callable=AsyncMock)
    @patch("app.router.knowledge.save_upload_file", new_callable=AsyncMock)
    async def test_upload_txt_file(self, mock_save, mock_ingest, client, mock_db):
        mock_save.return_value = ("uploads/test.txt", 100)

        doc_id = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")

        mock_db.commit = AsyncMock()

        async def fake_refresh(obj):
            obj.id = doc_id
            obj.user_id = user_id
            obj.name = "test.txt"
            obj.title = None
            obj.tags = None
            obj.language = None
            obj.status = "ready"
            obj.chunk_count = 5
            obj.error_message = None
            obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            "/api/v1/kb/documents",
            files={"file": ("test.txt", b"hello world content", "text/plain")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test.txt"
        assert data["status"] == "ready"

    @patch("app.router.knowledge.ingest_document", new_callable=AsyncMock)
    @patch("app.router.knowledge.save_upload_file", new_callable=AsyncMock)
    async def test_upload_unsupported_mime(self, mock_save, mock_ingest, client, mock_db):
        response = await client.post(
            "/api/v1/kb/documents",
            files={"file": ("test.exe", b"binary content", "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
class TestListDocuments:
    async def test_list_documents_empty(self, client, mock_db):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/v1/kb/documents")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_documents_with_items(self, client, mock_db):
        doc = MagicMock()
        doc.id = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        doc.user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        doc.name = "doc.pdf"
        doc.title = "My Doc"
        doc.tags = ["research"]
        doc.language = "en"
        doc.status = "ready"
        doc.chunk_count = 10
        doc.error_message = None
        doc.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [doc]
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/v1/kb/documents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "doc.pdf"
        assert data[0]["status"] == "ready"


@pytest.mark.asyncio
class TestGetDocument:
    async def test_get_document_found(self, client, mock_db):
        doc = MagicMock()
        doc.id = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        doc.user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        doc.name = "doc.pdf"
        doc.title = "My Doc"
        doc.tags = None
        doc.language = None
        doc.status = "ready"
        doc.chunk_count = 5
        doc.error_message = None
        doc.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/kb/documents/{doc.id}"
        )
        assert response.status_code == 200
        assert response.json()["name"] == "doc.pdf"

    async def test_get_document_not_found(self, client, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/kb/documents/{uuid.uuid4()}"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteDocument:
    @patch("app.router.knowledge.VectorStore")
    async def test_delete_document_success(self, mock_vs_cls, client, mock_db):
        doc = MagicMock()
        doc.id = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        doc.user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")

        # First execute returns the document, second returns chunks
        mock_result_doc = MagicMock()
        mock_result_doc.scalar_one_or_none.return_value = doc

        mock_result_chunks = MagicMock()
        mock_result_chunks.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(
            side_effect=[mock_result_doc, mock_result_chunks]
        )
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        mock_vs = MagicMock()
        mock_vs_cls.return_value = mock_vs

        response = await client.delete(
            f"/api/v1/kb/documents/{doc.id}"
        )
        assert response.status_code == 204

    async def test_delete_document_not_found(self, client, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.delete(
            f"/api/v1/kb/documents/{uuid.uuid4()}"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestSearchKnowledge:
    @patch("app.router.knowledge.retrieve", new_callable=AsyncMock)
    async def test_search_returns_results(self, mock_retrieve, client, mock_db):
        mock_result = MagicMock()
        mock_result.text = "found text"
        mock_result.score = 0.9
        mock_result.document_name = "test.pdf"
        mock_result.page = 1
        mock_result.section = None
        mock_result.document_id = "doc-1"
        mock_retrieve.return_value = [mock_result]

        response = await client.post(
            "/api/v1/kb/search",
            json={"query": "test query"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test query"
        assert len(data["results"]) == 1
        assert data["results"][0]["text"] == "found text"
        assert data["results"][0]["score"] == 0.9

    @patch("app.router.knowledge.retrieve", new_callable=AsyncMock)
    async def test_search_empty_results(self, mock_retrieve, client, mock_db):
        mock_retrieve.return_value = []

        response = await client.post(
            "/api/v1/kb/search",
            json={"query": "no results query"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    @patch("app.router.knowledge.retrieve", new_callable=AsyncMock)
    async def test_search_with_document_ids(self, mock_retrieve, client, mock_db):
        mock_retrieve.return_value = []

        response = await client.post(
            "/api/v1/kb/search",
            json={"query": "test", "document_ids": ["doc-1", "doc-2"]},
        )
        assert response.status_code == 200
        mock_retrieve.assert_called_once()
        call_kwargs = mock_retrieve.call_args.kwargs
        assert call_kwargs["document_ids"] == ["doc-1", "doc-2"]
