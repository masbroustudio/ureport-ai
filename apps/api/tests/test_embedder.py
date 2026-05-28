from unittest.mock import MagicMock, patch

import numpy as np

from app.rag.embedder import EMBEDDING_DIM


class TestEmbedTexts:
    @patch("app.rag.embedder._get_model")
    def test_returns_list_of_vectors(self, mock_get_model):
        mock_model = MagicMock()
        fake_embeddings = [
            np.random.rand(EMBEDDING_DIM).astype(np.float32) for _ in range(3)
        ]
        mock_model.embed.return_value = iter(fake_embeddings)
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_texts

        result = embed_texts(["text one", "text two", "text three"])
        assert len(result) == 3

    @patch("app.rag.embedder._get_model")
    def test_correct_dimensions(self, mock_get_model):
        mock_model = MagicMock()
        fake_embeddings = [np.random.rand(EMBEDDING_DIM).astype(np.float32)]
        mock_model.embed.return_value = iter(fake_embeddings)
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_texts

        result = embed_texts(["hello"])
        assert len(result[0]) == EMBEDDING_DIM

    @patch("app.rag.embedder._get_model")
    def test_returns_python_lists(self, mock_get_model):
        mock_model = MagicMock()
        fake_embeddings = [np.random.rand(EMBEDDING_DIM).astype(np.float32)]
        mock_model.embed.return_value = iter(fake_embeddings)
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_texts

        result = embed_texts(["hello"])
        assert isinstance(result[0], list)
        assert isinstance(result[0][0], float)

    @patch("app.rag.embedder._get_model")
    def test_batch_processing(self, mock_get_model):
        mock_model = MagicMock()
        batch_size = 10
        fake_embeddings = [
            np.random.rand(EMBEDDING_DIM).astype(np.float32) for _ in range(batch_size)
        ]
        mock_model.embed.return_value = iter(fake_embeddings)
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_texts

        texts = [f"text {i}" for i in range(batch_size)]
        result = embed_texts(texts)
        assert len(result) == batch_size
        mock_model.embed.assert_called_once_with(texts)


class TestEmbedQuery:
    @patch("app.rag.embedder._get_model")
    def test_returns_single_vector(self, mock_get_model):
        mock_model = MagicMock()
        fake_embedding = np.random.rand(EMBEDDING_DIM).astype(np.float32)
        mock_model.query_embed.return_value = iter([fake_embedding])
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_query

        result = embed_query("test query")
        assert len(result) == EMBEDDING_DIM

    @patch("app.rag.embedder._get_model")
    def test_returns_python_list(self, mock_get_model):
        mock_model = MagicMock()
        fake_embedding = np.random.rand(EMBEDDING_DIM).astype(np.float32)
        mock_model.query_embed.return_value = iter([fake_embedding])
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_query

        result = embed_query("test query")
        assert isinstance(result, list)
        assert isinstance(result[0], float)

    @patch("app.rag.embedder._get_model")
    def test_calls_query_embed(self, mock_get_model):
        mock_model = MagicMock()
        fake_embedding = np.random.rand(EMBEDDING_DIM).astype(np.float32)
        mock_model.query_embed.return_value = iter([fake_embedding])
        mock_get_model.return_value = mock_model

        from app.rag.embedder import embed_query

        embed_query("my query")
        mock_model.query_embed.assert_called_once_with("my query")
