# 17 - Development Guide

## Overview

Panduan lengkap untuk setup development environment, menjalankan project, dan workflow pengembangan uReport AI v2.

> **Status:** Dokumen ini mencerminkan kondisi project di **Phase 1 (MVP Chat Multi-LLM)**. Semua bagian sudah terverifikasi dan bisa langsung diikuti.

---

## 1. Prerequisites (Yang Harus Diinstall)

### Wajib (Must Have)

| Software | Version | Kegunaan | Install Link |
|----------|---------|----------|-------------|
| Python | 3.12+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ LTS | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| pnpm | 9+ | Frontend package manager | [pnpm.io](https://pnpm.io/installation) |
| uv | latest | Python package manager (pengganti pip) | [astral.sh/uv](https://docs.astral.sh/uv/) |
| Docker | 24+ | Infrastructure services saja | [docker.com](https://www.docker.com/get-started/) |
| Docker Compose | v2+ | Multi-container orchestration | Included with Docker Desktop |
| Git | 2.40+ | Version control | [git-scm.com](https://git-scm.com/) |

> **Catatan:** Docker hanya diperlukan untuk menjalankan infrastructure services (PostgreSQL, Redis, Qdrant, MinIO). Backend (FastAPI) dan Frontend (Next.js) dijalankan secara native untuk development.

### Optional (Nice to Have)

| Software | Kegunaan |
|----------|----------|
| pyenv | Manage multiple Python versions |
| pgAdmin / DBeaver | GUI untuk PostgreSQL |
| Redis Insight | GUI untuk Redis |
| Qdrant Web UI | GUI vector database (included di port 6333) |
| VS Code | Code editor (recommended) |
| Bruno / Insomnia | API testing |

### VS Code Extensions (Recommended)

```text
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- GitLens (eamodio.gitlens)
- Docker (ms-azuretools.vscode-docker)
- Error Lens (usernamehw.errorlens)
```

---

## 2. Project Setup Step-by-Step

### Step 1: Clone Repository

```bash
git clone https://github.com/masbroustudio/ureport-ai.git
cd ureport-ai
```

### Step 2: Setup Backend (apps/api)

```bash
# Install uv jika belum (Python package manager modern)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install backend dependencies
cd apps/api
uv sync

# Kembali ke root
cd ../..
```

### Step 3: Setup Frontend (apps/web)

```bash
# Install pnpm jika belum
npm install -g pnpm

# Install frontend dependencies
cd apps/web
pnpm install

# Kembali ke root
cd ../..
```

### Step 4: Setup Environment Variables

```bash
# Copy environment file
cp .env.example .env

# Edit .env jika perlu (default values sudah cukup untuk development lokal)
```

### Step 5: Start Infrastructure (Docker)

```bash
# Start semua infrastructure services
docker compose -f infra/docker/compose.dev.yml up -d

# Verify semua services running
docker compose -f infra/docker/compose.dev.yml ps
```

Services yang dijalankan:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333, 6334)
- MinIO (port 9000 API, 9001 Console)

### Step 6: Start Development Servers

```bash
# Terminal 1: Backend (FastAPI)
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (Next.js)
cd apps/web
pnpm dev
```

### Step 7: Verify Setup

| Service | URL | Keterangan |
|---------|-----|-----------|
| Frontend | http://localhost:3000 | Next.js App (landing page) |
| Frontend Chat | http://localhost:3000/chat | Chat page (placeholder) |
| Backend API | http://localhost:8000/docs | FastAPI Swagger UI |
| Health Check | http://localhost:8000/healthz | Backend health endpoint |
| Ready Check | http://localhost:8000/readyz | Backend readiness endpoint |
| MinIO Console | http://localhost:9001 | Object storage UI |
| Qdrant UI | http://localhost:6333/dashboard | Vector DB UI |

### Shortcut: Menggunakan Make

Semua langkah di atas bisa dilakukan dengan Makefile:

```bash
# Install semua dependencies (backend + frontend)
make install

# Start infrastructure containers
make dev-up

# Start backend (terminal terpisah)
make api-dev

# Start frontend (terminal terpisah)
make web-dev
```

---

## 3. Makefile Commands

File: `Makefile` (root project)

| Command | Deskripsi |
|---------|-----------|
| `make help` | Tampilkan daftar perintah |
| `make install` | Install semua dependencies (backend + frontend) |
| `make dev-up` | Start infrastructure Docker containers |
| `make dev-down` | Stop infrastructure Docker containers |
| `make api-dev` | Start backend dev server (FastAPI) |
| `make web-dev` | Start frontend dev server (Next.js) |
| `make api-test` | Run backend tests |
| `make lint` | Lint semua code (ruff + eslint) |
| `make format` | Format semua code (ruff + prettier) |

---

## 4. Environment Variables

### Root `.env` / `apps/api/.env`

File `.env.example` di root project berisi semua variabel yang diperlukan:

```bash
# Application
APP_ENV=development
APP_DEBUG=true
APP_NAME="uReport AI API"
APP_VERSION=0.1.0

# CORS
CORS_ORIGINS=http://localhost:3000

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# Object Storage (MinIO / S3)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=ureport-files

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333

# Celery (Task Queue)
CELERY_BROKER_URL=redis://localhost:6379/2

# Authentication (JWT)
JWT_SECRET_KEY=change-me-in-production-min-32-chars
JWT_ALGORITHM=HS256
```

> **Catatan Phase 0:** Variabel di atas digunakan ketika infrastructure services sudah berjalan via Docker.

### LLM Provider API Keys (Phase 1)

```bash
# === LLM Provider API Keys ===
# Minimal satu provider harus dikonfigurasi untuk fitur chat
GROQ_API_KEY=                    # https://console.groq.com/keys
CEREBRAS_API_KEY=                # https://cloud.cerebras.ai/
GEMINI_API_KEY=                  # https://aistudio.google.com/apikey
SUMOPOD_API_KEY=                 # OpenAI-compatible provider
SUMOPOD_BASE_URL=                # Base URL untuk Sumopod API

# === JWT Configuration ===
JWT_SECRET_KEY=change-me-in-production-min-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

> **Catatan Phase 1:** Minimal satu LLM provider API key harus dikonfigurasi agar fitur chat berfungsi. Prioritas default: Groq > Cerebras > Gemini > Sumopod.

### Cara Konfigurasi LLM Providers

1. Daftar di salah satu provider:
   - **Groq** (recommended, paling cepat): https://console.groq.com/keys
   - **Cerebras**: https://cloud.cerebras.ai/
   - **Google Gemini**: https://aistudio.google.com/apikey
   - **Sumopod** (OpenAI-compatible): memerlukan API key + base URL

2. Set API key di `.env`:
   ```bash
   GROQ_API_KEY=gsk_xxxxxxxxxxxxx
   ```

3. Restart backend server. Model yang tersedia akan muncul otomatis berdasarkan key yang dikonfigurasi.

---

## 5. API Endpoints

### Phase 0 - Foundation

| Method | Path | Deskripsi | Status |
|--------|------|-----------|--------|
| GET | `/healthz` | Health check | Aktif |
| GET | `/readyz` | Readiness check | Aktif |
| GET | `/api/v1/files/` | List files | Placeholder |
| POST | `/api/v1/files/` | Upload file | Placeholder |

### Phase 1 - MVP Chat Multi-LLM

| Method | Path | Deskripsi | Auth |
|--------|------|-----------|------|
| POST | `/api/v1/auth/signup` | Registrasi user baru | Tidak |
| POST | `/api/v1/auth/signin` | Login user | Tidak |
| GET | `/api/v1/auth/me` | Profil user saat ini | Ya |
| GET | `/api/v1/conversations/` | List semua percakapan | Ya |
| POST | `/api/v1/conversations/` | Buat percakapan baru | Ya |
| GET | `/api/v1/conversations/{id}` | Detail percakapan | Ya |
| PATCH | `/api/v1/conversations/{id}` | Update percakapan | Ya |
| DELETE | `/api/v1/conversations/{id}` | Hapus percakapan | Ya |
| GET | `/api/v1/conversations/{id}/messages` | List pesan dalam percakapan | Ya |
| POST | `/api/v1/conversations/{id}/messages` | Kirim pesan (SSE streaming) | Ya |

### Frontend Pages

| Path | Deskripsi |
|------|-----------|
| `/` | Landing page |
| `/signin` | Halaman login |
| `/signup` | Halaman registrasi |
| `/chat` | Chat interface dengan model selector |
| `/settings` | Halaman pengaturan user |

---

## 6. Testing dan Code Quality

### Menjalankan Tests

```bash
# Backend tests (14 tests: auth, conversations, health)
cd apps/api
uv run pytest tests/ -v

# Atau dari root menggunakan Make
make api-test
```

### Cara Menjalankan Fitur Chat End-to-End

1. Pastikan infrastructure berjalan (`docker compose -f infra/docker/compose.dev.yml up -d`)
2. Jalankan migrasi database:
   ```bash
   cd apps/api
   uv run alembic upgrade head
   ```
3. Start backend:
   ```bash
   cd apps/api
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start frontend:
   ```bash
   cd apps/web
   pnpm dev
   ```
5. Buka http://localhost:3000/signup untuk registrasi
6. Setelah login, buka http://localhost:3000/chat
7. Pilih model dari dropdown (model yang muncul tergantung API key yang dikonfigurasi)
8. Ketik pesan dan tekan Enter untuk mulai chat

### Linting

```bash
# Lint backend (ruff)
cd apps/api && uv run ruff check .

# Lint frontend (eslint)
cd apps/web && pnpm lint

# Atau semua sekaligus dari root
make lint
```

### Formatting

```bash
# Format backend (ruff format)
cd apps/api && uv run ruff format .

# Format frontend (prettier)
cd apps/web && pnpm format

# Atau semua sekaligus dari root
make format
```

### Build Verification

```bash
# Verify backend imports correctly
cd apps/api && uv run python -c "import app.main"

# Verify frontend builds
cd apps/web && pnpm build
```

---

## 7. Common Development Tasks

> **Catatan:** Bagian ini berisi panduan untuk fase berikutnya. Patterns dan contoh di bawah akan relevan saat fitur-fitur mulai diimplementasikan.

### 7.1 Menambah shadcn/ui Component

```bash
cd apps/web

# Install component (contoh: dialog)
pnpm dlx shadcn@latest add dialog

# Install multiple components
pnpm dlx shadcn@latest add button card input label

# Component akan tersedia di src/components/ui/
```

Setelah install:
1. Component muncul di `apps/web/src/components/ui/`
2. Import: `import { Dialog, DialogContent } from "@/components/ui/dialog"`
3. Customisasi styling di file component langsung (bukan di global CSS)
4. Lihat docs lengkap: https://ui.shadcn.com/docs/components

### 7.2 Menambah FastAPI Router Baru

1. Buat file router baru di `apps/api/app/router/`:

```python
# apps/api/app/router/reports.py
from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/")
async def create_report():
    return {"message": "TODO: implement"}
```

2. Register router di `app/main.py`:

```python
from app.router import reports

app.include_router(reports.router, prefix="/api/v1")
```

3. Buat tests di `tests/`

### 7.3 Database Migrations (Alembic)

Alembic sudah dikonfigurasi di `apps/api/alembic.ini` dan `apps/api/alembic/`.

```bash
cd apps/api

# Buat migration baru (autogenerate dari model changes)
uv run alembic revision --autogenerate -m "add users table"

# Jalankan semua migration yang pending
uv run alembic upgrade head

# Rollback satu migration
uv run alembic downgrade -1

# Lihat history migration
uv run alembic history
```

---

## 8. Testing Strategy

> **Catatan:** Bagian ini berisi panduan untuk fase berikutnya. Saat ini hanya health check test yang tersedia.

### Backend Testing (pytest + pytest-asyncio + httpx)

**Stack:**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client

**Struktur direktori saat ini:**

```
apps/api/tests/
|-- __init__.py
|-- test_health.py           # Health check tests (aktif)
```

**Menjalankan tests:**

```bash
cd apps/api

# Run semua tests
uv run pytest -v

# Run specific file
uv run pytest tests/test_health.py -v

# Run dengan output print (debug)
uv run pytest -s -v
```

### Frontend Testing (Planned)

Stack yang akan digunakan:
- `vitest` - Test runner
- `@testing-library/react` - Component testing
- `@testing-library/user-event` - User interaction simulation

---

## 9. Git Workflow

### Branch Naming Convention

```
feature/   - Fitur baru          (feature/add-report-export)
fix/       - Bug fix             (fix/chat-streaming-error)
docs/      - Dokumentasi         (docs/update-api-docs)
chore/     - Maintenance         (chore/update-dependencies)
refactor/  - Refactoring         (refactor/simplify-auth-flow)
test/      - Penambahan test     (test/add-report-service-tests)
```

### Commit Message Convention

Menggunakan format [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - Fitur baru
- `fix` - Bug fix
- `docs` - Perubahan dokumentasi
- `style` - Formatting (tidak mengubah logic)
- `refactor` - Refactoring code
- `test` - Menambah atau memperbaiki tests
- `chore` - Maintenance tasks
- `perf` - Performance improvements
- `ci` - CI/CD changes

**Contoh:**

```
feat(reports): add PDF export with WeasyPrint

Implement report generation pipeline using Jinja2 templates
and WeasyPrint for HTML-to-PDF conversion.

Closes #42
```

### Pull Request Template

```markdown
## Deskripsi
[Jelaskan perubahan yang dilakukan]

## Tipe Perubahan
- [ ] Fitur baru (non-breaking change)
- [ ] Bug fix (non-breaking change)
- [ ] Breaking change
- [ ] Dokumentasi

## Testing
- [ ] Unit tests ditambahkan/diupdate
- [ ] Manual testing dilakukan
- [ ] Semua tests passing

## Checklist
- [ ] Code sudah di-review sendiri
- [ ] Self-review sudah dilakukan
- [ ] Dokumentasi diupdate (jika perlu)
- [ ] Tidak ada console.log/print debug
```

---

## 10. Troubleshooting

### Port sudah digunakan

```bash
# Cek proses yang menggunakan port
lsof -i :8000  # backend
lsof -i :3000  # frontend

# Kill proses jika perlu
kill -9 <PID>
```

### Docker containers tidak bisa start

```bash
# Reset containers dan volumes
docker compose -f infra/docker/compose.dev.yml down -v
docker compose -f infra/docker/compose.dev.yml up -d
```

### Python dependencies error

```bash
cd apps/api
# Hapus virtual environment dan reinstall
rm -rf .venv
uv sync
```

### Node.js dependencies error

```bash
cd apps/web
# Hapus node_modules dan reinstall
rm -rf node_modules
pnpm install
```

### Tests gagal import

Pastikan menjalankan tests dengan `uv run`:
```bash
cd apps/api
uv run pytest tests/ -v
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `make install` |
| Start infrastructure | `make dev-up` |
| Stop infrastructure | `make dev-down` |
| Start backend | `make api-dev` |
| Start frontend | `make web-dev` |
| Run backend tests | `make api-test` |
| Lint code | `make lint` |
| Format code | `make format` |

---

> **Tip:** Bookmark halaman ini! Ini adalah referensi utama untuk workflow development sehari-hari di project uReport AI v2.
