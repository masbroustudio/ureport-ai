# Phase 2: Data Analyst Mode

## 1. Overview

Phase 2 adds **Data Analyst Mode** to uReport AI, transforming it from a simple chat application into an intelligent data analysis platform. Users can upload Excel (`.xlsx`, `.xls`) or CSV files, and the AI automatically profiles the data and performs interactive analysis with tables and Plotly charts.

**Key capabilities:**

- **File upload** - Drag-and-drop or select CSV/Excel files (up to 50 MB)
- **Auto-profiling** - Automatic column statistics, data types, missing values, and sample data extraction
- **Code execution sandbox** - Secure subprocess-based Python execution with AST safety checking
- **Interactive charts** - Plotly-powered visualizations streamed directly to the frontend via SSE

## 2. Architecture

### File Upload Pipeline

```
POST /api/v1/files (multipart)
    -> Validate MIME type (CSV, XLSX, XLS)
    -> Save to local storage (apps/api/storage/uploads/{user_id}/{file_id}_{filename})
    -> Auto-profile with pandas (column stats, dtypes, sample values)
    -> Store profile JSON in database
    -> Return FileResponse with profile
```

### Data Analysis Flow

```
User sends message with file_ids
    -> Backend fetches file profile from DB
    -> build_data_analysis_system_prompt() creates context with column details
    -> LLM generates Python code using pandas/plotly
    -> extract_code_from_response() parses code from markdown
    -> SandboxExecutor runs code in subprocess with pre-loaded DataFrame
    -> Results (chart_spec, table_data) streamed to frontend via SSE
```

### SSE Event Flow

The streaming response emits events in this order:

```
event: token   -> Incremental text from LLM
event: code    -> The Python code that was executed
event: chart   -> Plotly figure specification (if generated)
event: table   -> Tabular data with columns and rows (if generated)
event: done    -> Completion signal with message_id and usage stats
```

## 3. Project Structure (New Files)

### Backend (`apps/api/`)

| File | Purpose |
|------|---------|
| `app/model/file.py` | SQLAlchemy model for uploaded files (UUID PK, user_id, profile_json JSONB) |
| `app/schema/file.py` | Pydantic schemas: `FileResponse`, `FilePreviewResponse` |
| `app/service/files.py` | File storage service: save, delete, path resolution |
| `app/data/profiler.py` | Auto-profiling engine using pandas (column stats, head preview) |
| `app/data/sandbox.py` | Code execution sandbox with AST safety checking and subprocess isolation |
| `app/data/tools.py` | Data analysis tool functions: `get_dataframe_profile`, `run_python_code`, `make_chart` |
| `app/data/prompts.py` | LLM prompt templates: `build_data_analysis_system_prompt`, `extract_code_from_response` |
| `app/router/files.py` | File endpoints: upload, list, get, preview, delete |

### Frontend (`apps/web/`)

| File | Purpose |
|------|---------|
| `src/components/files/FileUpload.tsx` | File upload button and drag-and-drop interface |
| `src/components/files/FilePanel.tsx` | Panel displaying uploaded files and their profiles |
| `src/components/charts/PlotlyChart.tsx` | Plotly chart renderer for SSE chart events |
| `src/components/tables/DataTable.tsx` | Table renderer for SSE table events |

## 4. Setup Instructions

### Prerequisites

- Python 3.12
- Node.js 22
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node.js package manager)

### Backend Setup

```bash
cd apps/api
uv sync
```

### Frontend Setup

```bash
cd apps/web
pnpm install
```

### Environment Variables

Create `apps/api/.env` with the following Phase 2 variables (see `app/settings.py` for all options):

| Variable | Default | Description |
|----------|---------|-------------|
| `FILE_STORAGE_PATH` | `./storage/uploads` | Directory for uploaded files |
| `DATA_SANDBOX_TIMEOUT_SECONDS` | `30` | Max execution time for sandbox code |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum file upload size |
| `GROQ_API_KEY` | (required) | API key for Groq LLM provider |
| `CEREBRAS_API_KEY` | (optional) | API key for Cerebras provider |
| `GEMINI_API_KEY` | (optional) | API key for Gemini provider |

### Storage Directory

The storage directory (`apps/api/storage/uploads/`) is created automatically when the first file is uploaded. Each user gets a subdirectory:

```
apps/api/storage/uploads/
  {user_id}/
    {file_uuid}_{original_filename}
```

## 5. API Endpoints

### Upload File

```http
POST /api/v1/files
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
conversation_id: (optional UUID)
```

**Response** (`201 Created`):

```json
{
  "id": "a1b2c3d4-...",
  "user_id": "u1234-...",
  "conversation_id": null,
  "name": "sales.csv",
  "mime": "text/csv",
  "size_bytes": 102400,
  "kind": "data",
  "status": "ready",
  "profile_json": {
    "n_rows": 1000,
    "n_cols": 5,
    "columns": [...],
    "head_preview": [...],
    "memory_mb": 0.042
  },
  "created_at": "2025-01-28T12:00:00Z"
}
```

### List Files

```http
GET /api/v1/files
Authorization: Bearer {token}
```

**Response** (`200 OK`): Array of `FileResponse` objects.

### Get File Detail

```http
GET /api/v1/files/{id}
Authorization: Bearer {token}
```

**Response** (`200 OK`): Single `FileResponse` with full `profile_json`.

### Preview File Data

```http
GET /api/v1/files/{id}/preview?rows=20
Authorization: Bearer {token}
```

**Response** (`200 OK`):

```json
{
  "columns": ["product", "revenue", "quantity", "date", "region"],
  "rows": [
    {"product": "Widget A", "revenue": 1500.0, "quantity": 50, "date": "2024-01-01", "region": "East"},
    ...
  ],
  "total_rows": 1000
}
```

### Delete File

```http
DELETE /api/v1/files/{id}
Authorization: Bearer {token}
```

**Response**: `204 No Content`

### Send Message with Data Context

```http
POST /api/v1/conversations/{id}/messages
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "Show me top 5 products by revenue as a bar chart",
  "file_ids": ["a1b2c3d4-..."]
}
```

**Response**: SSE stream (see Section 6).

## 6. SSE Event Format

The chat streaming endpoint emits Server-Sent Events with the following types:

### `event: token`

Incremental text tokens from the LLM response.

```
event: token
data: {"text": "I'll analyze the revenue data and create a bar chart for you.\n\n"}
```

### `event: chart`

A Plotly figure specification for rendering interactive charts.

```
event: chart
data: {"data": [{"type": "bar", "x": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E"], "y": [15000, 12000, 9500, 8200, 7100], "marker": {"color": "#636EFA"}}], "layout": {"title": {"text": "Top 5 Products by Revenue"}, "xaxis": {"title": {"text": "product"}}, "yaxis": {"title": {"text": "revenue"}}}}
```

### `event: table`

Tabular data with column names and row objects.

```
event: table
data: {"columns": ["product", "revenue"], "rows": [{"product": "Widget A", "revenue": 15000}, {"product": "Widget B", "revenue": 12000}, {"product": "Widget C", "revenue": 9500}, {"product": "Widget D", "revenue": 8200}, {"product": "Widget E", "revenue": 7100}]}
```

### `event: code`

The Python code that was executed in the sandbox.

```
event: code
data: {"code": "import pandas as pd\nimport plotly.express as px\n\ntop5 = df.groupby('product')['revenue'].sum().nlargest(5).reset_index()\nresult_table = top5\nfig = px.bar(top5, x='product', y='revenue', title='Top 5 Products by Revenue')"}
```

### `event: done`

Signals the end of the response stream.

```
event: done
data: {"message_id": "msg-uuid-...", "usage": {"prompt_tokens": 450, "completion_tokens": 120}}
```

## 7. Sandbox Security

The sandbox (`app/data/sandbox.py`) implements multiple layers of security:

### AST-Based Code Safety Checking

Before execution, the `check_code_safety()` function parses the code into an AST and walks every node to detect dangerous patterns:

- Import statements are checked against the blocked list
- `__import__()` calls are explicitly blocked

### Blocked Modules

The following modules are blocked from import:

```python
BLOCKED_MODULES = {
    "os", "subprocess", "sys", "socket", "shutil",
    "importlib", "ctypes", "signal", "multiprocessing", "threading",
}
```

### Subprocess Isolation

- Code runs in a separate Python subprocess via `subprocess.run()`
- A configurable timeout (default 30 seconds, set via `DATA_SANDBOX_TIMEOUT_SECONDS`) kills long-running processes
- Output is captured (`capture_output=True`) and parsed for structured results

### No Network Access

Sandbox code cannot make network requests because `socket` is in the blocked modules list.

### Pre-Loaded DataFrame

The wrapper script automatically loads the user's file as a `df` variable:

```python
# Available in sandbox:
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv(file_path)  # or pd.read_excel() for XLSX
```

User code assigns to `result_table` (DataFrame) and/or `fig` (Plotly figure) to produce output.

## 8. How to Test

### Running Backend Tests

```bash
cd apps/api
uv run pytest tests/ -v
```

### Running Lint

```bash
cd apps/api
uv run ruff check .
```

### Building Frontend

```bash
cd apps/web
pnpm build
```

### Manual Testing - File Upload

```bash
# Upload a CSV file
curl -X POST http://localhost:8000/api/v1/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sales.csv"

# List uploaded files
curl http://localhost:8000/api/v1/files \
  -H "Authorization: Bearer YOUR_TOKEN"

# Preview file data
curl "http://localhost:8000/api/v1/files/{file_id}/preview?rows=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Manual Testing - Chat with Data

```bash
# Send a data analysis message (SSE stream)
curl -N -X POST http://localhost:8000/api/v1/conversations/{conv_id}/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Show me a summary of the data", "file_ids": ["FILE_ID_HERE"]}'
```

## 9. Example Conversation Flow

Here is a complete end-to-end flow showing how data analysis works:

### Step 1: User Uploads `sales.csv`

The user uploads a CSV file containing sales data (1000 rows, 5 columns: product, revenue, quantity, date, region).

```
POST /api/v1/files -> 201 Created
```

The system auto-profiles the file:
- Detects 5 columns with types (object, float64, int64, object, object)
- Computes min/max/mean for numeric columns
- Identifies top values for categorical columns
- Stores the profile in `profile_json`

### Step 2: User Asks a Question

> "Show me top 5 products by revenue as a bar chart"

The frontend sends this message with `file_ids` referencing the uploaded file.

### Step 3: System Builds LLM Context

The backend fetches the file profile and calls `build_data_analysis_system_prompt()` to create a system prompt including:

```
Column details:
  - product (object): 25 unique values, 0% missing, top: 'Widget A' (42), 'Widget B' (38)...
  - revenue (float64): 1000 unique values, 0% missing, range [10.5, 15000.0], mean=2450.30
  ...
```

### Step 4: LLM Generates Code

The LLM returns a response containing:

```python
top5 = df.groupby('product')['revenue'].sum().nlargest(5).reset_index()
result_table = top5
fig = px.bar(top5, x='product', y='revenue', title='Top 5 Products by Revenue')
```

### Step 5: Sandbox Executes Code

The `SandboxExecutor`:
1. Checks code safety via AST parsing (passes)
2. Wraps code with DataFrame loading and output serialization
3. Executes in a subprocess with 30s timeout
4. Parses the JSON output containing `table_data` and `chart_spec`

### Step 6: Frontend Receives and Renders

The SSE stream delivers:

1. `event: token` - Explanatory text from the LLM
2. `event: code` - The executed Python code
3. `event: table` - Top 5 products as structured data
4. `event: chart` - Plotly bar chart specification
5. `event: done` - Completion signal

The frontend renders:
- Text in a `MessageBubble`
- The chart via `PlotlyChart.tsx` (interactive, zoomable)
- The table via `DataTable.tsx` (sortable columns)

## 10. Deployment Notes

### Storage Configuration

- Set `FILE_STORAGE_PATH` to a **persistent volume** in production (e.g., `/data/uploads/`)
- Ensure the storage directory has write permissions for the application process
- For production at scale, consider switching to S3-compatible object storage (MinIO, AWS S3)

### Sandbox Configuration

- Set `DATA_SANDBOX_TIMEOUT_SECONDS` appropriately for your workload (default: 30s)
- Large datasets may require higher timeouts
- For production, consider switching to [E2B](https://e2b.dev/) sandboxes for stronger isolation

### Resource Considerations

- Each sandbox execution spawns a subprocess - monitor system resources under load
- Auto-profiling reads the entire file into memory - the `MAX_UPLOAD_SIZE_MB` limit (default: 50) prevents OOM
- Plotly chart specs can be large - consider compression for bandwidth-constrained deployments

### Security Checklist

- [ ] `FILE_STORAGE_PATH` is outside the web root
- [ ] Storage directory permissions are restricted (e.g., `750`)
- [ ] `DATA_SANDBOX_TIMEOUT_SECONDS` is set to prevent resource exhaustion
- [ ] `MAX_UPLOAD_SIZE_MB` is appropriate for your infrastructure
- [ ] JWT_SECRET_KEY is changed from the default in production
