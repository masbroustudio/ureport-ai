# 10 — API Design

## 10.1 Base URL & Konvensi

```
Base URL        : /api/v1
Framework       : FastAPI (Python 3.11+)
Validasi        : Pydantic v2 (BaseModel)
Content-Type    : application/json (default)
                  multipart/form-data (file upload)
                  text/event-stream (SSE streaming)
Authentication  : Bearer token (JWT) di header Authorization
```

### Konvensi Umum

- Semua path menggunakan kebab-case untuk resource, snake_case untuk field JSON
- UUID v4 untuk semua resource identifier
- Timestamp menggunakan ISO 8601 format (UTC): `2024-01-15T10:30:00Z`
- Semua endpoint memerlukan JWT kecuali `/auth/signup`, `/auth/signin`, `/auth/oauth/*`
- Response selalu dibungkus dalam standard envelope (lihat bagian 10.2)
- FastAPI dependency injection `get_current_user` untuk autentikasi di setiap route
- Pydantic v2 schema digunakan untuk validasi request body dan response serialization

---

## 10.2 Standard Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Resource Name",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Success Response (List dengan Cursor Pagination)

```json
{
  "success": true,
  "data": [
    { "id": "uuid-1", "title": "Item 1" },
    { "id": "uuid-2", "title": "Item 2" }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6InV1aWQtMiIsImNyZWF0ZWRfYXQiOiIyMDI0LTAxLTE1VDEwOjMwOjAwWiJ9",
    "has_more": true,
    "limit": 20
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email tidak valid",
    "details": [
      { "field": "email", "message": "Format email tidak valid" },
      { "field": "password", "message": "Minimal 8 karakter" }
    ]
  }
}
```

---

## 10.3 Common HTTP Status Codes

| Code | Status | Deskripsi |
|------|--------|-----------|
| 200 | OK | Request berhasil diproses |
| 201 | Created | Resource baru berhasil dibuat |
| 202 | Accepted | Request diterima, diproses secara async |
| 204 | No Content | Berhasil (DELETE), tidak ada body |
| 400 | Bad Request | Validasi gagal / request tidak valid |
| 401 | Unauthorized | Token tidak ada, expired, atau tidak valid |
| 403 | Forbidden | User tidak punya akses ke resource |
| 404 | Not Found | Resource tidak ditemukan |
| 409 | Conflict | Duplikasi (misal email sudah terdaftar) |
| 413 | Payload Too Large | File melebihi batas ukuran |
| 422 | Unprocessable Entity | Request valid tapi tidak bisa diproses |
| 429 | Too Many Requests | Rate limit terlampaui |
| 500 | Internal Server Error | Error tidak terduga di server |
| 503 | Service Unavailable | LLM provider sedang down |

---

## 10.4 Authentication & Authorization

### Mekanisme

- JWT digenerate oleh Auth.js (Next.js frontend) saat login/signup
- Token dikirim via header `Authorization: Bearer <token>`
- FastAPI memverifikasi JWT menggunakan dependency injection:

```python
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user
from app.schemas.user import UserInDB

@router.get("/conversations")
async def list_conversations(
    current_user: UserInDB = Depends(get_current_user)
):
    # current_user sudah terverifikasi
    ...
```

### Token Lifecycle

| Field | Nilai |
|-------|-------|
| Algorithm | HS256 |
| Access Token Expiry | 7 hari |
| Refresh Token Expiry | 30 hari |
| Storage (client) | httpOnly cookie |

### RBAC (Role-Based Access Control)

- V1: Semua user memiliki role `user`
- V2: Tambahan role `admin` dan `viewer`
- Pengecekan role dilakukan di level dependency injection

---

## 10.5 Endpoint Documentation

### 10.5.1 Auth Endpoints

#### POST /api/v1/auth/signup

Registrasi user baru dengan email dan password.

**Request:**
```json
{
  "name": "Budi Santoso",
  "email": "budi@example.com",
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
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Budi Santoso",
      "email": "budi@example.com",
      "role": "user",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjQ3YWMxMGIifQ.abc123",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCJ9.xyz789",
    "expires_in": 604800
  }
}
```

**Validation Rules:**
- `name`: required, min 2, max 100 karakter
- `email`: required, format email valid, unique di database
- `password`: required, min 8 karakter, harus mengandung huruf besar, huruf kecil, dan angka
- `password_confirmation`: required, harus sama dengan `password`

---

#### POST /api/v1/auth/signin

Login dan mendapatkan access token.

**Request:**
```json
{
  "email": "budi@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Budi Santoso",
      "email": "budi@example.com",
      "role": "user",
      "avatar_url": "https://lh3.googleusercontent.com/a/photo.jpg",
      "preferences": {
        "theme": "dark",
        "default_provider": "groq",
        "default_model": "llama-3.1-70b-versatile"
      }
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjQ3YWMxMGIifQ.newtoken",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCJ9.newrefresh",
    "expires_in": 604800
  }
}
```

**Validation Rules:**
- `email`: required, format email valid
- `password`: required

**Error Cases:**
- 401: Email atau password salah
- 429: Terlalu banyak percobaan login (5x dalam 15 menit)

---

#### GET /api/v1/auth/oauth/google

Redirect ke Google OAuth consent screen.

**Response (302):** Redirect ke Google OAuth URL

**Notes:**
- Menggunakan Auth.js OAuth flow
- Callback URL: `/api/v1/auth/oauth/google/callback`
- Scope: `openid email profile`

---

#### GET /api/v1/auth/oauth/google/callback

Callback dari Google setelah user memberikan consent.

**Query Parameters:**
- `code`: Authorization code dari Google
- `state`: CSRF state token

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Budi Santoso",
      "email": "budi@gmail.com",
      "role": "user",
      "avatar_url": "https://lh3.googleusercontent.com/a/photo.jpg",
      "oauth_provider": "google"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjQ3YWMxMGIifQ.oauthtoken",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCJ9.oauthrefresh",
    "expires_in": 604800,
    "is_new_user": true
  }
}
```

---

#### POST /api/v1/auth/signout

Invalidate session dan token.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Berhasil logout"
  }
}
```

**Notes:**
- Token ditambahkan ke blacklist di Redis
- httpOnly cookie dihapus dari client

---

#### GET /api/v1/auth/me

Mendapatkan profil user yang sedang login.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Budi Santoso",
    "email": "budi@example.com",
    "role": "user",
    "avatar_url": "https://lh3.googleusercontent.com/a/photo.jpg",
    "oauth_provider": null,
    "preferences": {
      "theme": "dark",
      "default_provider": "groq",
      "default_model": "llama-3.1-70b-versatile",
      "language": "id"
    },
    "usage_this_month": {
      "total_tokens": 45200,
      "total_cost_usd": 0.12
    },
    "created_at": "2024-01-10T08:00:00Z"
  }
}
```

---

#### POST /api/v1/auth/refresh

Refresh access token menggunakan refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVmcmVzaCJ9.xyz789"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjQ3YWMxMGIifQ.renewed",
    "expires_in": 604800
  }
}
```

**Error Cases:**
- 401: Refresh token expired atau tidak valid

---

### 10.5.2 Conversations Endpoints

#### GET /api/v1/conversations

Ambil daftar percakapan milik user (cursor-based pagination).

**Query Parameters:**
- `limit` (default: 20, max: 50)
- `cursor` (optional, cursor dari response sebelumnya)
- `search` (optional, cari berdasarkan title)
- `archived` (optional, boolean filter arsip)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Analisis Penjualan Q1 2024",
      "model": "llama-3.1-70b-versatile",
      "pinned": false,
      "archived": false,
      "last_message_preview": "Berdasarkan data yang Anda berikan, tren penjualan...",
      "message_count": 15,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:22:00Z"
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "title": "Visualisasi Data Keuangan",
      "model": "gemini-1.5-pro",
      "pinned": true,
      "archived": false,
      "last_message_preview": "Berikut grafik cashflow bulanan...",
      "message_count": 8,
      "created_at": "2024-01-14T09:00:00Z",
      "updated_at": "2024-01-14T16:45:00Z"
    }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6ImIyYzNkNGU1IiwidXBkYXRlZF9hdCI6IjIwMjQtMDEtMTRUMTY6NDU6MDBaIn0=",
    "has_more": true,
    "limit": 20
  }
}
```

---

#### POST /api/v1/conversations

Buat percakapan baru.

**Request:**
```json
{
  "title": "Analisis Data Penjualan",
  "model": "llama-3.1-70b-versatile"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "title": "Analisis Data Penjualan",
    "model": "llama-3.1-70b-versatile",
    "pinned": false,
    "archived": false,
    "message_count": 0,
    "created_at": "2024-01-15T15:00:00Z",
    "updated_at": "2024-01-15T15:00:00Z"
  }
}
```

**Validation Rules:**
- `title`: optional (auto-generated dari pesan pertama jika kosong), max 200 karakter
- `model`: optional, default dari user preferences

---

#### GET /api/v1/conversations/{id}

Ambil detail percakapan.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Analisis Penjualan Q1 2024",
    "model": "llama-3.1-70b-versatile",
    "pinned": false,
    "archived": false,
    "files": [
      {
        "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
        "name": "data_penjualan.xlsx",
        "size_bytes": 2048576,
        "status": "ready"
      }
    ],
    "message_count": 15,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:22:00Z"
  }
}
```

---

#### PATCH /api/v1/conversations/{id}

Update percakapan (rename, pin, archive, ganti model).

**Request:**
```json
{
  "title": "Analisis Penjualan Q1 2024 - Final",
  "pinned": true,
  "archived": false,
  "model": "gemini-1.5-pro"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Analisis Penjualan Q1 2024 - Final",
    "model": "gemini-1.5-pro",
    "pinned": true,
    "archived": false,
    "updated_at": "2024-01-15T15:30:00Z"
  }
}
```

**Validation Rules:**
- `title`: max 200 karakter
- `model`: harus model yang tersedia di sistem
- Minimal satu field harus dikirim

---

#### DELETE /api/v1/conversations/{id}

Hapus percakapan beserta semua messages, tool_calls, dan file associations.

**Response (204):** No content

**Notes:**
- Cascade delete ke messages dan tool_calls
- File yang di-attach tidak dihapus (hanya unlink)

---

#### GET /api/v1/conversations/{id}/messages

Ambil daftar pesan dalam percakapan (cursor-based, newest first).

**Query Parameters:**
- `limit` (default: 50, max: 100)
- `cursor` (optional, untuk load more ke atas/bawah)
- `direction` (optional: `before` | `after`, default: `before`)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "e5f6a7b8-c9d0-1234-ef01-345678901234",
      "role": "user",
      "content": "Analisis data penjualan ini dan buatkan grafik tren bulanan",
      "status": "done",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "f6a7b8c9-d0e1-2345-f012-456789012345",
      "role": "assistant",
      "content": "Berdasarkan data yang Anda berikan, berikut analisis tren penjualan bulanan:\n\n## Ringkasan\n- Total penjualan Q1: Rp 1.23 miliar\n- Pertumbuhan MoM rata-rata: 12%\n- Kategori terbaik: Elektronik",
      "status": "done",
      "model": "llama-3.1-70b-versatile",
      "tokens_in": 1250,
      "tokens_out": 380,
      "tool_calls": [
        {
          "id": "tc_001",
          "tool_name": "run_python",
          "duration_ms": 850
        }
      ],
      "created_at": "2024-01-15T10:30:05Z"
    }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6ImU1ZjZhN2I4IiwiY3JlYXRlZF9hdCI6IjIwMjQtMDEtMTVUMTA6MzA6MDBaIn0=",
    "has_more": true,
    "limit": 50
  }
}
```

---

#### POST /api/v1/conversations/{id}/messages

Kirim pesan baru dan terima respons AI via SSE streaming.

**Request:**
```json
{
  "content": "Buatkan grafik penjualan per bulan dari data yang sudah diupload",
  "file_ids": ["d4e5f6a7-b8c9-0123-def0-234567890123"],
  "model": "llama-3.1-70b-versatile"
}
```

**Response (200, Content-Type: text/event-stream):**
```
event: token
data: {"text": "Berdasarkan "}

event: token
data: {"text": "data penjualan "}

event: token
data: {"text": "yang Anda berikan, "}

event: tool_start
data: {"id": "tc_001", "tool": "run_python", "args": {"code": "import pandas as pd\ndf = pd.read_excel('data.xlsx')\nmonthly = df.groupby(df['tanggal'].dt.month)['total'].sum()"}}

event: tool_chunk
data: {"id": "tc_001", "stdout": "Processing 1500 rows..."}

event: tool_end
data: {"id": "tc_001", "output": {"type": "dataframe", "shape": [12, 3]}}

event: chart
data: {"id": "chart_abc", "spec": {"type": "bar", "title": "Penjualan per Bulan", "data": [{"bulan": "Jan", "total": 150000000}, {"bulan": "Feb", "total": 180000000}, {"bulan": "Mar", "total": 210000000}], "config": {"xAxis": "bulan", "yAxis": "total"}}}

event: token
data: {"text": "\n\nDari grafik di atas terlihat bahwa penjualan mengalami peningkatan konsisten..."}

event: done
data: {"message_id": "f6a7b8c9-d0e1-2345-f012-456789012345", "usage": {"tokens_in": 1250, "tokens_out": 380, "cost_usd": 0.002}}
```

**Validation Rules:**
- `content`: required, min 1 karakter, max 32000 karakter
- `file_ids`: optional, array of valid file UUIDs milik user
- `model`: optional, override model percakapan

**Error Cases:**
- 404: Conversation tidak ditemukan
- 429: Rate limit chat (60 req/menit)
- 503: LLM provider sedang tidak tersedia

---

#### POST /api/v1/conversations/{id}/messages/{mid}/regenerate

Regenerate respons AI untuk pesan tertentu (dengan model berbeda opsional).

**Request:**
```json
{
  "model": "gemini-1.5-pro"
}
```

**Response (200, Content-Type: text/event-stream):**

Format sama dengan endpoint send message di atas (SSE streaming).

**Notes:**
- Pesan assistant lama tetap tersimpan (branching)
- `model` opsional, default menggunakan model percakapan saat ini
- Jika `model` diisi, hanya berlaku untuk regenerasi ini

---

### 10.5.3 Files Endpoints

#### POST /api/v1/files

Upload file data (Excel/CSV) untuk analisis. Menggunakan multipart/form-data.

**Request:** `multipart/form-data`
- `file`: Binary file (max 50MB)
- `conversation_id`: UUID (optional, langsung link ke percakapan)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
    "name": "data_penjualan_2024.xlsx",
    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "size_bytes": 2048576,
    "kind": "data",
    "status": "ready",
    "profile_json": {
      "columns": [
        {"name": "tanggal", "type": "datetime64", "sample": "2024-01-01"},
        {"name": "produk", "type": "object", "sample": "Widget A"},
        {"name": "kategori", "type": "object", "sample": "Elektronik"},
        {"name": "jumlah", "type": "int64", "sample": 150},
        {"name": "harga_satuan", "type": "float64", "sample": 25000.0},
        {"name": "total", "type": "float64", "sample": 3750000.0},
        {"name": "region", "type": "object", "sample": "Jawa Barat"},
        {"name": "salesperson", "type": "object", "sample": "Budi"}
      ],
      "sheet_names": ["Sheet1", "Summary"],
      "active_sheet": "Sheet1",
      "row_count": 1500,
      "col_count": 8
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Validation Rules:**
- Tipe file yang diizinkan: `.xlsx`, `.xls`, `.csv`
- Ukuran maksimal: 50MB
- Batas baris: 1.000.000 rows
- Batas kolom: 500 columns
- Nama file: tidak boleh mengandung karakter khusus berbahaya

**Error Cases:**
- 413: File melebihi 50MB
- 415: Tipe file tidak didukung
- 422: File corrupt atau tidak bisa dibaca

---

#### GET /api/v1/files

Ambil daftar file milik user.

**Query Parameters:**
- `limit` (default: 20, max: 50)
- `cursor` (optional)
- `kind` (optional: `data` | `document` | `image`)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
      "name": "data_penjualan_2024.xlsx",
      "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "size_bytes": 2048576,
      "kind": "data",
      "status": "ready",
      "row_count": 1500,
      "col_count": 8,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "e5f6a7b8-c9d0-1234-ef01-345678901234",
      "name": "laporan_keuangan.csv",
      "mime": "text/csv",
      "size_bytes": 512000,
      "kind": "data",
      "status": "ready",
      "row_count": 800,
      "col_count": 12,
      "created_at": "2024-01-14T08:00:00Z"
    }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6ImU1ZjZhN2I4LWM5ZDAtMTIzNCJ9",
    "has_more": false,
    "limit": 20
  }
}
```

---

#### GET /api/v1/files/{id}

Ambil metadata dan profil lengkap file.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
    "name": "data_penjualan_2024.xlsx",
    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "size_bytes": 2048576,
    "kind": "data",
    "status": "ready",
    "profile_json": {
      "columns": [
        {"name": "tanggal", "type": "datetime64", "non_null": 1500, "unique": 365},
        {"name": "produk", "type": "object", "non_null": 1498, "unique": 25},
        {"name": "kategori", "type": "object", "non_null": 1500, "unique": 4},
        {"name": "jumlah", "type": "int64", "non_null": 1500, "min": 1, "max": 500, "mean": 120.5},
        {"name": "harga_satuan", "type": "float64", "non_null": 1500, "min": 5000, "max": 500000, "mean": 75000},
        {"name": "total", "type": "float64", "non_null": 1500, "min": 25000, "max": 25000000, "mean": 4500000},
        {"name": "region", "type": "object", "non_null": 1495, "unique": 8},
        {"name": "salesperson", "type": "object", "non_null": 1500, "unique": 15}
      ],
      "sheet_names": ["Sheet1", "Summary"],
      "row_count": 1500,
      "col_count": 8
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### GET /api/v1/files/{id}/preview

Ambil sample baris data dari file.

**Query Parameters:**
- `n` (default: 20, max: 100) - jumlah baris
- `sheet` (optional, nama sheet untuk file Excel)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "columns": ["tanggal", "produk", "kategori", "jumlah", "harga_satuan", "total", "region", "salesperson"],
    "rows": [
      ["2024-01-01", "Widget A", "Elektronik", 150, 25000, 3750000, "Jawa Barat", "Budi"],
      ["2024-01-01", "Widget B", "Fashion", 80, 50000, 4000000, "DKI Jakarta", "Ani"],
      ["2024-01-02", "Widget C", "Makanan", 200, 15000, 3000000, "Jawa Timur", "Candra"],
      ["2024-01-02", "Widget A", "Elektronik", 120, 25000, 3000000, "Bali", "Dewi"],
      ["2024-01-03", "Widget D", "Otomotif", 30, 250000, 7500000, "Jawa Barat", "Eko"]
    ],
    "total_rows": 1500,
    "showing": 5,
    "sheet": "Sheet1"
  }
}
```

---

#### DELETE /api/v1/files/{id}

Hapus file dari storage (S3) dan database.

**Response (204):** No content

**Notes:**
- File dihapus dari S3 bucket
- Metadata dihapus dari database
- Jika file sedang digunakan di percakapan aktif, tetap bisa dihapus (soft reference)

---

### 10.5.4 Knowledge Base Endpoints

#### POST /api/v1/kb/documents

Upload dokumen ke knowledge base untuk RAG. Proses ingestion berjalan async (parsing, chunking, embedding, store ke Qdrant).

**Request:** `multipart/form-data`
- `file`: Binary file (PDF, DOCX, TXT, MD)
- `title`: String (optional, default dari nama file)
- `tags`: String, comma-separated (optional)
- `language`: String (optional, default: auto-detect)

**Response (202):**
```json
{
  "success": true,
  "data": {
    "id": "a7b8c9d0-e1f2-3456-7890-abcdef123456",
    "title": "Panduan Analisis Penjualan 2024",
    "status": "processing",
    "tags": ["penjualan", "analisis", "2024"],
    "language": "id",
    "message": "Dokumen sedang diproses dan di-index"
  }
}
```

**Validation Rules:**
- Tipe file: `.pdf`, `.docx`, `.txt`, `.md`
- Ukuran maksimal: 20MB
- `title`: max 200 karakter
- `tags`: max 10 tags, masing-masing max 50 karakter

**Notes:**
- Proses async: parsing -> chunking -> embedding -> store di Qdrant
- Status berubah: `processing` -> `ready` | `failed`
- Gunakan GET `/kb/documents/{id}` untuk cek status

---

#### GET /api/v1/kb/documents

List semua dokumen di knowledge base.

**Query Parameters:**
- `limit` (default: 20, max: 50)
- `cursor` (optional)
- `tag` (optional, filter by tag)
- `status` (optional: `processing` | `ready` | `failed`)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "a7b8c9d0-e1f2-3456-7890-abcdef123456",
      "title": "Panduan Analisis Penjualan 2024",
      "status": "ready",
      "tags": ["penjualan", "analisis"],
      "language": "id",
      "chunk_count": 45,
      "created_at": "2024-01-10T08:00:00Z"
    },
    {
      "id": "b8c9d0e1-f2a3-4567-8901-bcdef1234567",
      "title": "Statistik Bisnis - Teori dan Praktik",
      "status": "ready",
      "tags": ["statistik", "teori"],
      "language": "id",
      "chunk_count": 120,
      "created_at": "2024-01-08T14:30:00Z"
    }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6ImI4YzlkMGUxLWYyYTMtNDU2NyJ9",
    "has_more": false,
    "limit": 20
  }
}
```

---

#### GET /api/v1/kb/documents/{id}

Ambil detail dokumen beserta status processing.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "a7b8c9d0-e1f2-3456-7890-abcdef123456",
    "title": "Panduan Analisis Penjualan 2024",
    "status": "ready",
    "tags": ["penjualan", "analisis", "2024"],
    "language": "id",
    "authors": "Tim Riset PT ABC",
    "year": 2024,
    "chunk_count": 45,
    "source_file": {
      "id": "file-uuid-source",
      "name": "panduan_analisis.pdf",
      "size_bytes": 5242880
    },
    "processing_info": {
      "started_at": "2024-01-10T08:00:00Z",
      "completed_at": "2024-01-10T08:02:30Z",
      "duration_seconds": 150
    },
    "created_at": "2024-01-10T08:00:00Z"
  }
}
```

---

#### DELETE /api/v1/kb/documents/{id}

Hapus dokumen dari knowledge base (termasuk chunks dan vektor di Qdrant).

**Response (204):** No content

**Notes:**
- Semua chunks dihapus dari PostgreSQL
- Semua vektor dihapus dari Qdrant collection
- Source file di S3 juga dihapus

---

#### POST /api/v1/kb/search

Semantic search di knowledge base. Mengembalikan chunks yang paling relevan.

**Request:**
```json
{
  "query": "metode analisis tren penjualan seasonal",
  "top_k": 5,
  "filters": {
    "tags": ["penjualan"],
    "language": "id"
  },
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
        "chunk_id": "chunk-uuid-001",
        "document_id": "a7b8c9d0-e1f2-3456-7890-abcdef123456",
        "document_title": "Panduan Analisis Penjualan 2024",
        "content": "Metode analisis tren penjualan seasonal menggunakan decomposition untuk memisahkan komponen trend, seasonal, dan residual. Pendekatan STL (Seasonal and Trend decomposition using Loess) sangat efektif untuk data dengan pola musiman yang kompleks.",
        "similarity_score": 0.92,
        "metadata": {
          "page": 15,
          "section": "Bab 3 - Metode Analisis",
          "chunk_index": 12
        }
      },
      {
        "chunk_id": "chunk-uuid-002",
        "document_id": "b8c9d0e1-f2a3-4567-8901-bcdef1234567",
        "document_title": "Statistik Bisnis - Teori dan Praktik",
        "content": "Dalam menganalisis tren penjualan, pendekatan time-series seperti ARIMA dan Prophet dapat menangkap pola seasonal dengan baik. Seasonal decomposition membantu memisahkan efek musiman dari tren jangka panjang.",
        "similarity_score": 0.85,
        "metadata": {
          "page": 42,
          "section": "Time Series Analysis",
          "chunk_index": 38
        }
      }
    ],
    "query_embedding_time_ms": 45,
    "search_time_ms": 12,
    "total_results": 2
  }
}
```

**Validation Rules:**
- `query`: required, min 3 karakter, max 1000 karakter
- `top_k`: optional, default 5, max 20
- `threshold`: optional, default 0.7, range 0.0 - 1.0
- `filters.tags`: optional, array of strings
- `filters.language`: optional, ISO 639-1 code

---

### 10.5.5 Reports Endpoints

#### POST /api/v1/reports

Buat report baru. Tahap planning (generate outline) berjalan sync, writing berjalan async.

**Request:**
```json
{
  "title": "Laporan Analisis Penjualan Q1 2024",
  "description": "Laporan lengkap analisis penjualan kuartal 1 tahun 2024 dengan fokus pada tren regional",
  "source_files": ["d4e5f6a7-b8c9-0123-def0-234567890123"],
  "source_conversations": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
  "template_id": "template-formal-report",
  "custom_instructions": "Fokus pada perbandingan antar region dan trend bulanan. Sertakan rekomendasi aksi.",
  "model": "gemini-1.5-pro"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "title": "Laporan Analisis Penjualan Q1 2024",
    "status": "planning",
    "outline_json": {
      "sections": [
        { "id": "sec-1", "title": "BAB I - Pendahuluan", "description": "Latar belakang dan tujuan analisis" },
        { "id": "sec-2", "title": "BAB II - Metodologi", "description": "Sumber data dan metode analisis" },
        { "id": "sec-3", "title": "BAB III - Hasil Analisis", "description": "Temuan utama per region dan kategori" },
        { "id": "sec-4", "title": "BAB IV - Visualisasi Data", "description": "Grafik dan tabel pendukung" },
        { "id": "sec-5", "title": "BAB V - Kesimpulan & Rekomendasi", "description": "Ringkasan dan saran aksi" }
      ]
    },
    "progress_pct": 0,
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

**Validation Rules:**
- `title`: required, max 200 karakter
- `source_files`: optional, array of valid file UUIDs
- `source_conversations`: optional, array of valid conversation UUIDs
- `template_id`: optional, ID template yang tersedia
- `custom_instructions`: optional, max 2000 karakter
- `model`: optional, default dari user preferences

**Error Cases:**
- 422: Tidak ada source_files atau source_conversations
- 429: Rate limit report (10/hari)

---

#### GET /api/v1/reports

Ambil daftar report milik user.

**Query Parameters:**
- `limit` (default: 20, max: 50)
- `cursor` (optional)
- `status` (optional: `planning` | `writing` | `rendering` | `done` | `failed`)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890",
      "title": "Laporan Analisis Penjualan Q1 2024",
      "status": "done",
      "progress_pct": 100,
      "section_count": 5,
      "created_at": "2024-01-15T15:00:00Z",
      "updated_at": "2024-01-15T15:12:00Z"
    },
    {
      "id": "r2b3c4d5-e6f7-8901-bcde-f12345678901",
      "title": "Analisis Kinerja Tim Sales",
      "status": "writing",
      "progress_pct": 60,
      "section_count": 4,
      "created_at": "2024-01-15T16:00:00Z",
      "updated_at": "2024-01-15T16:05:00Z"
    }
  ],
  "meta": {
    "next_cursor": "eyJpZCI6InIyYjNjNGQ1In0=",
    "has_more": false,
    "limit": 20
  }
}
```

---

#### GET /api/v1/reports/{id}

Ambil detail report termasuk status dan outline.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "title": "Laporan Analisis Penjualan Q1 2024",
    "status": "done",
    "progress_pct": 100,
    "outline_json": {
      "sections": [
        { "id": "sec-1", "title": "BAB I - Pendahuluan", "status": "done", "word_count": 450 },
        { "id": "sec-2", "title": "BAB II - Metodologi", "status": "done", "word_count": 600 },
        { "id": "sec-3", "title": "BAB III - Hasil Analisis", "status": "done", "word_count": 1200 },
        { "id": "sec-4", "title": "BAB IV - Visualisasi Data", "status": "done", "word_count": 800 },
        { "id": "sec-5", "title": "BAB V - Kesimpulan & Rekomendasi", "status": "done", "word_count": 550 }
      ]
    },
    "total_word_count": 3600,
    "pdf_s3_key": "reports/r1a2b3c4/output.pdf",
    "created_at": "2024-01-15T15:00:00Z",
    "updated_at": "2024-01-15T15:12:00Z"
  }
}
```

---

#### PUT /api/v1/reports/{id}/outline

Edit outline sebelum memulai writing. Bisa menambah, menghapus, atau mengubah urutan section.

**Request:**
```json
{
  "sections": [
    { "id": "sec-1", "title": "BAB I - Pendahuluan", "description": "Latar belakang dan tujuan" },
    { "id": "sec-2", "title": "BAB II - Data & Metodologi", "description": "Sumber data dan pendekatan analisis" },
    { "id": "sec-new", "title": "BAB III - Analisis Regional", "description": "Breakdown per region" },
    { "id": "sec-3", "title": "BAB IV - Analisis Kategori", "description": "Breakdown per kategori produk" },
    { "id": "sec-5", "title": "BAB V - Kesimpulan", "description": "Ringkasan temuan dan rekomendasi" }
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "outline_json": {
      "sections": [
        { "id": "sec-1", "title": "BAB I - Pendahuluan", "description": "Latar belakang dan tujuan" },
        { "id": "sec-2", "title": "BAB II - Data & Metodologi", "description": "Sumber data dan pendekatan analisis" },
        { "id": "sec-new", "title": "BAB III - Analisis Regional", "description": "Breakdown per region" },
        { "id": "sec-3", "title": "BAB IV - Analisis Kategori", "description": "Breakdown per kategori produk" },
        { "id": "sec-5", "title": "BAB V - Kesimpulan", "description": "Ringkasan temuan dan rekomendasi" }
      ]
    },
    "updated_at": "2024-01-15T15:05:00Z"
  }
}
```

**Notes:**
- Hanya bisa dilakukan saat status = `planning`
- Setelah writing dimulai, outline tidak bisa diubah

---

#### POST /api/v1/reports/{id}/start

Mulai proses writing secara async. Report akan ditulis section per section.

**Response (202):**
```json
{
  "success": true,
  "data": {
    "id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890",
    "status": "writing",
    "message": "Proses writing dimulai. Gunakan SSE endpoint untuk memantau progress."
  }
}
```

**Error Cases:**
- 409: Report sudah dalam status `writing` atau `done`
- 422: Outline belum ada / masih kosong

---

#### GET /api/v1/reports/{id}/sse

Stream progress report writing via Server-Sent Events.

**Response (200, Content-Type: text/event-stream):**
```
event: progress
data: {"section_id": "sec-1", "section_title": "BAB I - Pendahuluan", "status": "writing", "progress_pct": 20}

event: section_done
data: {"section_id": "sec-1", "section_title": "BAB I - Pendahuluan", "word_count": 450}

event: progress
data: {"section_id": "sec-2", "section_title": "BAB II - Metodologi", "status": "writing", "progress_pct": 40}

event: section_done
data: {"section_id": "sec-2", "section_title": "BAB II - Metodologi", "word_count": 600}

event: progress
data: {"section_id": "sec-3", "section_title": "BAB III - Hasil Analisis", "status": "writing", "progress_pct": 60}

event: section_done
data: {"section_id": "sec-3", "section_title": "BAB III - Hasil Analisis", "word_count": 1200}

event: rendering
data: {"status": "rendering", "message": "Generating PDF...", "progress_pct": 90}

event: done
data: {"report_id": "r1a2b3c4-d5e6-7890-abcd-ef1234567890", "status": "done", "total_word_count": 3600, "pdf_url": "/api/v1/reports/r1a2b3c4-d5e6-7890-abcd-ef1234567890/pdf"}

event: error
data: {"code": "GENERATION_FAILED", "message": "Gagal menulis section BAB III", "section_id": "sec-3"}
```

---

#### POST /api/v1/reports/{id}/regenerate-section

Regenerate ulang satu section tertentu.

**Request:**
```json
{
  "section_id": "sec-3",
  "instructions": "Tambahkan lebih banyak data kuantitatif dan grafik perbandingan"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "section_id": "sec-3",
    "status": "writing",
    "message": "Section sedang di-regenerate"
  }
}
```

**Validation Rules:**
- `section_id`: required, harus section yang ada di outline
- `instructions`: optional, max 1000 karakter, instruksi tambahan untuk regenerasi

---

#### GET /api/v1/reports/{id}/pdf

Mendapatkan pre-signed URL untuk download PDF report.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "pdf_url": "https://s3.ap-southeast-1.amazonaws.com/ureport-reports/r1a2b3c4/output.pdf?X-Amz-Signature=...",
    "expires_in": 3600,
    "file_size": 2048576,
    "page_count": 24,
    "generated_at": "2024-01-15T15:12:00Z"
  }
}
```

**Error Cases:**
- 404: PDF belum digenerate (status bukan `done`)

---

#### DELETE /api/v1/reports/{id}

Hapus report beserta PDF dan data terkait.

**Response (204):** No content

**Notes:**
- PDF di S3 dihapus
- Jika report sedang `writing`, proses dibatalkan terlebih dahulu

---

### 10.5.6 Models Endpoint

#### GET /api/v1/models

Ambil daftar provider dan model yang tersedia (berdasarkan konfigurasi environment).

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "provider": "groq",
      "display_name": "Groq",
      "description": "Ultra-low latency inference engine",
      "is_available": true,
      "models": [
        {
          "id": "llama-3.1-70b-versatile",
          "name": "LLaMA 3.1 70B Versatile",
          "context_window": 131072,
          "cost_per_1k_input": 0.00059,
          "cost_per_1k_output": 0.00079
        },
        {
          "id": "llama-3.1-8b-instant",
          "name": "LLaMA 3.1 8B Instant",
          "context_window": 131072,
          "cost_per_1k_input": 0.00005,
          "cost_per_1k_output": 0.00008
        },
        {
          "id": "mixtral-8x7b-32768",
          "name": "Mixtral 8x7B",
          "context_window": 32768,
          "cost_per_1k_input": 0.00024,
          "cost_per_1k_output": 0.00024
        }
      ]
    },
    {
      "provider": "cerebras",
      "display_name": "Cerebras",
      "description": "Fastest inference with Cerebras hardware",
      "is_available": true,
      "models": [
        {
          "id": "llama-3.1-70b",
          "name": "LLaMA 3.1 70B",
          "context_window": 8192,
          "cost_per_1k_input": 0.0006,
          "cost_per_1k_output": 0.0006
        },
        {
          "id": "llama-3.1-8b",
          "name": "LLaMA 3.1 8B",
          "context_window": 8192,
          "cost_per_1k_input": 0.0001,
          "cost_per_1k_output": 0.0001
        }
      ]
    },
    {
      "provider": "gemini",
      "display_name": "Google Gemini",
      "description": "Multimodal AI with large context window",
      "is_available": true,
      "models": [
        {
          "id": "gemini-1.5-pro",
          "name": "Gemini 1.5 Pro",
          "context_window": 1048576,
          "cost_per_1k_input": 0.00125,
          "cost_per_1k_output": 0.005
        },
        {
          "id": "gemini-1.5-flash",
          "name": "Gemini 1.5 Flash",
          "context_window": 1048576,
          "cost_per_1k_input": 0.000075,
          "cost_per_1k_output": 0.0003
        }
      ]
    }
  ]
}
```

**Notes:**
- Hanya menampilkan provider yang API key-nya sudah dikonfigurasi di environment
- `is_available` bisa `false` jika provider sedang down
- Cost dihitung per 1000 token

---

### 10.5.7 Usage Endpoint

#### GET /api/v1/usage/me

Ambil statistik penggunaan dan biaya user untuk bulan berjalan.

**Query Parameters:**
- `month` (optional, format: `2024-01`, default: bulan berjalan)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": "2024-01",
    "total_tokens_in": 125000,
    "total_tokens_out": 45200,
    "total_cost_usd": 0.42,
    "monthly_budget_usd": 2.00,
    "budget_remaining_usd": 1.58,
    "budget_used_pct": 21.0,
    "breakdown_by_provider": [
      {
        "provider": "groq",
        "model": "llama-3.1-70b-versatile",
        "tokens_in": 85000,
        "tokens_out": 32000,
        "cost_usd": 0.08,
        "request_count": 45
      },
      {
        "provider": "gemini",
        "model": "gemini-1.5-pro",
        "tokens_in": 40000,
        "tokens_out": 13200,
        "cost_usd": 0.34,
        "request_count": 12
      }
    ],
    "breakdown_by_task": [
      {
        "task_type": "chat",
        "tokens_in": 95000,
        "tokens_out": 35000,
        "cost_usd": 0.25,
        "request_count": 50
      },
      {
        "task_type": "report_writer",
        "tokens_in": 20000,
        "tokens_out": 8000,
        "cost_usd": 0.12,
        "request_count": 3
      },
      {
        "task_type": "data_analysis",
        "tokens_in": 10000,
        "tokens_out": 2200,
        "cost_usd": 0.05,
        "request_count": 4
      }
    ],
    "daily_usage": [
      { "date": "2024-01-01", "cost_usd": 0.03, "requests": 5 },
      { "date": "2024-01-02", "cost_usd": 0.05, "requests": 8 },
      { "date": "2024-01-03", "cost_usd": 0.02, "requests": 3 }
    ]
  }
}
```

**Notes:**
- Budget per user default Rp 30.000 / $2.00 per bulan (configurable)
- Jika budget terlampaui, request LLM akan ditolak dengan error 429

---

## 10.6 SSE Streaming Event Format

Digunakan pada endpoint `/conversations/{id}/messages` (chat) dan `/reports/{id}/sse` (report progress).

### Koneksi

```
GET /api/v1/conversations/{id}/messages
Content-Type: text/event-stream
Authorization: Bearer <token>
Cache-Control: no-cache
Connection: keep-alive
```

### Event Types

#### `token`

Fragment teks dari respons LLM. Client menggabungkan semua token untuk membentuk pesan lengkap.

```
event: token
data: {"text": "Berdasarkan analisis data, "}

event: token
data: {"text": "penjualan bulan Januari "}

event: token
data: {"text": "mengalami peningkatan 15% dibanding bulan sebelumnya."}
```

#### `tool_start`

Dimulainya eksekusi tool/skill oleh agent (misal: run_python, search_kb).

```
event: tool_start
data: {
  "id": "tc_001",
  "tool": "run_python",
  "args": {
    "code": "import pandas as pd\ndf = pd.read_excel('data.xlsx')\nresult = df.groupby('kategori')['total'].sum().sort_values(ascending=False)\nprint(result.to_string())"
  }
}
```

#### `tool_chunk`

Output streaming dari tool yang sedang berjalan (stdout/stderr).

```
event: tool_chunk
data: {
  "id": "tc_001",
  "stdout": "kategori\nElektronik    450000000\nFashion       380000000\nMakanan       220000000\nOtomotif      180000000"
}
```

#### `tool_end`

Tool selesai dieksekusi dengan output akhir.

```
event: tool_end
data: {
  "id": "tc_001",
  "output": {
    "type": "dataframe",
    "shape": [4, 2],
    "summary": "Aggregasi total penjualan per kategori"
  },
  "duration_ms": 1250
}
```

#### `chart`

Spesifikasi chart yang harus di-render oleh frontend (Recharts compatible).

```
event: chart
data: {
  "id": "chart_001",
  "spec": {
    "type": "bar",
    "title": "Total Penjualan per Kategori",
    "data": [
      {"kategori": "Elektronik", "total": 450000000},
      {"kategori": "Fashion", "total": 380000000},
      {"kategori": "Makanan", "total": 220000000},
      {"kategori": "Otomotif", "total": 180000000}
    ],
    "config": {
      "xAxis": {"dataKey": "kategori"},
      "yAxis": {"label": "Total (Rp)"},
      "colors": ["#8884d8", "#82ca9d", "#ffc658", "#ff7c7c"]
    }
  }
}
```

#### `table`

Data tabel yang harus di-render oleh frontend.

```
event: table
data: {
  "id": "tbl_001",
  "title": "Ringkasan Penjualan per Region",
  "columns": ["region", "total_penjualan", "jumlah_transaksi", "avg_per_transaksi"],
  "rows": [
    ["Jawa Barat", 320000000, 180, 1777778],
    ["DKI Jakarta", 280000000, 150, 1866667],
    ["Jawa Timur", 210000000, 200, 1050000],
    ["Bali", 150000000, 95, 1578947]
  ]
}
```

#### `citation`

Referensi ke dokumen di knowledge base yang digunakan untuk menjawab.

```
event: citation
data: {
  "id": "cit_001",
  "document_id": "a7b8c9d0-e1f2-3456-7890-abcdef123456",
  "document_title": "Panduan Analisis Penjualan 2024",
  "page": 15,
  "section": "Bab 3 - Metode Analisis",
  "snippet": "Metode analisis tren penjualan seasonal menggunakan decomposition..."
}
```

#### `done`

Streaming selesai. Berisi informasi penggunaan token dan cost.

```
event: done
data: {
  "message_id": "f6a7b8c9-d0e1-2345-f012-456789012345",
  "usage": {
    "tokens_in": 1250,
    "tokens_out": 380,
    "cost_usd": 0.002,
    "model": "llama-3.1-70b-versatile",
    "provider": "groq",
    "latency_ms": 2500
  }
}
```

#### `error`

Error terjadi selama streaming. Client harus menampilkan pesan error dan menghentikan rendering.

```
event: error
data: {
  "code": "LLM_TIMEOUT",
  "message": "Provider tidak merespons dalam 30 detik",
  "retryable": true
}
```

---

## 10.7 Rate Limiting

Rate limiting menggunakan Redis-based token bucket per user.

### Tabel Rate Limit

| Kategori Endpoint | Rate Limit | Window | Header |
|-------------------|-----------|--------|--------|
| Auth (login/signup) | 5 request | per menit | X-RateLimit-Auth |
| Chat messages (send) | 60 request | per menit | X-RateLimit-Chat |
| Chat messages (regenerate) | 30 request | per menit | X-RateLimit-Chat |
| File uploads | 50 file | per hari | X-RateLimit-Upload |
| Knowledge base upload | 20 dokumen | per hari | X-RateLimit-KB |
| Report generation | 10 report | per hari | X-RateLimit-Report |
| KB search | 100 request | per menit | X-RateLimit-Search |
| General API | 600 request | per jam | X-RateLimit-General |

### Response Headers

Setiap response menyertakan rate limit headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705312800
```

### Response Ketika Rate Limited (429)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Terlalu banyak request. Coba lagi dalam 45 detik.",
    "details": {
      "limit": 60,
      "window": "1 menit",
      "retry_after_seconds": 45
    }
  }
}
```

---

## 10.8 Cursor-based Pagination

Semua list endpoint menggunakan cursor-based pagination (bukan offset-based) untuk performa konsisten pada dataset besar.

### Request Pattern

```
GET /api/v1/conversations?limit=20&cursor=eyJpZCI6InV1aWQtMjAiLCJ1cGRhdGVkX2F0IjoiMjAyNC0wMS0xNVQxMDozMDowMFoifQ==
```

### Parameter

| Parameter | Type | Default | Deskripsi |
|-----------|------|---------|-----------|
| `limit` | integer | 20 | Jumlah item per halaman (max: 50) |
| `cursor` | string | null | Opaque cursor dari response sebelumnya |

### Response Meta

```json
{
  "meta": {
    "next_cursor": "eyJpZCI6InV1aWQtNDAiLCJ1cGRhdGVkX2F0IjoiMjAyNC0wMS0xNFQxNjo0NTowMFoifQ==",
    "has_more": true,
    "limit": 20
  }
}
```

### Cara Kerja

1. Request pertama tanpa cursor: `GET /conversations?limit=20`
2. Response berisi `next_cursor` dan `has_more: true`
3. Request berikutnya kirim cursor: `GET /conversations?limit=20&cursor=<next_cursor>`
4. Ulangi sampai `has_more: false`

### Cursor Encoding

Cursor adalah Base64-encoded JSON yang berisi primary key dan sort key:

```json
// Decoded cursor
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Notes:**
- Cursor bersifat opaque bagi client (jangan decode/modify)
- Cursor valid selama 24 jam
- Sort default: `updated_at DESC` (terbaru dulu)
- Cursor tetap konsisten meskipun ada insert/delete di tengah

---

## 10.9 Error Codes Catalog

Daftar lengkap error code yang mungkin dikembalikan API.

| Error Code | HTTP Status | Deskripsi |
|-----------|-------------|-----------|
| `VALIDATION_ERROR` | 400 | Request body tidak valid / field gagal validasi |
| `INVALID_JSON` | 400 | Body bukan JSON valid |
| `MISSING_FIELD` | 400 | Field required tidak dikirim |
| `INVALID_FORMAT` | 400 | Format field tidak sesuai (misal: email, UUID) |
| `UNAUTHORIZED` | 401 | Token tidak ada atau tidak valid |
| `TOKEN_EXPIRED` | 401 | JWT sudah expired |
| `INVALID_CREDENTIALS` | 401 | Email/password salah |
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token expired atau tidak valid |
| `FORBIDDEN` | 403 | User tidak punya akses ke resource ini |
| `NOT_FOUND` | 404 | Resource dengan ID tersebut tidak ditemukan |
| `CONVERSATION_NOT_FOUND` | 404 | Conversation tidak ditemukan |
| `FILE_NOT_FOUND` | 404 | File tidak ditemukan |
| `REPORT_NOT_FOUND` | 404 | Report tidak ditemukan |
| `DOCUMENT_NOT_FOUND` | 404 | KB document tidak ditemukan |
| `DUPLICATE_EMAIL` | 409 | Email sudah terdaftar |
| `CONFLICT` | 409 | Resource dalam state yang konflik |
| `REPORT_ALREADY_WRITING` | 409 | Report sudah dalam proses writing |
| `FILE_TOO_LARGE` | 413 | File melebihi batas ukuran |
| `UNSUPPORTED_FILE_TYPE` | 415 | Tipe file tidak didukung |
| `UNPROCESSABLE` | 422 | Request valid tapi tidak bisa diproses |
| `FILE_CORRUPT` | 422 | File tidak bisa dibaca/corrupt |
| `EMPTY_OUTLINE` | 422 | Outline report kosong |
| `RATE_LIMITED` | 429 | Rate limit terlampaui |
| `BUDGET_EXCEEDED` | 429 | Budget bulanan user sudah habis |
| `INTERNAL_ERROR` | 500 | Error tidak terduga di server |
| `LLM_ERROR` | 502 | Error dari LLM provider |
| `LLM_TIMEOUT` | 504 | LLM provider tidak merespons |
| `PROVIDER_UNAVAILABLE` | 503 | LLM provider sedang down/maintenance |
| `GENERATION_FAILED` | 500 | Gagal generate report section |
| `EMBEDDING_FAILED` | 500 | Gagal membuat embedding untuk dokumen |

---

## 10.10 OpenAPI & Type Generation

### Auto-generated OpenAPI Schema

FastAPI secara otomatis menggenerate OpenAPI 3.1 schema:

```
GET /openapi.json    -> OpenAPI spec (JSON)
GET /docs            -> Swagger UI (development only)
GET /redoc           -> ReDoc (development only)
```

### Frontend Type Generation

Menggunakan `openapi-typescript` untuk generate TypeScript types dari OpenAPI schema:

```bash
# Generate types dari backend OpenAPI
npx openapi-typescript http://localhost:8000/openapi.json -o packages/shared-types/src/api.d.ts

# Atau dari file spec yang sudah di-export
npx openapi-typescript ./openapi.json -o packages/shared-types/src/api.d.ts
```

### Pydantic v2 Schema Example

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = None


class ConversationResponse(BaseModel):
    id: UUID
    title: Optional[str]
    model: str
    pinned: bool = False
    archived: bool = False
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    content: str = Field(..., min_length=1, max_length=32000)
    file_ids: Optional[list[UUID]] = None
    model: Optional[str] = None


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list
    meta: dict
```

### CI Integration

```yaml
# .github/workflows/types.yml
- name: Generate API types
  run: |
    npx openapi-typescript ${{ env.API_URL }}/openapi.json \
      -o packages/shared-types/src/api.d.ts
    git diff --exit-code packages/shared-types/
```

**Notes:**
- Types digenerate saat CI dan di-commit ke repo
- Frontend mengimport types langsung, fully type-safe end-to-end
- Setiap perubahan schema backend harus disertai update types

---

## 10.11 Ringkasan Endpoint

| # | Method | Path | Deskripsi |
|---|--------|------|-----------|
| 1 | POST | `/auth/signup` | Registrasi user baru |
| 2 | POST | `/auth/signin` | Login |
| 3 | GET | `/auth/oauth/google` | OAuth Google redirect |
| 4 | GET | `/auth/oauth/google/callback` | OAuth callback |
| 5 | POST | `/auth/signout` | Logout |
| 6 | GET | `/auth/me` | Profil user |
| 7 | POST | `/auth/refresh` | Refresh token |
| 8 | GET | `/conversations` | List conversations |
| 9 | POST | `/conversations` | Buat conversation |
| 10 | GET | `/conversations/{id}` | Detail conversation |
| 11 | PATCH | `/conversations/{id}` | Update conversation |
| 12 | DELETE | `/conversations/{id}` | Hapus conversation |
| 13 | GET | `/conversations/{id}/messages` | List messages |
| 14 | POST | `/conversations/{id}/messages` | Send message (SSE) |
| 15 | POST | `/conversations/{id}/messages/{mid}/regenerate` | Regenerate |
| 16 | POST | `/files` | Upload file |
| 17 | GET | `/files` | List files |
| 18 | GET | `/files/{id}` | Detail file |
| 19 | GET | `/files/{id}/preview` | Preview rows |
| 20 | DELETE | `/files/{id}` | Hapus file |
| 21 | POST | `/kb/documents` | Upload KB document |
| 22 | GET | `/kb/documents` | List KB documents |
| 23 | GET | `/kb/documents/{id}` | Detail KB document |
| 24 | DELETE | `/kb/documents/{id}` | Hapus KB document |
| 25 | POST | `/kb/search` | Semantic search |
| 26 | POST | `/reports` | Buat report |
| 27 | GET | `/reports` | List reports |
| 28 | GET | `/reports/{id}` | Detail report |
| 29 | PUT | `/reports/{id}/outline` | Edit outline |
| 30 | POST | `/reports/{id}/start` | Mulai writing |
| 31 | GET | `/reports/{id}/sse` | Stream progress |
| 32 | POST | `/reports/{id}/regenerate-section` | Regenerate section |
| 33 | GET | `/reports/{id}/pdf` | Download PDF |
| 34 | DELETE | `/reports/{id}` | Hapus report |
| 35 | GET | `/models` | List providers & models |
| 36 | GET | `/usage/me` | Usage & cost |
