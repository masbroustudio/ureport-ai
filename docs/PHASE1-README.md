# Phase 1 - MVP Chat Multi-LLM

Dokumentasi lengkap untuk Phase 1 uReport AI v2: fitur chat real-time dengan dukungan multi-provider LLM.

---

## 1. Apa yang Diimplementasi

Phase 1 menghadirkan fitur **chat real-time** dengan dukungan **4 provider LLM** melalui gateway terpadu. Berikut komponen yang diimplementasi:

### Backend (apps/api)

- **Autentikasi JWT** - signup, signin, endpoint `/me` dengan token berbasis Bearer
- **Password hashing** - argon2 untuk keamanan password
- **Model database** - User, Conversation, Message, UsageLog (SQLAlchemy async)
- **CRUD Conversations** - create, read, update, delete percakapan
- **Chat Streaming** - SSE (Server-Sent Events) untuk respons real-time dari LLM
- **Multi-LLM Gateway** - litellm sebagai abstraksi unifikasi 4 provider:
  - Groq (Llama 3.3 70B)
  - Cerebras (Llama 3.3 70B)
  - Google Gemini (Gemini 2.0 Flash)
  - Sumopod (OpenAI-compatible)
- **Usage logging** - pencatatan token usage per request
- **14 unit tests** - auth, conversations, health check

### Frontend (apps/web)

- **Halaman Auth** - signin dan signup dengan validasi form
- **Chat UI** - interface percakapan dengan sidebar
- **SSE Streaming** - rendering respons LLM secara real-time
- **Model Selector** - dropdown untuk memilih model/provider
- **Markdown Rendering** - react-markdown dengan syntax highlighting
- **Settings Page** - halaman pengaturan user

---

## 2. Prasyarat

| Software | Versi Minimum | Kegunaan |
|----------|---------------|----------|
| Python | 3.12+ | Backend runtime |
| Node.js | 22+ LTS | Frontend runtime |
| pnpm | 9+ | Frontend package manager |
| uv | latest | Python package manager |
| PostgreSQL | 16+ | Database utama |
| Redis | 7+ | Cache dan session |
| Docker & Docker Compose | 24+ / v2+ | Infrastructure services |
| Git | 2.40+ | Version control |

### API Keys (minimal satu)

| Provider | Cara Mendapatkan |
|----------|-----------------|
| Groq | https://console.groq.com/keys |
| Cerebras | https://cloud.cerebras.ai/ |
| Google Gemini | https://aistudio.google.com/apikey |
| Sumopod | Hubungi administrator |

---

## 3. Setup Environment

### 3.1 Clone Repository

```bash
git clone https://github.com/masbroustudio/ureport-ai.git
cd ureport-ai
```

### 3.2 Konfigurasi Environment Variables

```bash
cp .env.example .env
```

Edit file `.env` dan isi minimal variabel berikut:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai

# JWT (WAJIB diganti untuk production)
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# LLM Provider - isi minimal satu
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Untuk Sumopod, isi kedua variabel:
# SUMOPOD_API_KEY=sk-xxxxxx
# SUMOPOD_BASE_URL=https://api.sumopod.example.com/v1
```

### 3.3 Install Dependencies

```bash
# Backend
cd apps/api
uv sync
cd ../..

# Frontend
cd apps/web
pnpm install
cd ../..
```

---

## 4. Cara Menjalankan

### 4.1 Start Infrastructure (Docker Compose)

```bash
docker compose -f infra/docker/compose.dev.yml up -d
```

Ini menjalankan:
- PostgreSQL di port 5432
- Redis di port 6379
- Qdrant di port 6333
- MinIO di port 9000/9001

Verifikasi:
```bash
docker compose -f infra/docker/compose.dev.yml ps
```

### 4.2 Jalankan Database Migration

```bash
cd apps/api
uv run alembic upgrade head
```

Ini membuat tabel-tabel: `users`, `conversations`, `messages`, `usage_logs`.

### 4.3 Start Backend

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend tersedia di:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthz

### 4.4 Start Frontend

```bash
cd apps/web
pnpm dev
```

Frontend tersedia di:
- http://localhost:3000 (landing page)
- http://localhost:3000/signin (login)
- http://localhost:3000/signup (registrasi)
- http://localhost:3000/chat (chat interface)
- http://localhost:3000/settings (pengaturan)

### 4.5 Menggunakan Makefile (Shortcut)

```bash
make install      # Install semua dependencies
make dev-up       # Start Docker containers
make api-dev      # Start backend
make web-dev      # Start frontend
```

---

## 5. Cara Menjalankan Test

### 5.1 Backend Tests

```bash
cd apps/api
uv run pytest tests/ -v
```

Output yang diharapkan: **14 tests passed**

Cakupan test:
- `tests/test_health.py` - health check endpoints
- `tests/test_auth.py` - signup, signin, dan me endpoints
- `tests/test_conversations.py` - CRUD conversations dan messages

### 5.2 Frontend Type Check

```bash
cd apps/web
pnpm build
```

Ini menjalankan TypeScript compiler dan memastikan tidak ada error tipe.

### 5.3 Lint

```bash
# Backend lint (ruff)
cd apps/api
uv run ruff check .

# Frontend lint (eslint)
cd apps/web
pnpm lint
```

### 5.4 Menjalankan Test Tanpa Docker

Backend tests menggunakan mock untuk database, sehingga bisa dijalankan tanpa PostgreSQL/Redis:

```bash
cd apps/api
uv run pytest tests/ -v
```

---

## 6. API Endpoints Reference

### Authentication

| Method | Path | Deskripsi | Auth | Request Body |
|--------|------|-----------|------|-------------|
| POST | `/api/v1/auth/signup` | Registrasi user baru | Tidak | `{email, name, password}` |
| POST | `/api/v1/auth/signin` | Login | Tidak | `{email, password}` |
| GET | `/api/v1/auth/me` | Profil user aktif | Ya | - |

**Response signup/signin:**
```json
{
  "access_token": "eyJ...",
  "expires_in": 604800,
  "user": {"id": "uuid", "email": "...", "name": "..."}
}
```

### Conversations

| Method | Path | Deskripsi | Auth |
|--------|------|-----------|------|
| GET | `/api/v1/conversations/` | List percakapan (cursor pagination) | Ya |
| POST | `/api/v1/conversations/` | Buat percakapan baru | Ya |
| GET | `/api/v1/conversations/{id}` | Detail percakapan | Ya |
| PATCH | `/api/v1/conversations/{id}` | Update judul/model | Ya |
| DELETE | `/api/v1/conversations/{id}` | Hapus percakapan | Ya |

### Messages

| Method | Path | Deskripsi | Auth |
|--------|------|-----------|------|
| GET | `/api/v1/conversations/{id}/messages` | List pesan (cursor pagination) | Ya |
| POST | `/api/v1/conversations/{id}/messages` | Kirim pesan, respons via SSE | Ya |

**SSE Events pada POST messages:**
- `event: token` - data: `{"text": "..."}` (setiap token dari LLM)
- `event: done` - data: `{"message_id": "uuid", "usage": {...}}` (selesai)
- `event: error` - data: `{"detail": "..."}` (jika terjadi error)

### Infrastructure

| Method | Path | Deskripsi | Auth |
|--------|------|-----------|------|
| GET | `/healthz` | Health check | Tidak |
| GET | `/readyz` | Readiness check | Tidak |

### Autentikasi

Semua endpoint yang memerlukan auth menggunakan header:
```
Authorization: Bearer <access_token>
```

---

## 7. Arsitektur & Keputusan Teknis

### 7.1 JWT Authentication (bukan Sessions)

**Alasan:** Stateless authentication cocok untuk SPA (Single Page Application) dan memudahkan horizontal scaling.

- Token disimpan di `localStorage` pada frontend
- Expire time default: 7 hari (10080 menit)
- Algorithm: HS256
- Tidak ada refresh token (simplifikasi untuk MVP)

### 7.2 Argon2 untuk Password Hashing

**Alasan:** Argon2id adalah pemenang Password Hashing Competition dan lebih aman dari bcrypt terhadap GPU/ASIC attacks.

- Library: `argon2-cffi`
- Konfigurasi default argon2 (memory-hard, timing-safe)

### 7.3 LiteLLM sebagai Unified LLM Gateway

**Alasan:** Satu interface untuk banyak provider LLM, tanpa perlu menulis adapter terpisah untuk masing-masing provider.

- Package: `litellm`
- Model format: `{provider}/{model_name}` (contoh: `groq/llama-3.3-70b-versatile`)
- Streaming via `acompletion()` async generator
- API key dan base URL di-resolve berdasarkan prefix model

### 7.4 SSE Streaming untuk Real-time Chat

**Alasan:** SSE lebih sederhana dari WebSocket untuk kasus unidirectional streaming (server-to-client).

- Response type: `text/event-stream`
- Event types: `token`, `done`, `error`
- Frontend menggunakan `EventSource` API atau `fetch` dengan stream reader

### 7.5 Async SQLAlchemy dengan asyncpg

**Alasan:** Non-blocking database operations cocok untuk FastAPI async handlers.

- Engine: `postgresql+asyncpg`
- Session management via FastAPI dependency injection (`get_db`)
- Models menggunakan `DeclarativeBase` dengan UUID primary keys

### 7.6 Model Registry Pattern

Model LLM yang tersedia ditentukan secara dinamis berdasarkan API key yang dikonfigurasi:
- Tidak ada API key = model tidak ditampilkan
- Prioritas default: Groq > Cerebras > Gemini > Sumopod

---

## 8. Deployment Guide

### 8.1 Environment Variables untuk Production

| Variable | Wajib | Deskripsi |
|----------|-------|-----------|
| `DATABASE_URL` | Ya | PostgreSQL connection string |
| `REDIS_URL` | Ya | Redis connection string |
| `JWT_SECRET_KEY` | Ya | Secret key min 32 chars (JANGAN default) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Tidak | Default: 10080 (7 hari) |
| `CORS_ORIGINS` | Ya | Domain frontend (contoh: https://app.ureport.ai) |
| `GROQ_API_KEY` | Min 1 | API key untuk Groq |
| `CEREBRAS_API_KEY` | Min 1 | API key untuk Cerebras |
| `GEMINI_API_KEY` | Min 1 | API key untuk Gemini |
| `SUMOPOD_API_KEY` | Min 1 | API key untuk Sumopod |
| `SUMOPOD_BASE_URL` | Jika Sumopod | Base URL untuk Sumopod API |
| `APP_ENV` | Ya | Set ke `production` |
| `APP_DEBUG` | Ya | Set ke `false` |

> **Penting:** Minimal satu LLM provider API key harus dikonfigurasi.

### 8.2 Docker Compose untuk Production

```yaml
# docker-compose.prod.yml (contoh)
version: "3.8"
services:
  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - APP_ENV=production
      - APP_DEBUG=false
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ureport_ai
      POSTGRES_USER: ureport
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 8.3 Menjalankan Migration di Production

```bash
# Dari container atau server yang memiliki akses ke database
cd apps/api
uv run alembic upgrade head
```

Pastikan `DATABASE_URL` di environment mengarah ke database production.

### 8.4 Build dan Deploy Frontend

```bash
cd apps/web
pnpm build    # Output di .next/
pnpm start    # Start production server
```

Atau menggunakan Docker:
```bash
docker build -t ureport-web ./apps/web
docker run -p 3000:3000 ureport-web
```

### 8.5 Checklist Deployment

- [ ] `JWT_SECRET_KEY` sudah diganti dari default value
- [ ] `APP_ENV=production` dan `APP_DEBUG=false`
- [ ] `CORS_ORIGINS` mengarah ke domain frontend production
- [ ] Minimal satu LLM provider API key dikonfigurasi
- [ ] Database migration sudah dijalankan (`alembic upgrade head`)
- [ ] PostgreSQL dan Redis accessible dari backend
- [ ] Frontend build berhasil (`pnpm build`)

---

## 9. Debugging & Troubleshooting

### 9.1 Chat Tidak Merespons

**Gejala:** Pesan terkirim tapi tidak ada respons dari AI.

**Solusi:**
1. Periksa apakah minimal satu LLM API key sudah dikonfigurasi di `.env`
2. Verifikasi key masih valid (belum expired/revoked)
3. Cek log backend untuk error dari litellm
4. Pastikan variabel di `.env` terbaca (restart backend setelah mengubah `.env`)

### 9.2 Error "Invalid email or password"

**Gejala:** Tidak bisa login meskipun sudah registrasi.

**Solusi:**
1. Pastikan email yang digunakan persis sama (case-sensitive)
2. Cek apakah database migration sudah dijalankan
3. Coba signup ulang jika database baru di-reset

### 9.3 SSE Streaming Terputus

**Gejala:** Respons AI terpotong di tengah.

**Solusi:**
1. Periksa apakah ada proxy/load balancer yang timeout (tingkatkan timeout ke 120s+)
2. Pastikan `Content-Type: text/event-stream` tidak di-buffer oleh reverse proxy
3. Untuk nginx, tambahkan: `proxy_buffering off;`

### 9.4 Frontend Build Error

**Gejala:** `pnpm build` gagal.

**Solusi:**
```bash
cd apps/web
rm -rf node_modules .next
pnpm install
pnpm build
```

### 9.5 Backend Import Error

**Gejala:** `ModuleNotFoundError` saat menjalankan backend.

**Solusi:**
```bash
cd apps/api
rm -rf .venv
uv sync
uv run python -c "from app.main import app; print('OK')"
```

### 9.6 Database Connection Refused

**Gejala:** Backend tidak bisa konek ke PostgreSQL.

**Solusi:**
1. Pastikan Docker containers berjalan: `docker compose -f infra/docker/compose.dev.yml ps`
2. Verifikasi `DATABASE_URL` di `.env` sesuai dengan konfigurasi Docker
3. Reset containers jika perlu:
   ```bash
   docker compose -f infra/docker/compose.dev.yml down -v
   docker compose -f infra/docker/compose.dev.yml up -d
   ```

### 9.7 Token Expired

**Gejala:** Request mendapat 401 Unauthorized meskipun sudah login.

**Solusi:**
1. Login ulang melalui `/signin`
2. Default token expire: 7 hari. Jika perlu lebih lama, ubah `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` di `.env`

### 9.8 Model Tidak Muncul di Dropdown

**Gejala:** Dropdown model selector kosong.

**Solusi:**
1. Pastikan minimal satu `*_API_KEY` terisi di `.env`
2. Restart backend setelah mengubah `.env`
3. Model hanya muncul jika API key untuk provider tersebut sudah dikonfigurasi

---

## Referensi Cepat

| Aksi | Perintah |
|------|----------|
| Install semua deps | `make install` |
| Start infrastructure | `make dev-up` |
| Jalankan migration | `cd apps/api && uv run alembic upgrade head` |
| Start backend | `make api-dev` |
| Start frontend | `make web-dev` |
| Jalankan test | `cd apps/api && uv run pytest tests/ -v` |
| Lint backend | `cd apps/api && uv run ruff check .` |
| Build frontend | `cd apps/web && pnpm build` |

---

> Dokumen ini ditulis untuk **Phase 1 - MVP Chat Multi-LLM** dari project uReport AI v2.
