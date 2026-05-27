# uReport AI - Development Guide

## Prerequisites (Yang Harus Diinstall)

### Wajib (Must Have)

| Software | Version | Kegunaan | Install Link |
|----------|---------|----------|-------------|
| Node.js | 20+ LTS | JavaScript runtime | [nodejs.org](https://nodejs.org/) |
| Bun | 1.0+ | Package manager & runtime (lebih cepat dari npm) | [bun.sh](https://bun.sh/) |
| Python | 3.11+ | Data processing microservice | [python.org](https://www.python.org/) |
| PostgreSQL | 16+ | Database utama | [postgresql.org](https://www.postgresql.org/download/) |
| Redis | 7+ | Cache & job queue | [redis.io](https://redis.io/download) |
| Git | 2.40+ | Version control | [git-scm.com](https://git-scm.com/) |
| Docker | 24+ | Containerization | [docker.com](https://www.docker.com/get-started/) |

### Optional (Nice to Have)

| Software | Kegunaan |
|----------|----------|
| Docker Compose | Multi-container orchestration (included with Docker Desktop) |
| pgAdmin | GUI untuk PostgreSQL |
| Redis Insight | GUI untuk Redis |
| VS Code | Code editor (recommended) |
| Postman/Insomnia | API testing |

### VS Code Extensions (Recommended)

```
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Prisma
- Python
- GitLens
- Thunder Client (API testing)
- Error Lens
```

---

## Project Setup from Scratch

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ureport-ai.git
cd ureport-ai
```

### Step 2: Install Dependencies (Frontend/Backend Node.js)

```bash
# Install bun jika belum
curl -fsSL https://bun.sh/install | bash

# Install dependencies
bun install
```

### Step 3: Setup Python Environment

```bash
# Buat virtual environment
cd services/python
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Setup Database

```bash
# Option A: Menggunakan Docker (recommended)
docker compose up -d postgres redis minio

# Option B: Manual install
# 1. Install PostgreSQL 16
# 2. Create database
createdb ureport_ai

# 3. Enable pgvector extension
psql ureport_ai -c "CREATE EXTENSION vector;"
```

### Step 5: Configure Environment

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan credentials kamu
# (lihat section Environment Variables di bawah)
```

### Step 6: Run Database Migrations

```bash
# Generate Prisma client
bunx prisma generate

# Run migrations
bunx prisma migrate dev

# Seed data (optional - untuk data dummy)
bunx prisma db seed
```

### Step 7: Start Development

```bash
# Terminal 1: Next.js frontend + API
bun run dev

# Terminal 2: Python microservice
cd services/python
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 3: BullMQ Worker (optional, untuk report generation)
bun run worker
```

### Step 8: Verify Setup

```bash
# Frontend: http://localhost:3000
# Python API: http://localhost:8000/docs (Swagger UI)
# MinIO Console: http://localhost:9001 (admin/admin123)
```

---

## Environment Variables

Buat file `.env` di root project:

```bash
# ============================================
# APP CONFIGURATION
# ============================================
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME="uReport AI"

# ============================================
# DATABASE
# ============================================
# PostgreSQL connection string
DATABASE_URL="postgresql://postgres:password@localhost:5432/ureport_ai?schema=public"

# ============================================
# AUTHENTICATION
# ============================================
# NextAuth secret (generate: openssl rand -base64 32)
NEXTAUTH_SECRET="your-random-secret-here-generate-with-openssl"
NEXTAUTH_URL="http://localhost:3000"

# ============================================
# LLM PROVIDERS - API KEYS
# ============================================

# Groq - Dapatkan di: https://console.groq.com/keys
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Cerebras - Dapatkan di: https://cloud.cerebras.ai/
CEREBRAS_API_KEY="csk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Google Gemini - Dapatkan di: https://aistudio.google.com/apikey
GOOGLE_GENERATIVE_AI_API_KEY="AIzaxxxxxxxxxxxxxxxxxxxxxxxxx"

# Sumopod (Custom) - Endpoint dan key custom kamu
SUMOPOD_API_URL="https://api.sumopod.com/v1"
SUMOPOD_API_KEY="your-sumopod-key"

# ============================================
# PYTHON MICROSERVICE
# ============================================
PYTHON_SERVICE_URL="http://localhost:8000"

# ============================================
# FILE STORAGE (MinIO / S3)
# ============================================
S3_ENDPOINT="http://localhost:9000"
S3_ACCESS_KEY="minioadmin"
S3_SECRET_KEY="minioadmin123"
S3_BUCKET_NAME="ureport-files"
S3_REGION="us-east-1"

# ============================================
# REDIS
# ============================================
REDIS_URL="redis://localhost:6379"

# ============================================
# EMBEDDING MODEL
# ============================================
# Pilih salah satu:
# Option 1: OpenAI embeddings (bayar, tapi bagus)
# OPENAI_API_KEY="sk-xxxxx"
# EMBEDDING_MODEL="text-embedding-3-small"

# Option 2: Local/HuggingFace (gratis, jalan lokal)
EMBEDDING_MODEL="all-MiniLM-L6-v2"
EMBEDDING_DIMENSION=384

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# ============================================
# PDF GENERATION
# ============================================
PUPPETEER_EXECUTABLE_PATH="/usr/bin/chromium-browser"
# Atau biarkan kosong untuk auto-detect
```

---

## Directory Structure (Recommended)

```
ureport-ai/
├── docs/                          # Dokumentasi project (kamu sedang di sini!)
│   ├── BLUEPRINT.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── TECHSTACK.md
│   ├── SKILLS_REQUIRED.md
│   ├── API_DESIGN.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── MEMORY.md
│
├── src/                           # Next.js source code
│   ├── app/                       # App Router pages & layouts
│   │   ├── (auth)/               # Auth pages (login, register)
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (chat)/               # Chat pages
│   │   │   ├── page.tsx          # Main chat page
│   │   │   └── [id]/            # Specific conversation
│   │   ├── reports/              # Report pages
│   │   │   ├── page.tsx          # Report list
│   │   │   ├── [id]/            # Report detail/editor
│   │   │   └── new/             # Create new report
│   │   ├── knowledge/            # Knowledge base management
│   │   ├── settings/             # User settings
│   │   ├── api/                  # API Route handlers
│   │   │   ├── auth/
│   │   │   ├── conversations/
│   │   │   ├── messages/
│   │   │   ├── files/
│   │   │   ├── analysis/
│   │   │   ├── reports/
│   │   │   ├── llm/
│   │   │   └── knowledge/
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Landing page
│   │
│   ├── components/               # Reusable UI components
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── chat/                 # Chat-specific components
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatSidebar.tsx
│   │   │   ├── MessageContent.tsx
│   │   │   └── FileUploadZone.tsx
│   │   ├── charts/              # Chart components
│   │   │   ├── BarChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   ├── PieChart.tsx
│   │   │   └── ChartRenderer.tsx
│   │   ├── reports/             # Report components
│   │   │   ├── ReportEditor.tsx
│   │   │   ├── ReportSection.tsx
│   │   │   └── ReportPreview.tsx
│   │   ├── tables/             # Data table components
│   │   │   └── DataTable.tsx
│   │   └── layout/             # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   │
│   ├── lib/                    # Utility libraries
│   │   ├── prisma.ts           # Prisma client instance
│   │   ├── auth.ts             # Auth configuration
│   │   ├── redis.ts            # Redis client
│   │   ├── s3.ts               # S3/MinIO client
│   │   ├── utils.ts            # General utilities
│   │   └── llm/                # LLM integration
│   │       ├── router.ts       # LLM Router (strategy pattern)
│   │       ├── providers/
│   │       │   ├── groq.ts
│   │       │   ├── cerebras.ts
│   │       │   ├── gemini.ts
│   │       │   └── sumopod.ts
│   │       ├── prompts/        # Prompt templates
│   │       │   ├── analysis.ts
│   │       │   ├── chart.ts
│   │       │   └── report.ts
│   │       └── types.ts        # LLM-related types
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useChat.ts
│   │   ├── useFileUpload.ts
│   │   └── useStreamResponse.ts
│   │
│   ├── store/                  # Zustand stores
│   │   ├── chatStore.ts
│   │   ├── settingsStore.ts
│   │   └── reportStore.ts
│   │
│   ├── types/                  # TypeScript type definitions
│   │   ├── chat.ts
│   │   ├── report.ts
│   │   ├── analysis.ts
│   │   └── api.ts
│   │
│   └── styles/                 # Global styles
│       └── globals.css
│
├── services/                   # Microservices
│   └── python/                # Python data processing service
│       ├── main.py            # FastAPI entry point
│       ├── routers/           # API routers
│       │   ├── parse.py       # File parsing endpoints
│       │   ├── analyze.py     # Analysis endpoints
│       │   └── chart.py       # Chart data endpoints
│       ├── services/          # Business logic
│       │   ├── file_parser.py
│       │   ├── analyzer.py
│       │   └── chart_generator.py
│       ├── models/            # Pydantic models
│       │   └── schemas.py
│       ├── requirements.txt   # Python dependencies
│       └── Dockerfile
│
├── prisma/                    # Database schema & migrations
│   ├── schema.prisma
│   ├── migrations/
│   └── seed.ts
│
├── workers/                   # Background job workers
│   └── reportWorker.ts       # Report generation worker
│
├── public/                    # Static files
│   ├── logo.svg
│   └── favicon.ico
│
├── docker/                    # Docker configurations
│   ├── Dockerfile.nextjs
│   ├── Dockerfile.python
│   └── nginx.conf
│
├── .env.example               # Environment template
├── .gitignore
├── docker-compose.yml         # Docker Compose configuration
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── postcss.config.mjs
└── README.md
```

---

## How to Run Locally

### Option A: Semua dengan Docker (Paling Mudah)

```bash
# Start semua services
docker compose up

# Akses:
# - Frontend: http://localhost:3000
# - Python API: http://localhost:8000
# - MinIO: http://localhost:9001
# - pgAdmin: http://localhost:5050 (optional)
```

### Option B: Development Mode (Recommended untuk coding)

```bash
# Terminal 1: Start infrastructure (DB, Redis, MinIO)
docker compose up -d postgres redis minio

# Terminal 2: Start Next.js (frontend + API)
bun run dev

# Terminal 3: Start Python service
cd services/python
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 4 (optional): Start worker
bun run worker:dev
```

### Option C: Tanpa Docker (Manual semua)

```bash
# 1. Install dan start PostgreSQL manually
# 2. Install dan start Redis manually
# 3. Setup MinIO atau gunakan local filesystem

# Start Next.js
bun run dev

# Start Python
cd services/python && python -m uvicorn main:app --reload --port 8000
```

---

## Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Next.js Application
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.nextjs
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ureport_ai
      - REDIS_URL=redis://redis:6379
      - PYTHON_SERVICE_URL=http://python:8000
      - S3_ENDPOINT=http://minio:9000
    depends_on:
      - postgres
      - redis
      - minio
      - python

  # Python Microservice
  python:
    build:
      context: ./services/python
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - S3_ENDPOINT=http://minio:9000
    volumes:
      - ./services/python:/app

  # PostgreSQL + pgvector
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ureport_ai
    volumes:
      - pgdata:/var/lib/postgresql/data

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  # MinIO (S3-compatible storage)
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  redisdata:
  miniodata:
```

---

## Development Workflow

### Git Flow (Branching Strategy)

```mermaid
gitGraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "setup"
    
    branch feature/chat-ui
    checkout feature/chat-ui
    commit id: "chat component"
    commit id: "styling"
    checkout develop
    merge feature/chat-ui
    
    branch feature/file-upload
    checkout feature/file-upload
    commit id: "upload API"
    commit id: "parser"
    checkout develop
    merge feature/file-upload
    
    checkout main
    merge develop tag: "v0.1.0"
    
    checkout develop
    branch feature/multi-llm
    commit id: "llm router"
    checkout develop
    merge feature/multi-llm
    
    checkout main
    merge develop tag: "v0.2.0"
```

### Branch Naming Convention

```
main              - Production-ready code
develop           - Integration branch
feature/xxx       - New features (feature/chat-ui, feature/file-upload)
fix/xxx           - Bug fixes (fix/upload-error)
hotfix/xxx        - Urgent production fixes
refactor/xxx      - Code refactoring
```

### Commit Message Convention

```
feat: add chat streaming response
fix: resolve file upload timeout
docs: update API documentation
style: format chat component
refactor: extract LLM router to separate module
test: add unit tests for analysis service
chore: update dependencies
perf: optimize chart rendering
```

---

## Testing Strategy

### Unit Tests

```bash
# Run semua tests
bun test

# Run specific test file
bun test src/lib/llm/__tests__/router.test.ts

# Watch mode
bun test --watch
```

### Test Structure

```
src/
├── lib/
│   └── llm/
│       ├── router.ts
│       └── __tests__/
│           └── router.test.ts
├── components/
│   └── chat/
│       ├── ChatMessage.tsx
│       └── __tests__/
│           └── ChatMessage.test.tsx
```

### Python Tests

```bash
cd services/python
pytest
pytest tests/test_analyzer.py -v
```

### E2E Tests (Optional)

```bash
# Menggunakan Playwright
bun run test:e2e
```

---

## Deployment Options

### Option 1: Vercel + Railway (Easiest, ada free tier)

```
Frontend (Next.js)  -> Vercel (auto-deploy dari GitHub)
Python Service      -> Railway
PostgreSQL          -> Railway (atau Neon, Supabase)
Redis               -> Railway (atau Upstash)
File Storage        -> Cloudflare R2 (atau AWS S3)
```

**Pros:** Easy setup, auto-scaling, free tier untuk development
**Cons:** Biaya bisa naik di traffic tinggi, cold starts

### Option 2: Docker Self-Hosted (VPS)

```
Semua service      -> Docker Compose di VPS
                      (DigitalOcean, Hetzner, Contabo)
                      Rp 100-300rb/bulan
```

**Pros:** Full control, predictable cost, no cold starts
**Cons:** Harus manage sendiri (updates, backups, monitoring)

### Option 3: Cloud Platform (AWS/GCP/Azure)

```
Frontend           -> AWS Amplify / GCP Cloud Run
Python             -> AWS ECS / GCP Cloud Run
Database           -> AWS RDS / GCP Cloud SQL
Redis              -> AWS ElastiCache
Storage            -> AWS S3
```

**Pros:** Enterprise-grade, highly scalable
**Cons:** Complex, bisa mahal, steep learning curve

### Recommended untuk Mulai: Option 1 (Vercel + Railway)

Alasan:
- Paling cepat untuk deploy
- Free tier cukup untuk development dan testing
- Auto-deploy dari GitHub push
- Tidak perlu manage server

---

## Common Development Tasks

### Menambah Component shadcn/ui Baru

```bash
bunx shadcn-ui@latest add button
bunx shadcn-ui@latest add dialog
bunx shadcn-ui@latest add sheet
```

### Menambah Database Table/Column

```bash
# 1. Edit prisma/schema.prisma
# 2. Create migration
bunx prisma migrate dev --name add_xxx_table
# 3. Regenerate client
bunx prisma generate
```

### Menambah LLM Provider Baru

1. Buat file baru: `src/lib/llm/providers/new-provider.ts`
2. Implement `LLMProvider` interface
3. Register di `src/lib/llm/router.ts`
4. Tambah API key di `.env`
5. Update UI settings

### Menambah Chart Type Baru

1. Buat component: `src/components/charts/NewChart.tsx`
2. Register di `src/components/charts/ChartRenderer.tsx`
3. Update Python chart data generator
4. Update prompt template untuk chart type baru
