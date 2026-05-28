from app.rag.chunker import Chunk, chunk_text


class TestChunkText:
    def test_short_text_single_chunk(self):
        """Short text below target_tokens returns a single chunk."""
        pages = [{"text": "This is a short sentence.", "page": 1, "section": None}]
        chunks = chunk_text(pages, target_tokens=512, overlap_tokens=77)
        assert len(chunks) == 1
        assert chunks[0].text == "This is a short sentence."
        assert chunks[0].chunk_index == 0
        assert chunks[0].page == 1

    def test_long_text_multiple_chunks(self):
        """Long text exceeding target_tokens returns multiple chunks."""
        # Create text that will exceed 512 tokens
        long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 200)
        pages = [{"text": long_text, "page": 1, "section": "intro"}]
        chunks = chunk_text(pages, target_tokens=512, overlap_tokens=77)
        assert len(chunks) > 1

    def test_empty_input(self):
        """Empty pages list returns empty chunk list."""
        chunks = chunk_text([])
        assert chunks == []

    def test_empty_text_input(self):
        """Pages with empty text returns empty chunk list."""
        pages = [{"text": "", "page": 1, "section": None}]
        chunks = chunk_text(pages)
        assert chunks == []

    def test_chunk_index_sequential(self):
        """Chunk indices are sequential starting from 0."""
        long_text = " ".join(["word"] * 2000)
        pages = [{"text": long_text, "page": 1, "section": None}]
        chunks = chunk_text(pages, target_tokens=100, overlap_tokens=20)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_token_count_within_range(self):
        """Each chunk token_count is within expected range (target + some slack)."""
        long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 200)
        pages = [{"text": long_text, "page": 1, "section": None}]
        chunks = chunk_text(pages, target_tokens=512, overlap_tokens=77)
        for chunk in chunks:
            assert chunk.token_count > 0
            # Allow generous upper bound due to overlap and sentence boundaries
            assert chunk.token_count <= 1024

    def test_page_metadata_preserved(self):
        """Page metadata is carried through to chunks."""
        pages = [{"text": "Hello world content here.", "page": 5, "section": "intro"}]
        chunks = chunk_text(pages)
        assert chunks[0].page == 5
        assert chunks[0].section == "intro"

    def test_chunk_is_dataclass(self):
        """Chunks are Chunk dataclass instances."""
        pages = [{"text": "Some text.", "page": 1, "section": None}]
        chunks = chunk_text(pages)
        assert isinstance(chunks[0], Chunk)
        assert hasattr(chunks[0], "text")
        assert hasattr(chunks[0], "page")
        assert hasattr(chunks[0], "section")
        assert hasattr(chunks[0], "chunk_index")
        assert hasattr(chunks[0], "token_count")

    def test_multiple_pages(self):
        """Multiple pages are combined and chunked together."""
        pages = [
            {"text": "Content from page one.", "page": 1, "section": None},
            {"text": "Content from page two.", "page": 2, "section": None},
        ]
        chunks = chunk_text(pages)
        # With small text, should be a single chunk or two depending on total size
        assert len(chunks) >= 1
        # All text should be present
        all_text = " ".join(c.text for c in chunks)
        assert "page one" in all_text
        assert "page two" in all_text
