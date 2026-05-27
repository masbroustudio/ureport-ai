# 17 - Development Guide

## Overview

Panduan lengkap untuk setup development environment, menjalankan project, dan workflow pengembangan uReport AI v2.

---

## 1. Prerequisites (Yang Harus Diinstall)

### Wajib (Must Have)

| Software | Version | Kegunaan | Install Link |
|----------|---------|----------|-------------|
| Python | 3.12+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ LTS | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| pnpm | 9+ | Frontend package manager | [pnpm.io](https://pnpm.io/installation) |
| uv | latest | Python package manager (pengganti pip) | [astral.sh/uv](https://docs.astral.sh/uv/) |
| Docker | 24+ | Containerization | [docker.com](https://www.docker.com/get-started/) |
| Docker Compose | v2+ | Multi-container orchestration | Included with Docker Desktop |
| Git | 2.40+ | Version control | [git-scm.com](https://git-scm.com/) |

### Optional (Nice to Have)

| Software | Kegunaan |
|----------|----------|
| pgAdmin / DBeaver | GUI untuk PostgreSQL |
| Redis Insight | GUI untuk Redis |
| Qdrant Web UI | GUI vector database (included di port 6333) |
| VS Code | Code editor (recommended) |
| Bruno / Insomnia | API testing |
| Flower | Celery task monitoring |

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
- Thunder Client (rangav.vscode-thunder-client)
- Error Lens (usernamehw.errorlens)
```

---

## 2. Project Setup Step-by-Step

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ureport-ai.git
cd ureport-ai
```

### Step 2: Setup Frontend (apps/web)

```bash
# Install pnpm jika belum
npm install -g pnpm

# Install frontend dependencies
cd apps/web
pnpm install

# Copy environment file
cp .env.example .env.local
```

### Step 3: Setup Backend (apps/api)

```bash
# Install uv jika belum (Python package manager modern)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install backend dependencies
cd apps/api
uv sync

# Copy environment file
cp .env.example .env
```

### Step 4: Setup Infrastructure (Docker)

```bash
# Start semua infrastructure services
docker compose -f infra/docker/compose.dev.yml up -d

# Verify semua services running
docker compose -f infra/docker/compose.dev.yml ps
```

### Step 5: Run Database Migrations

```bash
cd apps/api

# Run migrations menggunakan uv
uv run alembic upgrade head

# Seed data (optional, untuk data dummy)
uv run python -m scripts.seed
```

### Step 6: Start Development Servers

```bash
# Terminal 1: Frontend (Next.js)
cd apps/web
pnpm run start:dev

# Terminal 2: Backend (FastAPI)
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Celery Worker (background jobs)
cd apps/api
uv run celery -A app.worker worker --loglevel=info

# Terminal 4: Celery Beat (periodic tasks, optional)
cd apps/api
uv run celery -A app.worker beat --loglevel=info
```

### Step 7: Verify Setup

| Service | URL | Keterangan |
|---------|-----|-----------|
| Frontend | localhost:3000 | Next.js App |
| Backend API | localhost:8000/docs | FastAPI Swagger |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache dan broker |
| Qdrant UI | localhost:6333/dashboard | Vector DB |
| MinIO Console | localhost:9001 | Object storage |
| Flower | localhost:5555 | Celery monitoring |

---

## 3. Docker Compose (Development Configuration)

File: `infra/docker/compose.dev.yml`

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: ureport-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ureport
      POSTGRES_PASSWORD: ureport_secret
      POSTGRES_DB: ureport_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ureport -d ureport_ai"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ureport-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ureport-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: ureport-minio
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio-init:
    image: minio/mc:latest
    container_name: ureport-minio-init
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin minioadmin123;
      mc mb local/ureport-files --ignore-existing;
      mc mb local/ureport-reports --ignore-existing;
      exit 0;
      "

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  qdrant_data:
    driver: local
  minio_data:
    driver: local

networks:
  default:
    name: ureport-network
```

---

## 4. Environment Variables

### apps/web/.env.local (Frontend)

```bash
# ============================================
# APP CONFIGURATION
# ============================================
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME="uReport AI"
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# AUTHENTICATION (NextAuth.js)
# ============================================
# Generate: openssl rand -base64 32
NEXTAUTH_SECRET="your-random-secret-here-generate-with-openssl"
NEXTAUTH_URL="http://localhost:3000"

# ============================================
# LLM PROVIDER KEYS (untuk Vercel AI SDK di frontend)
# ============================================
# Hanya jika menggunakan edge/server actions langsung
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
CEREBRAS_API_KEY="csk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GOOGLE_GENERATIVE_AI_API_KEY="AIzaxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### apps/api/.env (Backend)

```bash
# ============================================
# APP CONFIGURATION
# ============================================
APP_ENV=development
APP_DEBUG=true
APP_NAME="uReport AI API"
APP_VERSION=0.1.0
CORS_ORIGINS=http://localhost:3000

# ============================================
# DATABASE (PostgreSQL + asyncpg)
# ============================================
DATABASE_URL="postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ============================================
# REDIS
# ============================================
REDIS_URL="redis://localhost:6379/0"
REDIS_CACHE_DB=1
REDIS_CELERY_DB=2

# ============================================
# S3 / MINIO (Object Storage)
# ============================================
S3_ENDPOINT="http://localhost:9000"
S3_ACCESS_KEY="minioadmin"
S3_SECRET_KEY="minioadmin123"
S3_BUCKET_NAME="ureport-files"
S3_REPORTS_BUCKET="ureport-reports"
S3_REGION="us-east-1"
S3_USE_SSL=false

# ============================================
# LLM PROVIDERS
# ============================================
# Groq - https://console.groq.com/keys
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Cerebras - https://cloud.cerebras.ai/
CEREBRAS_API_KEY="csk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Google Gemini - https://aistudio.google.com/apikey
GOOGLE_GENERATIVE_AI_API_KEY="AIzaxxxxxxxxxxxxxxxxxxxxxxxxx"

# Sumopod (Custom/Self-hosted)
SUMOPOD_API_URL="https://api.sumopod.com/v1"
SUMOPOD_API_KEY="your-sumopod-key"

# Default LLM configuration
DEFAULT_LLM_PROVIDER="groq"
DEFAULT_LLM_MODEL="llama-3.3-70b-versatile"

# ============================================
# QDRANT (Vector Database)
# ============================================
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
QDRANT_COLLECTION_NAME="ureport_documents"

# ============================================
# EMBEDDINGS
# ============================================
EMBEDDING_MODEL="BAAI/bge-m3"
EMBEDDING_DIMENSION=1024

# ============================================
# CELERY (Background Jobs)
# ============================================
CELERY_BROKER_URL="redis://localhost:6379/2"
CELERY_RESULT_BACKEND="redis://localhost:6379/3"

# ============================================
# AUTHENTICATION
# ============================================
JWT_SECRET_KEY="your-jwt-secret-key-min-32-chars"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# REPORT GENERATION
# ============================================
REPORT_OUTPUT_DIR="/tmp/ureport-reports"
MAX_REPORT_GENERATION_TIME=300
WEASYPRINT_DPI=150
```

---

## 5. Alembic Migrations

### Konfigurasi

Alembic dikonfigurasi di `apps/api/alembic.ini` dan `apps/api/alembic/env.py`. Menggunakan async engine dengan `asyncpg`.

### Perintah Umum

```bash
cd apps/api

# Buat migration baru (autogenerate dari model changes)
uv run alembic revision --autogenerate -m "add users table"

# Buat migration kosong (untuk data migration)
uv run alembic revision -m "seed initial roles"

# Jalankan semua migration yang pending
uv run alembic upgrade head

# Jalankan satu migration ke depan
uv run alembic upgrade +1

# Rollback satu migration
uv run alembic downgrade -1

# Rollback ke revision tertentu
uv run alembic downgrade abc123

# Rollback semua (kembali ke awal)
uv run alembic downgrade base

# Lihat history migration
uv run alembic history

# Lihat current revision
uv run alembic current

# Lihat migration yang pending
uv run alembic heads

# Generate SQL tanpa eksekusi (offline mode)
uv run alembic upgrade head --sql > migration.sql
```

### Best Practices

1. **Selalu review autogenerated migration** sebelum commit
2. **Jangan edit migration yang sudah di-apply** di production
3. **Beri nama deskriptif:** `add_reports_status_column`, bukan `update_1`
4. **Test downgrade:** Pastikan `downgrade()` function bekerja
5. **Data migration terpisah:** Jangan campur schema dan data migration
6. **Branching:** Jika ada konflik, gunakan `alembic merge heads`

### Contoh Migration File

```python
"""add reports table

Revision ID: abc123def456
Revises: prev_revision_id
Create Date: 2025-05-27 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'abc123def456'
down_revision = 'prev_revision_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_reports_user_id', 'reports', ['user_id'])
    op.create_index('ix_reports_status', 'reports', ['status'])


def downgrade() -> None:
    op.drop_index('ix_reports_status')
    op.drop_index('ix_reports_user_id')
    op.drop_table('reports')
```

---

## 6. Makefile Commands

File: `Makefile` (root project)

```makefile
.PHONY: help install build start stop test lint format migrate seed clean

# ============================================
# HELP
# ============================================
help: ## Tampilkan daftar perintah
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# DEVELOPMENT
# ============================================
install: ## Install semua dependencies
	cd apps/web && pnpm install
	cd apps/api && uv sync

dev: ## Start semua services untuk development
	docker compose -f infra/docker/compose.dev.yml up -d
	@echo "Infrastructure started. Run 'make dev-fe' dan 'make dev-be' di terminal terpisah."

dev-fe: ## Start frontend development server
	cd apps/web && pnpm run dev

dev-be: ## Start backend development server
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker: ## Start Celery worker
	cd apps/api && uv run celery -A app.worker worker --loglevel=info

dev-beat: ## Start Celery beat scheduler
	cd apps/api && uv run celery -A app.worker beat --loglevel=info

# ============================================
# TESTING
# ============================================
test: test-be test-fe ## Run semua tests

test-be: ## Run backend tests
	cd apps/api && uv run pytest -v --cov=app --cov-report=term-missing

test-fe: ## Run frontend tests
	cd apps/web && pnpm test

test-be-watch: ## Run backend tests dalam watch mode
	cd apps/api && uv run pytest-watch

test-fe-watch: ## Run frontend tests dalam watch mode
	cd apps/web && pnpm test:watch

# ============================================
# DATABASE
# ============================================
migrate: ## Run database migrations
	cd apps/api && uv run alembic upgrade head

migrate-new: ## Buat migration baru (usage: make migrate-new MSG="add users table")
	cd apps/api && uv run alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback satu migration
	cd apps/api && uv run alembic downgrade -1

migrate-history: ## Tampilkan migration history
	cd apps/api && uv run alembic history

seed: ## Seed database dengan data dummy
	cd apps/api && uv run python -m scripts.seed

# ============================================
# CODE QUALITY
# ============================================
lint: lint-be lint-fe ## Lint semua code

lint-be: ## Lint backend (ruff)
	cd apps/api && uv run ruff check .

lint-fe: ## Lint frontend (eslint)
	cd apps/web && pnpm lint

format: format-be format-fe ## Format semua code

format-be: ## Format backend (ruff format)
	cd apps/api && uv run ruff format .

format-fe: ## Format frontend (prettier)
	cd apps/web && pnpm format

typecheck: ## Run type checking
	cd apps/web && pnpm typecheck
	cd apps/api && uv run mypy app/

# ============================================
# DOCKER
# ============================================
docker-up: ## Start infrastructure containers
	docker compose -f infra/docker/compose.dev.yml up -d

docker-down: ## Stop infrastructure containers
	docker compose -f infra/docker/compose.dev.yml down

docker-logs: ## Tampilkan logs dari containers
	docker compose -f infra/docker/compose.dev.yml logs -f

docker-reset: ## Reset semua containers dan volumes (DESTRUCTIVE)
	docker compose -f infra/docker/compose.dev.yml down -v
	docker compose -f infra/docker/compose.dev.yml up -d

# ============================================
# BUILD & DEPLOY
# ============================================
build: build-fe build-be ## Build semua untuk production

build-fe: ## Build frontend
	cd apps/web && pnpm build

build-be: ## Build backend Docker image
	docker build -f infra/docker/Dockerfile.api -t ureport-api:latest .

# ============================================
# UTILITIES
# ============================================
clean: ## Bersihkan artifacts
	rm -rf apps/web/.next apps/web/node_modules/.cache
	find apps/api -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/api/.pytest_cache apps/api/.ruff_cache

flower: ## Start Flower (Celery monitoring UI)
	cd apps/api && uv run celery -A app.worker flower --port=5555
```

---

## 7. Common Development Tasks

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

1. Buat file router baru:

```python
# apps/api/app/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.report import ReportCreate, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    return await service.create(data)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
```

2. Register router di `app/main.py`:

```python
from app.routers import reports

app.include_router(reports.router, prefix="/api/v1")
```

3. Buat schema di `app/schemas/report.py`
4. Buat service di `app/services/report_service.py`
5. Buat tests di `tests/routers/test_reports.py`

### 7.3 Menambah LangGraph Skill/Tool Baru

1. Buat tool definition:

```python
# apps/api/app/agent/tools/data_analysis.py
from langchain_core.tools import tool
from typing import Annotated


@tool
def analyze_dataframe(
    query: Annotated[str, "Natural language query tentang data"],
    dataset_id: Annotated[str, "ID dataset yang akan dianalisis"],
) -> str:
    """Menganalisis dataset berdasarkan query pengguna.
    Gunakan tool ini ketika pengguna meminta analisis statistik atau insight dari data.
    """
    # Implementation here
    pass
```

2. Register tool di agent graph:

```python
# apps/api/app/agent/graph.py
from app.agent.tools.data_analysis import analyze_dataframe

tools = [analyze_dataframe, ...]
```

3. Tambahkan conditional routing jika diperlukan
4. Buat tests di `tests/agent/tools/test_data_analysis.py`

### 7.4 Menambah Alembic Migration Baru

```bash
cd apps/api

# 1. Edit model di app/models/
# 2. Generate migration
uv run alembic revision --autogenerate -m "add status column to reports"

# 3. Review file migration yang di-generate (di alembic/versions/)
# 4. Test upgrade
uv run alembic upgrade head

# 5. Test downgrade
uv run alembic downgrade -1

# 6. Upgrade lagi
uv run alembic upgrade head
```

### 7.5 Menambah Report Template Baru (Jinja2)

1. Buat template HTML:

```html
<!-- apps/api/app/templates/reports/research_report.html -->
{% extends "base_report.html" %}

{% block title %}{{ report.title }}{% endblock %}

{% block content %}
<section class="chapter">
  <h1>BAB I - Pendahuluan</h1>
  <div class="content">
    {{ sections.pendahuluan | safe }}
  </div>
</section>

<section class="chapter" style="page-break-before: always;">
  <h1>BAB II - Tinjauan Pustaka</h1>
  <div class="content">
    {{ sections.tinjauan | safe }}
  </div>
</section>

{% for chart in charts %}
<figure class="chart">
  <img src="{{ chart.image_path }}" alt="{{ chart.caption }}" />
  <figcaption>{{ chart.caption }}</figcaption>
</figure>
{% endfor %}
{% endblock %}
```

2. Buat CSS untuk print:

```css
/* apps/api/app/templates/reports/styles/research.css */
@page {
  size: A4;
  margin: 2.5cm 2cm;
  @top-center { content: string(chapter-title); }
  @bottom-center { content: counter(page); }
}
```

3. Register template di config:

```python
# apps/api/app/config/report_templates.py
TEMPLATES = {
    "research": {
        "name": "Laporan Penelitian",
        "template": "reports/research_report.html",
        "stylesheet": "reports/styles/research.css",
        "sections": ["pendahuluan", "tinjauan", "metodologi", "hasil", "kesimpulan"],
    }
}
```

### 7.6 Menambah LLM Provider Baru ke LiteLLM Config

1. Update konfigurasi LiteLLM:

```python
# apps/api/app/config/litellm_config.py
LITELLM_CONFIG = {
    "model_list": [
        {
            "model_name": "default-fast",
            "litellm_params": {
                "model": "groq/llama-3.3-70b-versatile",
                "api_key": "os.environ/GROQ_API_KEY",
            },
        },
        {
            "model_name": "default-fast",  # fallback
            "litellm_params": {
                "model": "cerebras/llama-3.3-70b",
                "api_key": "os.environ/CEREBRAS_API_KEY",
            },
        },
        {
            "model_name": "default-smart",
            "litellm_params": {
                "model": "gemini/gemini-2.0-flash",
                "api_key": "os.environ/GOOGLE_GENERATIVE_AI_API_KEY",
            },
        },
        # Tambahkan provider baru di sini
        {
            "model_name": "new-provider",
            "litellm_params": {
                "model": "openai/model-name",  # format: provider/model
                "api_key": "os.environ/NEW_PROVIDER_API_KEY",
                "api_base": "https://api.newprovider.com/v1",
            },
        },
    ],
    "router_settings": {
        "routing_strategy": "latency-based-routing",
        "num_retries": 3,
        "retry_after": 5,
        "fallbacks": [
            {"default-fast": ["default-smart"]},
        ],
    },
}
```

2. Tambahkan API key ke `.env`:

```bash
NEW_PROVIDER_API_KEY="your-api-key-here"
```

3. Test koneksi:

```python
uv run python -c "
import litellm
response = litellm.completion(
    model='openai/model-name',
    messages=[{'role': 'user', 'content': 'Hello'}],
    api_base='https://api.newprovider.com/v1',
    api_key='your-key'
)
print(response.choices[0].message.content)
"
```

---

## 8. Testing Strategy

### Backend Testing (pytest + pytest-asyncio + httpx)

**Stack:**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client (pengganti TestClient untuk async)
- `pytest-cov` - Code coverage
- `factory-boy` - Test data factories
- `faker` - Fake data generation

**Struktur direktori:**

```
apps/api/tests/
|-- conftest.py              # Shared fixtures (db session, client, auth)
|-- factories/               # Factory Boy factories
|   |-- user_factory.py
|   |-- report_factory.py
|-- routers/                 # API endpoint tests
|   |-- test_auth.py
|   |-- test_reports.py
|   |-- test_chat.py
|-- services/                # Business logic tests
|   |-- test_report_service.py
|   |-- test_llm_service.py
|-- agent/                   # Agent/LangGraph tests
|   |-- test_graph.py
|   |-- tools/
|       |-- test_data_analysis.py
|-- utils/                   # Utility function tests
```

**conftest.py (shared fixtures):**

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai_test"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(client, db_session):
    # Create test user dan set auth header
    # ...
    pass
```

**Contoh test:**

```python
# tests/routers/test_reports.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_report(client: AsyncClient):
    response = await client.post("/api/v1/reports/", json={
        "title": "Test Report",
        "template": "research",
        "dataset_id": "test-dataset-id",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Report"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient):
    response = await client.get("/api/v1/reports/nonexistent-id")
    assert response.status_code == 404
```

**Menjalankan tests:**

```bash
cd apps/api

# Run semua tests
uv run pytest -v

# Run dengan coverage
uv run pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific file
uv run pytest tests/routers/test_reports.py -v

# Run specific test
uv run pytest tests/routers/test_reports.py::test_create_report -v

# Run dengan output print (debug)
uv run pytest -s -v
```

### Frontend Testing (Vitest + Testing Library)

**Stack:**
- `vitest` - Test runner (pengganti Jest, lebih cepat)
- `@testing-library/react` - Component testing
- `@testing-library/user-event` - User interaction simulation
- `msw` - API mocking (Mock Service Worker)

**Struktur direktori:**

```
apps/web/src/
|-- __tests__/                 # Integration tests
|   |-- pages/
|-- components/
|   |-- ui/
|   |   |-- button.test.tsx    # Co-located tests
|   |-- chat/
|   |   |-- chat-input.test.tsx
|-- lib/
|   |-- utils.test.ts
|-- mocks/
|   |-- handlers.ts           # MSW handlers
|   |-- server.ts             # MSW server setup
```

**Contoh test:**

```typescript
// src/components/chat/chat-input.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { ChatInput } from './chat-input'

describe('ChatInput', () => {
  it('renders input field', () => {
    render(<ChatInput onSubmit={vi.fn()} />)
    expect(screen.getByPlaceholderText(/ketik pesan/i)).toBeInTheDocument()
  })

  it('calls onSubmit when form is submitted', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} />)

    await user.type(screen.getByRole('textbox'), 'Hello AI')
    await user.click(screen.getByRole('button', { name: /kirim/i }))

    expect(onSubmit).toHaveBeenCalledWith('Hello AI')
  })

  it('disables input when loading', () => {
    render(<ChatInput onSubmit={vi.fn()} isLoading={true} />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })
})
```

**Menjalankan tests:**

```bash
cd apps/web

# Run semua tests
pnpm test

# Run dalam watch mode
pnpm test:watch

# Run dengan coverage
pnpm test:coverage

# Run specific file
pnpm test src/components/chat/chat-input.test.tsx
```

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

- Add base report template with header/footer
- Add research report template
- Add CSS paged media styles
- Integrate with Celery for async generation

Closes #42
```

```
fix(chat): resolve streaming disconnect on slow connections

Increase SSE timeout from 30s to 120s and add
automatic reconnection logic in useChat hook.
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
- [ ] Code sudah di-lint dan format
- [ ] Self-review sudah dilakukan
- [ ] Dokumentasi diupdate (jika perlu)
- [ ] Tidak ada console.log/print debug
```

### Workflow

```
main (protected)
  |
  |-- feature/add-report-export (development)
  |     |
  |     |-- commit: feat(reports): add base template
  |     |-- commit: feat(reports): add WeasyPrint integration
  |     |-- commit: test(reports): add PDF generation tests
  |     |
  |     |-- PR -> main (require review + CI passing)
  |
  |-- fix/chat-streaming (hotfix)
        |
        |-- commit: fix(chat): resolve streaming timeout
        |
        |-- PR -> main
```

### Pre-commit Hooks

Menggunakan `pre-commit` framework:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: bash -c 'cd apps/api && uv run ruff check .'
        language: system
        types: [python]

      - id: ruff-format
        name: ruff format
        entry: bash -c 'cd apps/api && uv run ruff format --check .'
        language: system
        types: [python]

      - id: eslint
        name: eslint
        entry: bash -c 'cd apps/web && pnpm lint'
        language: system
        types: [typescript, tsx]
```

---

## 10. Deployment Options

### Option A: Vercel + Railway (Recommended untuk MVP)

**Frontend (Vercel):**
- Push ke GitHub, Vercel auto-deploy dari `main` branch
- Environment variables di Vercel Dashboard
- Edge functions untuk API routes yang ringan
- Preview deployments untuk setiap PR

**Backend (Railway):**
- Deploy FastAPI dari Dockerfile
- Managed PostgreSQL, Redis tersedia
- Auto-scaling berdasarkan traffic
- Environment variables di Railway Dashboard

**Infrastruktur (Railway/Managed):**
- PostgreSQL: Railway managed atau Supabase
- Redis: Railway managed atau Upstash
- Qdrant: Qdrant Cloud (free tier tersedia)
- MinIO: Cloudflare R2 atau AWS S3

### Option B: Docker Self-hosted VPS

Untuk deployment di VPS (Hetzner, DigitalOcean, dll):

```yaml
# infra/docker/compose.prod.yml
version: "3.8"

services:
  web:
    build:
      context: ../..
      dockerfile: infra/docker/Dockerfile.web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - api

  api:
    build:
      context: ../..
      dockerfile: infra/docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
    depends_on:
      - postgres
      - redis
      - qdrant

  worker:
    build:
      context: ../..
      dockerfile: infra/docker/Dockerfile.api
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    depends_on:
      - redis
      - postgres

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - certbot_data:/var/www/certbot
    depends_on:
      - web
      - api

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_prod_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_prod_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY}

volumes:
  postgres_prod_data:
  redis_prod_data:
  qdrant_prod_data:
  certbot_data:
```

**Deployment commands:**

```bash
# Build dan deploy
docker compose -f infra/docker/compose.prod.yml build
docker compose -f infra/docker/compose.prod.yml up -d

# Run migrations
docker compose -f infra/docker/compose.prod.yml exec api alembic upgrade head

# Lihat logs
docker compose -f infra/docker/compose.prod.yml logs -f api worker
```

### Option C: Full Cloud (Enterprise)

Untuk skala besar:
- **Frontend:** Vercel atau Cloudflare Pages
- **Backend:** AWS ECS / Google Cloud Run / Azure Container Apps
- **Database:** AWS RDS / Google Cloud SQL (PostgreSQL)
- **Redis:** AWS ElastiCache / Google Memorystore
- **Vector DB:** Qdrant Cloud (managed)
- **Storage:** AWS S3 / Google Cloud Storage
- **CDN:** Cloudflare
- **Monitoring:** Datadog / Grafana Cloud
- **CI/CD:** GitHub Actions + ArgoCD

### Deployment Checklist

- [ ] Environment variables sudah di-set
- [ ] Database migrations sudah di-run
- [ ] SSL certificates sudah di-setup
- [ ] Backup strategy sudah di-configure
- [ ] Monitoring dan alerting aktif
- [ ] Rate limiting di-enable
- [ ] CORS origins di-restrict ke domain production
- [ ] Debug mode di-disable
- [ ] Error tracking (Sentry) di-setup
- [ ] Health check endpoints tersedia
- [ ] Log rotation di-configure

---

## Quick Reference

| Task | Command |
|------|---------|
| Start semua | `make dev` lalu `make dev-fe` + `make dev-be` |
| Run tests | `make test` |
| Lint code | `make lint` |
| Format code | `make format` |
| New migration | `make migrate-new MSG="description"` |
| Apply migrations | `make migrate` |
| Seed data | `make seed` |
| Start containers | `make docker-up` |
| Stop containers | `make docker-down` |
| Build production | `make build` |

---

> **Tip:** Bookmark halaman ini! Ini adalah referensi utama untuk workflow development sehari-hari di project uReport AI v2.
