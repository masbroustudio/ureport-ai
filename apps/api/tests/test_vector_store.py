from unittest.mock import MagicMock, patch

from app.rag.embedder import EMBEDDING_DIM


class TestVectorStore:
    @patch("app.rag.vector_store.QdrantClient")
    def test_ensure_collection_creates_new(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client
        # Simulate no existing collections
        mock_client.get_collections.return_value.collections = []

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        store.ensure_collection("user123")

        mock_client.create_collection.assert_called_once()
        call_kwargs = mock_client.create_collection.call_args
        assert "kb_user123" in str(call_kwargs)

    @patch("app.rag.vector_store.QdrantClient")
    def test_ensure_collection_skips_existing(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client
        # Simulate existing collection
        existing = MagicMock()
        existing.name = "kb_user123"
        mock_client.get_collections.return_value.collections = [existing]

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        store.ensure_collection("user123")

        mock_client.create_collection.assert_not_called()

    @patch("app.rag.vector_store.QdrantClient")
    def test_upsert_chunks(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        chunks = [
            {
                "point_id": "point-1",
                "vector": [0.1] * EMBEDDING_DIM,
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "document_name": "test.pdf",
                "text": "Sample text",
                "page": 1,
                "section": None,
                "chunk_index": 0,
            }
        ]
        store.upsert_chunks("user123", chunks)

        mock_client.upsert.assert_called_once()
        call_kwargs = mock_client.upsert.call_args
        assert call_kwargs.kwargs["collection_name"] == "kb_user123"

    @patch("app.rag.vector_store.QdrantClient")
    def test_search_returns_results(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client

        # Mock search result
        mock_point = MagicMock()
        mock_point.payload = {
            "text": "result text",
            "document_name": "test.pdf",
            "page": 1,
            "section": None,
            "document_id": "doc-1",
            "chunk_index": 0,
        }
        mock_point.score = 0.95
        mock_client.query_points.return_value.points = [mock_point]

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        results = store.search("user123", query_vector=[0.1] * EMBEDDING_DIM)

        assert len(results) == 1
        assert results[0]["text"] == "result text"
        assert results[0]["score"] == 0.95
        assert results[0]["document_name"] == "test.pdf"
        assert results[0]["document_id"] == "doc-1"

    @patch("app.rag.vector_store.QdrantClient")
    def test_search_with_document_ids_filter(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client
        mock_client.query_points.return_value.points = []

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        store.search("user123", query_vector=[0.1] * EMBEDDING_DIM, document_ids=["doc-1"])

        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs["query_filter"] is not None

    @patch("app.rag.vector_store.QdrantClient")
    def test_search_without_filter(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client
        mock_client.query_points.return_value.points = []

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        store.search("user123", query_vector=[0.1] * EMBEDDING_DIM)

        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs["query_filter"] is None

    @patch("app.rag.vector_store.QdrantClient")
    def test_delete_document(self, mock_qdrant_cls):
        mock_client = MagicMock()
        mock_qdrant_cls.return_value = mock_client

        from app.rag.vector_store import VectorStore

        store = VectorStore(qdrant_url="http://fake:6333")
        store.delete_document("user123", "doc-1")

        mock_client.delete.assert_called_once()
        call_kwargs = mock_client.delete.call_args.kwargs
        assert call_kwargs["collection_name"] == "kb_user123"
