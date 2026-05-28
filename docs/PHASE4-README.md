# Phase 4: Report Generator

## 1. Overview

Phase 4 adds a **Report Generator** to uReport AI. Users can create structured reports with chapters following the Indonesian academic format (BAB I through BAB V). The system uses an LLM-powered pipeline to plan report outlines, write each section individually, and render the final output as PDF (or HTML fallback).

**Key capabilities:**

- **LLM-powered outline planning** - Generates a structured report outline using Gemini Flash
- **Section-by-section writing** - Each section is written independently by Cerebras/Llama 70B
- **Real-time progress via SSE** - Streaming progress updates during generation
- **PDF rendering** - Professional PDF output via WeasyPrint with Jinja2 templates
- **HTML fallback** - When WeasyPrint is unavailable, HTML output is generated instead
- **Template system** - Extensible template structure with meta.yaml configuration
- **RAG integration** - Sections can optionally pull context from the knowledge base
- **Outline editing** - Users can review and modify the generated outline before writing

## 2. Architecture

### Pipeline Diagram

```
+-------------------+     +------------------+     +-------------------+
|   User Request    | --> |  Planner         | --> |  Outline JSON     |
|   (title, opts)   |     |  (Gemini Flash)  |     |  (BAB I-V with    |
|                   |     |                  |     |   sections)       |
+-------------------+     +------------------+     +-------------------+
                                                           |
                                                           v
+-------------------+     +------------------+     +-------------------+
|   Rendered File   | <-- |  Renderer        | <-- |  Writer           |
|   (PDF or HTML)   |     |  (Jinja2 +       |     |  (Cerebras/Llama  |
|                   |     |   WeasyPrint)    |     |   70B per section)|
+-------------------+     +------------------+     +-------------------+
```

### Component Responsibilities

| Component | File | Role |
|-----------|------|------|
| **Planner** | `app/report/planner.py` | Calls Gemini Flash to produce an outline JSON with chapters and sections |
| **Writer** | `app/report/writer.py` | Calls Cerebras/Llama 70B to write markdown content for each section |
| **Renderer** | `app/report/renderer.py` | Converts section markdown to HTML via Jinja2 template, renders PDF via WeasyPrint |
| **Router** | `app/router/reports.py` | REST API endpoints for CRUD operations and SSE generation streaming |
| **Models** | `app/model/report.py` | SQLAlchemy ORM models for `reports` and `report_sections` tables |
| **Schemas** | `app/schema/report.py` | Pydantic request/response schemas |

## 3. API Endpoints

All endpoints are prefixed with `/api/v1/reports` and require authentication via `Authorization: Bearer <token>` header.

### POST /api/v1/reports/

Create a new report and generate its outline via LLM.

**Request Body:**

```json
{
  "title": "Laporan Penjualan Q1 2025",
  "template_id": "business_report_v1",
  "file_ids": ["uuid-1", "uuid-2"],
  "kb_document_ids": ["uuid-3"],
  "custom_instructions": "Focus on revenue growth",
  "conversation_id": "uuid-of-conversation"
}
```

Only `title` is required. All other fields are optional.

**Response (201 Created):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "12345678-1234-5678-1234-567812345678",
  "conversation_id": null,
  "title": "Laporan Penjualan Q1 2025",
  "subtitle": null,
  "author": null,
  "template_id": "business_report_v1",
  "outline_json": {
    "chapters": [
      {
        "number": "BAB I",
        "title": "Pendahuluan",
        "sections": [
          {
            "id": "1.1",
            "title": "Latar Belakang",
            "instruction": "Write background about Q1 sales performance",
            "use_rag": false,
            "use_data": false,
            "target_words": 300
          }
        ]
      }
    ]
  },
  "status": "created",
  "progress_pct": 0,
  "error_message": null,
  "pdf_path": null,
  "created_at": "2025-01-15T00:00:00Z",
  "updated_at": "2025-01-15T00:00:00Z"
}
```

If outline planning fails, the response still returns 201 but with `status: "failed"` and `error_message` populated.

---

### GET /api/v1/reports/

List all reports for the authenticated user, ordered by creation date (newest first).

**Response (200 OK):**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Laporan Penjualan Q1 2025",
    "status": "done",
    "progress_pct": 100,
    "template_id": "business_report_v1",
    "created_at": "2025-01-15T00:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
]
```

---

### GET /api/v1/reports/{report_id}

Get full report details including the outline JSON.

**Response (200 OK):** Same structure as the POST response.

**Error (404):** `{"detail": "Report not found"}`

---

### PUT /api/v1/reports/{report_id}/outline

Update the report outline. This replaces the existing outline and recreates all section records.

**Request Body:**

```json
{
  "outline_json": {
    "chapters": [
      {
        "number": "BAB I",
        "title": "Pendahuluan",
        "sections": [
          {
            "id": "1.1",
            "title": "Latar Belakang",
            "instruction": "Write about the background",
            "use_rag": false,
            "target_words": 300
          }
        ]
      }
    ]
  }
}
```

**Response (200 OK):** Full report object with updated outline.

---

### POST /api/v1/reports/{report_id}/start

Start the report generation process. Returns a **Server-Sent Events (SSE)** stream with progress updates.

**Response:** `Content-Type: text/event-stream`

See [Section 6: SSE Progress Format](#6-sse-progress-format) for the event format.

**Error (400):** `{"detail": "Report has no outline. Create outline first."}`

---

### GET /api/v1/reports/{report_id}/sections

List all sections for a report, ordered by `section_order`.

**Response (200 OK):**

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "chapter_number": "BAB I",
    "chapter_title": "Pendahuluan",
    "section_order": 0,
    "section_title": "Latar Belakang",
    "content_markdown": "### Overview\n\nThis section covers...",
    "status": "done",
    "word_count": 285,
    "created_at": "2025-01-15T00:00:00Z",
    "updated_at": "2025-01-15T00:05:00Z"
  }
]
```

---

### POST /api/v1/reports/{report_id}/sections/{section_id}/regenerate

Regenerate a single section's content using the LLM writer.

**Response (200 OK):** Updated section object (same structure as items in the sections list).

---

### GET /api/v1/reports/{report_id}/pdf

Download the generated PDF or HTML file.

**Response:** File download with appropriate `Content-Type`:
- `application/pdf` for PDF files
- `text/html` for HTML fallback files

**Error (404):** `{"detail": "Report file not generated yet"}` or `{"detail": "Report file not found on disk"}`

---

### DELETE /api/v1/reports/{report_id}

Delete a report, all its sections, and the generated file from disk.

**Response (204 No Content):** Empty body on success.

## 4. Report Creation Flow

The full lifecycle of creating a report follows these steps:

1. **Create Report** - `POST /api/v1/reports/` with a title and optional parameters. The planner LLM generates an outline and creates section records in the database. Report status transitions: `planning` -> `created` (or `failed`).

2. **Review Outline** - `GET /api/v1/reports/{id}` to view the generated outline with chapters and sections.

3. **Edit Outline (optional)** - `PUT /api/v1/reports/{id}/outline` to modify the outline structure. This deletes existing sections and recreates them from the new outline.

4. **Start Generation** - `POST /api/v1/reports/{id}/start` initiates the writing process. Connect to the SSE stream to receive progress events. Report status transitions: `writing` -> `rendering` -> `done`.

5. **Monitor Progress** - Listen to SSE events:
   - `progress` events as each section completes (with percentage)
   - `render` event when PDF rendering begins
   - `done` event with final file path

6. **Review Sections** - `GET /api/v1/reports/{id}/sections` to view individual section content.

7. **Regenerate Sections (optional)** - `POST /api/v1/reports/{id}/sections/{section_id}/regenerate` to rewrite any section that needs improvement.

8. **Download Result** - `GET /api/v1/reports/{id}/pdf` to download the final PDF or HTML file.

## 5. Template Structure

Templates are stored in `apps/api/app/report/templates/{template_id}/` and consist of three files:

### meta.yaml

Defines the template metadata and default chapter structure:

```yaml
id: business_report_v1
name: "Laporan Bisnis"
description: "Template laporan bisnis profesional dengan format bab standar"
default_chapters:
  - "Pendahuluan"
  - "Tinjauan Pustaka"
  - "Metodologi"
  - "Pembahasan"
  - "Kesimpulan & Saran"
fonts:
  - "Inter"
  - "Source Serif Pro"
page_size: A4
margins:
  top: 25mm
  bottom: 25mm
  left: 30mm
  right: 25mm
```

The `default_chapters` list is passed to the planner LLM as a suggested structure. The planner may adapt it based on the user's request.

### layout.html.j2

Jinja2 template for the full HTML document. Available template variables:

| Variable | Type | Description |
|----------|------|-------------|
| `title` | `str` | Report title |
| `subtitle` | `str\|None` | Optional subtitle |
| `author` | `str\|None` | Optional author name |
| `date` | `str` | Formatted date (e.g., "15 January 2025") |
| `chapters` | `list[dict]` | List of chapter dicts with `number`, `title`, and `sections` |
| `styles_css` | `str` | Contents of styles.css (inlined in `<style>` tag) |

Each chapter contains a list of sections, where each section has:
- `title` (str) - The section title
- `content_html` (str) - Section markdown converted to HTML

### styles.css

CSS styles for the rendered document. Uses `@page` rules for PDF page setup (size, margins, headers/footers) and standard CSS for typography and layout. WeasyPrint supports a subset of CSS including `@page`, `break-before`, `string-set`, and CSS counters.

### Adding a New Template

1. Create a directory under `apps/api/app/report/templates/` with your template ID (e.g., `research_paper_v1/`).
2. Add `meta.yaml` with at minimum: `id`, `name`, `description`, and `default_chapters`.
3. Add `layout.html.j2` with your HTML structure using the Jinja2 variables above.
4. Add `styles.css` with your styling.
5. Use the template by passing `template_id: "your_template_id"` in the create report request.

## 6. SSE Progress Format

The `/api/v1/reports/{report_id}/start` endpoint returns a `text/event-stream` response with the following event types:

### Event: `progress`

Sent after each section is written (whether successful or failed).

```
event: progress
data: {"section": "Latar Belakang", "completed": 1, "total": 8, "pct": 11}
```

| Field | Type | Description |
|-------|------|-------------|
| `section` | `str` | Title of the section just completed |
| `completed` | `int` | Number of sections processed so far |
| `total` | `int` | Total number of sections |
| `pct` | `int` | Progress percentage (0-90, writing phase only) |

### Event: `render`

Sent when all sections are written and PDF rendering begins.

```
event: render
data: {"message": "Rendering PDF..."}
```

### Event: `done`

Sent when the report is fully generated and the file is ready for download.

```
event: done
data: {"report_id": "550e8400-e29b-41d4-a716-446655440000", "pdf_path": "storage/reports/550e8400-e29b-41d4-a716-446655440000.pdf", "total_sections": 8}
```

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | `str` | UUID of the report |
| `pdf_path` | `str` | Path to the generated file on the server |
| `total_sections` | `int` | Total number of sections written |

### Event: `error`

Sent if rendering fails after sections are written.

```
event: error
data: {"error": "WeasyPrint rendering failed: missing pango library"}
```

## 7. Database Schema

### Table: `reports`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default uuid4 | Report unique identifier |
| `user_id` | `UUID` | FK -> users.id, NOT NULL | Owner of the report |
| `conversation_id` | `UUID` | FK -> conversations.id, nullable | Optional linked conversation |
| `title` | `VARCHAR` | NOT NULL | Report title |
| `subtitle` | `VARCHAR` | nullable | Optional subtitle |
| `author` | `VARCHAR` | nullable | Optional author name |
| `template_id` | `VARCHAR` | default "business_report_v1" | Template used for rendering |
| `outline_json` | `JSONB` | nullable | Generated outline structure |
| `status` | `VARCHAR` | default "created" | One of: planning, created, writing, rendering, done, failed |
| `progress_pct` | `INTEGER` | default 0 | Progress percentage (0-100) |
| `error_message` | `TEXT` | nullable | Error details if status is "failed" |
| `pdf_path` | `TEXT` | nullable | Path to generated PDF/HTML file |
| `created_at` | `TIMESTAMPTZ` | server_default now() | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | server_default now(), onupdate now() | Last update timestamp |

### Table: `report_sections`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default uuid4 | Section unique identifier |
| `report_id` | `UUID` | FK -> reports.id, NOT NULL | Parent report |
| `chapter_number` | `VARCHAR` | NOT NULL | Chapter number (e.g., "BAB I") |
| `chapter_title` | `VARCHAR` | NOT NULL | Chapter title (e.g., "Pendahuluan") |
| `section_order` | `INTEGER` | NOT NULL | Ordering index (0-based) |
| `section_title` | `VARCHAR` | NOT NULL | Section title |
| `content_markdown` | `TEXT` | nullable | Generated markdown content |
| `status` | `VARCHAR` | default "pending" | One of: pending, writing, done, failed |
| `word_count` | `INTEGER` | default 0 | Word count of generated content |
| `created_at` | `TIMESTAMPTZ` | server_default now() | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | server_default now(), onupdate now() | Last update timestamp |

## 8. Testing

### Test Files

| File | Covers |
|------|--------|
| `apps/api/tests/test_reports.py` | API endpoint tests (create, list, get, update outline, delete, list sections) |
| `apps/api/tests/test_report_planner.py` | Planner unit tests (outline generation, JSON parsing, validation, defaults) |
| `apps/api/tests/test_report_writer.py` | Writer unit tests (section writing, prompt construction, RAG materials) |
| `apps/api/tests/test_report_renderer.py` | Renderer unit tests (HTML fallback, chapter grouping, empty content handling) |

### Running Tests

```bash
cd apps/api
uv run pytest tests/test_reports.py tests/test_report_planner.py tests/test_report_writer.py tests/test_report_renderer.py -v
```

Or run all tests:

```bash
cd apps/api
uv run pytest tests/ -v
```

### What is Mocked

- **LLM calls** - `litellm.acompletion` is patched to return controlled responses. No real API calls are made.
- **Database** - `AsyncMock` session with mocked `execute`, `commit`, `refresh`, and `delete` methods.
- **Authentication** - `get_current_user` dependency is overridden to return a mock user (see `apps/api/tests/conftest.py`).
- **WeasyPrint** - In renderer tests, `STORAGE_DIR` is patched to use `tmp_path`. The HTML fallback path is tested since WeasyPrint system libraries may not be available in CI.
- **RAG retriever** - Not mocked in report tests since it is imported conditionally and only called when `use_rag=True`.

### Adding New Tests

Follow the existing pattern in `tests/conftest.py`:
1. Use the `client` fixture for authenticated HTTP requests (uses `httpx.AsyncClient` with ASGI transport).
2. Use the `mock_db` fixture for database mocking.
3. Patch LLM calls with `@patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)`.
4. Use `MagicMock()` for model objects with attributes matching the SQLAlchemy model columns.

## 9. Deployment Notes

### WeasyPrint System Dependencies

WeasyPrint requires native libraries for PDF rendering. On Ubuntu/Debian:

```bash
sudo apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libglib2.0-0
```

### Font Installation

The default template uses "Inter" and "Source Serif Pro" fonts. Install them:

```bash
# On Ubuntu/Debian
sudo apt-get install -y fonts-inter

# For Source Serif Pro (Google Fonts)
mkdir -p /usr/local/share/fonts/source-serif-pro
wget -O /tmp/source-serif-pro.zip "https://fonts.google.com/download?family=Source+Serif+Pro"
unzip /tmp/source-serif-pro.zip -d /usr/local/share/fonts/source-serif-pro
fc-cache -fv
```

### Storage Directory

Generated reports are stored in `./storage/reports/` relative to the API working directory. Ensure this directory exists and is writable:

```bash
mkdir -p storage/reports
chmod 755 storage/reports
```

The renderer creates this directory automatically if it does not exist (`mkdir(parents=True, exist_ok=True)`), but the process must have write permissions to the parent directory.

### HTML Fallback Behavior

If WeasyPrint is not installed or fails at runtime, the renderer automatically falls back to saving the rendered HTML file. The download endpoint detects the file extension and serves it with the appropriate `Content-Type`:
- `.pdf` files are served as `application/pdf`
- `.html` files are served as `text/html`

This ensures the application remains functional even without WeasyPrint installed, which is useful for development environments or lightweight deployments.

### Docker Considerations

If deploying with Docker, include WeasyPrint dependencies in your image:

```dockerfile
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*
```

## 10. Configuration

### Environment Variables

The following environment variables are relevant to the report generator (defined in `apps/api/app/settings.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | `""` | API key for Google Gemini (used by the planner) |
| `CEREBRAS_API_KEY` | `""` | API key for Cerebras (used by the writer) |

Both keys are passed to `litellm.acompletion()`. If empty, litellm will attempt to use default environment-based authentication.

### LLM Models Used

| Component | Model | Provider | Purpose |
|-----------|-------|----------|---------|
| Planner | `gemini/gemini-2.0-flash` | Google Gemini | Fast outline generation |
| Writer | `cerebras/llama-3.3-70b` | Cerebras | High-quality section writing |

These model strings follow litellm's provider/model naming convention and can be changed by modifying `apps/api/app/report/planner.py` and `apps/api/app/report/writer.py` directly. There is currently no environment variable override for model selection.

### Template Configuration

The default template is `business_report_v1`. To change the default, modify the `template_id` default value in:
- `apps/api/app/model/report.py` (column default)
- `apps/api/app/schema/report.py` (Pydantic schema default)
