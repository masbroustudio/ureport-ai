# Phase 3: RAG & Knowledge Base

## 1. Overview

Phase 3 adds **Retrieval Augmented Generation (RAG)** and a **Knowledge Base** to uReport AI. Users can upload documents (PDF, DOCX, TXT), the system processes them into searchable chunks, and the AI uses relevant context from these documents when answering questions.

**Key capabilities:**

- **Document upload** - Upload PDF, DOCX, or TXT files to a personal knowledge base
- **Automatic ingestion** - Documents are parsed, chunked, embedded, and stored in a vector database
- **Semantic search** - Query the knowledge base using natural language
- **Context-aware chat** - Select documents to use as context when chatting with the AI
- **Citations** - AI responses include `[^N]` markers referencing the source material

## 2. RAG Pipeline Architecture

### Document Upload Flow

```
+--------+     +--------+     +---------+     +----------+     +---------+
|  File  | --> | Loader | --> | Chunker | --> | Embedder | --> | Qdrant  |
| Upload |     | (PDF/  |     | (512tok |     | (fastembed|     | Vector  |
|        |     |  DOCX/ |     |  chunks)|     |  bge-sm) |     | Store)  |
|        |     |  TXT)  |     |         |     |          |     |         |
+--------+     +--------+     +---------+     +----------+     +---------+
                                                                     |
                                                                     v
                                                               +----------+
                                                               | Stored   |
                                                               | Chunks   |
                                                               +----------+
```

### Query Flow

```
+-------+     +----------+     +---------+     +----------+
| User  | --> | Embed    | --> | Search  | --> | Top-K    |
| Query |     | Query    |     | Qdrant  |     | Results  |
+-------+     +----------+     +---------+     +----------+
                                                     |
                                                     v
                                              +-----------+     +--------+
                                              | Inject    | --> |  LLM   |
                                              | Context   |     | (with  |
                                              | + Cites   |     | context)|
                                              +-----------+     +--------+
```

## 3. Components Breakdown

| Component | File | Description |
|-----------|------|-------------|
| **Document Loaders** | `app/rag/loaders.py` | PDF (pymupdf/fitz), DOCX (python-docx), TXT extraction |
| **Chunker** | `app/rag/chunker.py` | Token-based splitting with tiktoken. 512 tokens target, 15% overlap, paragraph/sentence split boundaries |
| **Embedder** | `app/rag/embedder.py` | fastembed with `BAAI/bge-small-en-v1.5` (384 dimensions, ~33M params, fast) |
| **Vector Store** | `app/rag/vector_store.py` | Qdrant client wrapper, cosine similarity, per-user collections |
| **Ingestion** | `app/rag/ingest.py` | Orchestrates the full pipeline: load, chunk, embed, store |
| **Retriever** | `app/rag/retriever.py` | Query embedding + vector search + result formatting |

### Pipeline Details

- **Loaders** extract raw text with page/section metadata from each supported format
- **Chunker** uses tiktoken (`cl100k_base` encoding) to split text into ~512 token chunks with 15% overlap. Split boundaries respect paragraph and sentence boundaries when possible
- **Embedder** lazily downloads the `BAAI/bge-small-en-v1.5` model on first use and produces 384-dimensional vectors
- **Vector Store** manages per-user Qdrant collections with cosine similarity search
- **Ingestion** coordinates the full pipeline and persists chunk metadata to PostgreSQL

## 4. API Endpoints

All endpoints require authentication via Bearer token.

### Upload Document

```bash
curl -X POST http://localhost:8000/api/v1/kb/documents \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  -F "tags=report,2024"
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "document.pdf",
  "title": "My Document",
  "tags": ["report", "2024"],
  "language": null,
  "status": "ready",
  "chunk_count": 42,
  "error_message": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Documents

```bash
curl http://localhost:8000/api/v1/kb/documents \
  -H "Authorization: Bearer <token>"
```

**Response:** `200 OK` - Array of document objects.

### Get Document

```bash
curl http://localhost:8000/api/v1/kb/documents/{id} \
  -H "Authorization: Bearer <token>"
```

**Response:** `200 OK` - Single document object.

### Delete Document

```bash
curl -X DELETE http://localhost:8000/api/v1/kb/documents/{id} \
  -H "Authorization: Bearer <token>"
```

**Response:** `204 No Content`

Deletes the document, its vector embeddings from Qdrant, and all stored chunks from the database.

### Search Knowledge Base

```bash
curl -X POST http://localhost:8000/api/v1/kb/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "what is the revenue growth?", "top_k": 5, "document_ids": ["uuid-1"]}'
```

**Response:** `200 OK`
```json
{
  "query": "what is the revenue growth?",
  "results": [
    {
      "text": "Revenue grew by 15% year over year...",
      "score": 0.89,
      "document_name": "Annual Report 2024.pdf",
      "page": 5,
      "section": null,
      "document_id": "uuid-1"
    }
  ]
}
```

Parameters:
- `query` (required): Natural language search query
- `top_k` (optional, default 8): Number of results to return
- `document_ids` (optional): Filter results to specific documents

### Chat with KB Context

```bash
curl -X POST http://localhost:8000/api/v1/conversations/{id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"content": "Summarize the document", "kb_document_ids": ["uuid-1", "uuid-2"]}'
```

When `kb_document_ids` is provided, the system:
1. Embeds the user query
2. Retrieves top-K relevant chunks from the specified documents
3. Injects the context into the LLM system prompt with citation markers
4. Streams the response with citation events

## 5. SSE Citation Event Format

When KB documents are used in chat, citation events are emitted after the text stream and before the `done` event:

```
event: token
data: {"text": "According to the report, revenue grew by 15% [^1]..."}

event: token
data: {"text": " Operating margin also improved [^2]."}

event: citation
data: {"id": "1", "doc_name": "Annual Report 2024.pdf", "page": 5, "text": "Revenue grew by 15%...", "section": null}

event: citation
data: {"id": "2", "doc_name": "Q4 Results.docx", "page": 2, "text": "Operating margin improved...", "section": null}

event: done
data: {"message_id": "uuid", "usage": {"tokens_in": 1200, "tokens_out": 350}}
```

**Citation format:**
- Citations are emitted before the `done` event
- The LLM response uses `[^N]` markers referencing the citation IDs
- Citation `text` is truncated to 200 characters for the SSE payload

## 6. Frontend Usage

### Knowledge Base Page (`/knowledge`)

The dedicated Knowledge Base page provides:
- **Upload area** - Drag-and-drop or click to upload PDF, DOCX, or TXT files
- **Document list** - View all uploaded documents with status (processing/ready/error)
- **Search** - Semantic search across your knowledge base
- **Document management** - Delete documents and view metadata (tags, chunk count, timestamps)

### Chat Integration

- **KB document selector** - In the chat composer, select which documents to use as context
- **Only "ready" documents** are shown in the selector (documents that have been fully processed)
- **Multiple document selection** - Choose one or more documents per message

### Citation Display

- `[^N]` markers in AI responses are rendered as clickable citation links
- Clicking a citation shows a popover with the source document name, page number, and text excerpt
- Citations link back to the specific chunk that informed the AI's response

## 7. Setup & Configuration

### Environment Variables

```env
QDRANT_URL=http://localhost:6333   # Qdrant vector database URL
```

### Required Services

- **Qdrant** (vector database) - required for vector storage and search
  - Docker: `docker run -p 6333:6333 qdrant/qdrant`
  - Or use [Qdrant Cloud](https://cloud.qdrant.io/)

### fastembed Model Download

- The `BAAI/bge-small-en-v1.5` model is downloaded automatically on first use
- Cache location: `~/.cache/fastembed/` (approximately 120MB)
- First request may be slow due to model download
- Set `FASTEMBED_CACHE_PATH` environment variable for a custom cache location

### Python Dependencies (added in Phase 3)

- `pymupdf` - PDF text extraction (import as `fitz`)
- `python-docx` - DOCX text extraction
- `tiktoken` - Token counting for chunking
- `fastembed` - Local text embedding
- `qdrant-client` - Qdrant vector database client

## 8. Running Tests

```bash
# All backend tests (including RAG tests)
cd apps/api && uv run pytest tests/ -v

# Specific RAG tests
cd apps/api && uv run pytest tests/test_loaders.py tests/test_chunker.py tests/test_embedder.py tests/test_vector_store.py tests/test_ingest.py tests/test_knowledge_api.py tests/test_rag_chat.py -v

# Frontend build check
cd apps/web && pnpm build

# Lint
cd apps/api && uv run ruff check .
```

All tests run without external services (Qdrant and PostgreSQL are mocked). No internet connection is needed for tests since the fastembed model is also mocked.

## 9. Deployment Notes

Production deployment requires:

1. **Qdrant instance** - self-hosted or Qdrant Cloud
   - Recommended: Qdrant Cloud for managed service
   - Self-hosted: minimum 2GB RAM for small datasets
2. **fastembed model** - pre-download for faster cold starts:
   ```python
   from fastembed import TextEmbedding
   TextEmbedding(model_name="BAAI/bge-small-en-v1.5")  # downloads model
   ```
3. **File storage** - local filesystem (configure `FILE_STORAGE_PATH`) or object storage
4. **Database migrations** - run `alembic upgrade head` to create knowledge tables

### Performance Considerations

- Ingestion is synchronous (runs in the request lifecycle). For large documents (>100 pages), consider background processing in future iterations (Celery + Redis).
- Embedding batch size: fastembed handles batching internally
- Qdrant search is fast (<50ms for 100K vectors with HNSW index)
- Per-user collections keep data isolated and searches fast

## 10. Troubleshooting

| Issue | Solution |
|-------|----------|
| Qdrant connection refused | Ensure Qdrant is running at the URL specified in `QDRANT_URL` |
| Model download fails | Check internet connectivity. Model is ~120MB. Set `FASTEMBED_CACHE_PATH` env var for custom cache location. |
| Large PDF timeout | Currently ingestion is synchronous. Very large PDFs (>200 pages) may timeout. Split documents or increase server timeout. |
| Import error for pymupdf | Install with `pip install pymupdf` (package name is `pymupdf`, import as `fitz`) |
| DOCX extraction empty | Ensure the DOCX contains text content (not just images/tables). Tables are not extracted in MVP. |
| Upload returns 400 | Check that the file MIME type is one of: `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, or `text/plain` |
| Citations not appearing | Ensure `kb_document_ids` is provided in the message request and at least one document has status "ready" |
