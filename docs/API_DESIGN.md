# uReport AI - API Design Specification

## Base URL & Conventions

```
Base URL: /api/v1
Content-Type: application/json (kecuali file upload: multipart/form-data)
Authentication: Bearer token (JWT) di header Authorization
Streaming: Server-Sent Events (text/event-stream)
```

### Standard Response Format

```json
// Success
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "total": 100, "per_page": 20 }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [{ "field": "email", "message": "This field is required" }]
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | Kapan Digunakan |
|------|---------|-----------------|
| 200 | OK | Request berhasil |
| 201 | Created | Resource berhasil dibuat |
| 204 | No Content | Delete berhasil |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Token tidak valid/expired |
| 403 | Forbidden | Tidak punya akses |
| 404 | Not Found | Resource tidak ditemukan |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 1. Authentication Endpoints

### POST /api/v1/auth/register

Registrasi user baru.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirmation": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-xxx",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**Validation Rules:**
- name: required, min 2 chars, max 100 chars
- email: required, valid email format, unique
- password: required, min 8 chars, harus ada huruf besar, kecil, dan angka

---

### POST /api/v1/auth/login

Login dan mendapatkan access token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-xxx",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "preferences": {
        "theme": "dark",
        "default_provider": "groq"
      }
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

### POST /api/v1/auth/logout

Logout dan invalidate token.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "success": true,
  "data": { "message": "Logged out successfully" }
}
```

---

### POST /api/v1/auth/refresh

Refresh access token menggunakan refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "new-eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

## 2. Conversations Endpoints

### GET /api/v1/conversations

Ambil semua percakapan milik user (paginated).

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 50)
- `search` (optional, cari berdasarkan title)
- `archived` (optional, boolean)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "conv-uuid-1",
      "title": "Analisis Penjualan Q1",
      "model_provider": "groq",
      "model_name": "llama-3.1-70b",
      "last_message_preview": "Berdasarkan data yang Anda berikan...",
      "has_attachments": true,
      "message_count": 15,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:22:00Z"
    }
  ],
  "meta": { "page": 1, "total": 42, "per_page": 20, "total_pages": 3 }
}
```

---

### POST /api/v1/conversations

Buat percakapan baru.

**Request:**
```json
{
  "title": "Analisis Data Baru",
  "model_provider": "groq",
  "model_name": "llama-3.1-70b"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "conv-uuid-new",
    "title": "Analisis Data Baru",
    "model_provider": "groq",
    "model_name": "llama-3.1-70b",
    "messages": [],
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

---

### GET /api/v1/conversations/:id

Ambil detail percakapan beserta messages.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "conv-uuid-1",
    "title": "Analisis Penjualan Q1",
    "model_provider": "groq",
    "model_name": "llama-3.1-70b",
    "attachments": [
      {
        "id": "att-uuid-1",
        "original_name": "data_penjualan.xlsx",
        "row_count": 1500,
        "col_count": 8,
        "status": "ready"
      }
    ],
    "messages": [
      {
        "id": "msg-uuid-1",
        "role": "user",
        "content": "Analisis data penjualan ini",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": "msg-uuid-2",
        "role": "assistant",
        "content": "Berdasarkan data yang Anda berikan...",
        "metadata": { "provider": "groq", "latency_ms": 1200 },
        "charts": [
          {
            "id": "chart-uuid-1",
            "chart_type": "bar",
            "title": "Penjualan per Kategori"
          }
        ],
        "created_at": "2024-01-15T10:30:05Z"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### PATCH /api/v1/conversations/:id

Update percakapan (rename, archive, change model).

**Request:**
```json
{
  "title": "Analisis Penjualan Q1 2024 - Final",
  "is_archived": false,
  "model_provider": "gemini"
}
```

---

### DELETE /api/v1/conversations/:id

Hapus percakapan beserta semua messages dan attachments.

**Response (204):** No content

---

## 3. Messages Endpoints

### POST /api/v1/conversations/:id/messages

Kirim pesan baru dan dapatkan respons AI (streaming).

**Request:**
```json
{
  "content": "Buatkan grafik penjualan per bulan dari data yang sudah diupload",
  "attachment_ids": ["att-uuid-1"],
  "stream": true
}
```

**Response (Streaming - text/event-stream):**
```
event: message_start
data: {"message_id": "msg-uuid-new", "role": "assistant"}

event: content_delta
data: {"delta": "Berdasarkan "}

event: content_delta
data: {"delta": "data penjualan "}

event: content_delta
data: {"delta": "yang Anda berikan, "}

event: chart
data: {"chart_type": "bar", "title": "Penjualan per Bulan", "data": [...], "config": {...}}

event: content_delta
data: {"delta": "\n\nDari grafik di atas terlihat bahwa..."}

event: message_end
data: {"message_id": "msg-uuid-new", "token_count": 250, "latency_ms": 1500}
```

**Non-streaming Response (stream: false) - Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "msg-uuid-new",
    "role": "assistant",
    "content": "Berdasarkan data penjualan yang Anda berikan...",
    "charts": [
      {
        "chart_type": "bar",
        "title": "Penjualan per Bulan",
        "data": [
          {"bulan": "Jan", "penjualan": 150000000},
          {"bulan": "Feb", "penjualan": 180000000}
        ],
        "config": {
          "xAxis": {"dataKey": "bulan"},
          "yAxis": {"label": "Penjualan (Rp)"}
        }
      }
    ],
    "tables": [],
    "metadata": {
      "provider": "groq",
      "model": "llama-3.1-70b",
      "input_tokens": 150,
      "output_tokens": 250,
      "latency_ms": 1500
    },
    "created_at": "2024-01-15T10:31:00Z"
  }
}
```

---

### GET /api/v1/conversations/:id/messages

Ambil history pesan (paginated, default: 50 latest).

**Query Parameters:**
- `limit` (default: 50)
- `before` (cursor: message_id, untuk pagination ke atas)
- `after` (cursor: message_id, untuk pagination ke bawah)

---

### POST /api/v1/messages/:id/regenerate

Regenerate respons AI untuk pesan tertentu.

**Request:**
```json
{
  "provider": "cerebras",
  "model": "llama-3.1-8b"
}
```

---

## 4. File Upload Endpoints

### POST /api/v1/files/upload

Upload file Excel/CSV untuk analisis.

**Request:** `multipart/form-data`
- `file`: Binary file (max 50MB)
- `conversation_id`: UUID (optional, link ke percakapan)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "att-uuid-new",
    "original_name": "data_penjualan_2024.xlsx",
    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "file_size": 2048576,
    "status": "ready",
    "schema_info": {
      "columns": [
        {"name": "tanggal", "type": "datetime64", "sample": "2024-01-01"},
        {"name": "produk", "type": "object", "sample": "Widget A"},
        {"name": "kategori", "type": "object", "sample": "Elektronik"},
        {"name": "jumlah", "type": "int64", "sample": 150},
        {"name": "harga_satuan", "type": "float64", "sample": 25000},
        {"name": "total", "type": "float64", "sample": 3750000},
        {"name": "region", "type": "object", "sample": "Jawa Barat"},
        {"name": "salesperson", "type": "object", "sample": "Budi"}
      ],
      "sheet_names": ["Sheet1"],
      "active_sheet": "Sheet1"
    },
    "preview": [
      {"tanggal": "2024-01-01", "produk": "Widget A", "kategori": "Elektronik", "jumlah": 150, "harga_satuan": 25000, "total": 3750000, "region": "Jawa Barat", "salesperson": "Budi"},
      {"tanggal": "2024-01-02", "produk": "Widget B", "kategori": "Fashion", "jumlah": 80, "harga_satuan": 50000, "total": 4000000, "region": "DKI Jakarta", "salesperson": "Ani"}
    ],
    "statistics": {
      "row_count": 1500,
      "col_count": 8,
      "numeric_summary": {
        "jumlah": {"mean": 120.5, "min": 1, "max": 500, "std": 85.3},
        "total": {"mean": 4500000, "min": 25000, "max": 25000000, "std": 3200000}
      }
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Validation:**
- Allowed types: .xlsx, .xls, .csv
- Max size: 50MB
- Max rows: 1,000,000
- Max columns: 500

---

### GET /api/v1/files/:id

Ambil informasi file yang sudah diupload.

---

### GET /api/v1/files/:id/preview

Ambil preview data (configurable rows).

**Query Parameters:**
- `rows` (default: 10, max: 100)
- `sheet` (optional, nama sheet untuk Excel)

---

### DELETE /api/v1/files/:id

Hapus file dari storage dan database.

---

## 5. Analysis Endpoints

### POST /api/v1/analysis/query

Jalankan query analisis pada data yang sudah diupload.

**Request:**
```json
{
  "file_id": "att-uuid-1",
  "query": "Berapa total penjualan per kategori produk?",
  "output_format": "table_and_chart"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "query_interpretation": "GROUP BY kategori, SUM(total)",
    "table": {
      "columns": ["kategori", "total_penjualan", "jumlah_transaksi"],
      "rows": [
        ["Elektronik", 450000000, 320],
        ["Fashion", 380000000, 280],
        ["Makanan", 220000000, 450],
        ["Otomotif", 180000000, 85]
      ]
    },
    "chart": {
      "chart_type": "bar",
      "title": "Total Penjualan per Kategori",
      "data": [
        {"kategori": "Elektronik", "total_penjualan": 450000000},
        {"kategori": "Fashion", "total_penjualan": 380000000},
        {"kategori": "Makanan", "total_penjualan": 220000000},
        {"kategori": "Otomotif", "total_penjualan": 180000000}
      ],
      "config": {
        "xAxis": {"dataKey": "kategori"},
        "yAxis": {"label": "Total Penjualan (Rp)"},
        "colors": ["#8884d8"]
      }
    },
    "insight": "Kategori Elektronik memimpin penjualan dengan total Rp 450 juta (36% dari total). Fashion di posisi kedua dengan Rp 380 juta (31%)."
  }
}
```

---

### POST /api/v1/analysis/chart

Generate chart spesifik dari data.

**Request:**
```json
{
  "file_id": "att-uuid-1",
  "chart_type": "line",
  "x_axis": "tanggal",
  "y_axis": ["total"],
  "group_by": "kategori",
  "aggregation": "sum",
  "date_granularity": "month"
}
```

---

### POST /api/v1/analysis/statistics

Dapatkan statistical summary dari data.

**Request:**
```json
{
  "file_id": "att-uuid-1",
  "columns": ["total", "jumlah"],
  "operations": ["describe", "correlation", "distribution"]
}
```

---

## 6. Reports Endpoints

### POST /api/v1/reports

Buat laporan baru (trigger generation).

**Request:**
```json
{
  "title": "Laporan Analisis Penjualan Q1 2024",
  "template_id": "template-uuid-1",
  "description": "Laporan lengkap analisis penjualan kuartal 1 tahun 2024",
  "source_files": ["att-uuid-1", "att-uuid-2"],
  "source_conversations": ["conv-uuid-1"],
  "custom_instructions": "Fokus pada perbandingan antar region dan trend bulanan",
  "provider": "gemini"
}
```

**Response (202 - Accepted):**
```json
{
  "success": true,
  "data": {
    "id": "report-uuid-new",
    "title": "Laporan Analisis Penjualan Q1 2024",
    "status": "generating",
    "estimated_time_seconds": 120,
    "sections_total": 5,
    "sections_completed": 0,
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

---

### GET /api/v1/reports

Ambil daftar laporan milik user.

**Query Parameters:**
- `page`, `per_page`
- `status` (filter: draft, generating, completed, error)

---

### GET /api/v1/reports/:id

Ambil detail laporan beserta semua sections.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "report-uuid-1",
    "title": "Laporan Analisis Penjualan Q1 2024",
    "status": "completed",
    "sections": [
      {
        "id": "section-uuid-1",
        "section_order": 1,
        "section_title": "BAB I - Pendahuluan",
        "content": "## 1.1 Latar Belakang\n\nLaporan ini menyajikan...",
        "word_count": 850,
        "status": "completed"
      },
      {
        "id": "section-uuid-2",
        "section_order": 2,
        "section_title": "BAB II - Tinjauan Data",
        "content": "## 2.1 Sumber Data\n\nData yang dianalisis...",
        "charts": [{"chart_type": "bar", "data": [...]}],
        "word_count": 1200,
        "status": "completed"
      }
    ],
    "total_word_count": 5200,
    "generated_at": "2024-01-15T15:02:00Z",
    "pdf_url": null
  }
}
```

---

### PUT /api/v1/reports/:id/sections/:section_id

Edit konten section/BAB.

**Request:**
```json
{
  "content": "## 1.1 Latar Belakang\n\nLaporan ini menyajikan analisis mendalam...(edited content)"
}
```

---

### POST /api/v1/reports/:id/export-pdf

Generate PDF dari laporan.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "pdf_url": "/api/v1/files/download/report-uuid-1.pdf",
    "file_size": 2048576,
    "page_count": 24,
    "generated_at": "2024-01-15T15:10:00Z"
  }
}
```

---

### GET /api/v1/reports/:id/progress

Cek progress report generation (via polling atau WebSocket).

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "generating",
    "sections_total": 5,
    "sections_completed": 3,
    "current_section": "BAB IV - Hasil dan Pembahasan",
    "estimated_remaining_seconds": 45
  }
}
```

---

## 7. LLM Settings Endpoints

### GET /api/v1/llm/providers

Ambil daftar provider yang tersedia.

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "name": "groq",
      "display_name": "Groq",
      "description": "Ultra-low latency inference engine",
      "is_configured": true,
      "is_available": true,
      "models": [
        {"id": "llama-3.1-70b-versatile", "name": "LLaMA 3.1 70B", "context_window": 131072},
        {"id": "llama-3.1-8b-instant", "name": "LLaMA 3.1 8B", "context_window": 131072},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "context_window": 32768}
      ]
    },
    {
      "name": "cerebras",
      "display_name": "Cerebras",
      "description": "Fastest inference with Cerebras hardware",
      "is_configured": true,
      "is_available": true,
      "models": [
        {"id": "llama-3.1-70b", "name": "LLaMA 3.1 70B", "context_window": 8192},
        {"id": "llama-3.1-8b", "name": "LLaMA 3.1 8B", "context_window": 8192}
      ]
    },
    {
      "name": "gemini",
      "display_name": "Google Gemini",
      "description": "Multimodal AI with large context window",
      "is_configured": true,
      "is_available": true,
      "models": [
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context_window": 1048576},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context_window": 1048576}
      ]
    },
    {
      "name": "sumopod",
      "display_name": "Sumopod",
      "description": "Custom self-hosted model",
      "is_configured": false,
      "is_available": false,
      "models": []
    }
  ]
}
```

---

### PUT /api/v1/llm/active

Set provider dan model aktif untuk user.

**Request:**
```json
{
  "provider": "groq",
  "model": "llama-3.1-70b-versatile"
}
```

---

### POST /api/v1/llm/test

Test koneksi ke provider.

**Request:**
```json
{
  "provider": "cerebras",
  "model": "llama-3.1-8b"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "connected",
    "response_time_ms": 250,
    "test_response": "Hello! I'm working correctly.",
    "model_info": {
      "id": "llama-3.1-8b",
      "context_window": 8192
    }
  }
}
```

---

## 8. RAG / Knowledge Base Endpoints

### POST /api/v1/knowledge/documents

Upload dokumen ke knowledge base.

**Request:** `multipart/form-data`
- `file`: Binary file (PDF, DOCX, TXT, MD)
- `title`: String
- `category`: String (optional)

**Response (202):**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid-new",
    "title": "Panduan Analisis Penjualan",
    "status": "processing",
    "message": "Document is being processed and indexed"
  }
}
```

---

### GET /api/v1/knowledge/documents

List semua dokumen di knowledge base.

---

### DELETE /api/v1/knowledge/documents/:id

Hapus dokumen dari knowledge base (termasuk chunks dan embeddings).

---

### POST /api/v1/knowledge/search

Search knowledge base (untuk testing/debugging RAG).

**Request:**
```json
{
  "query": "metode analisis penjualan",
  "top_k": 5,
  "threshold": 0.7
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "chunk_id": "chunk-uuid-1",
        "document_title": "Panduan Analisis Penjualan",
        "content": "Metode analisis penjualan yang umum digunakan meliputi...",
        "similarity_score": 0.89,
        "metadata": { "page": 5, "heading": "Bab 3 - Metode" }
      },
      {
        "chunk_id": "chunk-uuid-2",
        "document_title": "Buku Statistik Bisnis",
        "content": "Dalam menganalisis tren penjualan, pendekatan time-series...",
        "similarity_score": 0.82,
        "metadata": { "page": 12, "heading": "Time Series Analysis" }
      }
    ],
    "query_embedding_time_ms": 50,
    "search_time_ms": 15
  }
}
```

---

## Rate Limiting

| Endpoint Category | Rate Limit | Window |
|-------------------|-----------|--------|
| Auth endpoints | 5 requests | per minute |
| Chat messages | 30 requests | per minute |
| File uploads | 10 requests | per minute |
| Analysis queries | 20 requests | per minute |
| Report generation | 5 requests | per hour |
| General API | 100 requests | per minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1705312800
```

---

## WebSocket Events (Real-time)

### Connection

```
ws://localhost:3000/api/v1/ws?token=<access_token>
```

### Events dari Server

```json
// Report progress
{"event": "report:progress", "data": {"report_id": "xxx", "section": 3, "total": 5}}

// Report completed
{"event": "report:completed", "data": {"report_id": "xxx"}}

// File processing done
{"event": "file:ready", "data": {"file_id": "xxx", "status": "ready"}}

// Document indexed
{"event": "document:indexed", "data": {"document_id": "xxx", "chunks": 45}}
```
