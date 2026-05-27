# uReport AI

> Platform AI Assistant untuk Analisis Data dan Pembuatan Laporan Terstruktur

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12-green?style=flat-square&logo=python)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

## Apa itu uReport AI?

uReport AI adalah aplikasi chat berbasis AI yang dirancang khusus untuk:

1. **Analisis Data** - Upload file Excel/CSV, tanyakan apa saja tentang data, AI menjawab dengan tabel dan grafik
2. **Visualisasi Interaktif** - AI menghasilkan chart interaktif (bar, line, pie, scatter, heatmap) langsung di chat
3. **Pembuatan Laporan** - Generate laporan terstruktur (BAB I s/d BAB V) dengan bantuan AI dan export ke PDF profesional
4. **Multi-LLM** - Pilih AI provider sesuai kebutuhan: Cerebras, Groq, Gemini, atau Sumopod (custom)
5. **RAG (Knowledge Base)** - Upload dokumen referensi, AI gunakan sebagai konteks untuk laporan yang lebih kaya

## Key Features

| Feature | Description |
|---------|-------------|
| Chat AI | Percakapan dengan AI (streaming real-time) |
| File Upload | Upload Excel (.xlsx) dan CSV untuk analisis |
| Table Response | AI merespons dengan tabel data interaktif |
| Chart Response | AI merespons dengan grafik interaktif (Plotly) |
| Multi-LLM | Switch antara Cerebras, Groq, Gemini, Sumopod |
| Report Generation | Laporan otomatis dengan struktur BAB |
| PDF Export | Export laporan ke PDF profesional (WeasyPrint) |
| RAG/Knowledge Base | Enrichment dengan dokumen referensi |
| Dark Mode | Tema gelap untuk kenyamanan mata |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, TailwindCSS, shadcn/ui, Plotly.js |
| **Backend** | Python 3.12, FastAPI, Pydantic v2 |
| **Database** | PostgreSQL 16, SQLAlchemy, Alembic |
| **LLM** | LiteLLM, LangGraph |
| **RAG** | LlamaIndex, Qdrant, bge-m3 |
| **Data** | pandas, Plotly, E2B sandbox |
| **Reports** | Jinja2, WeasyPrint |
| **Queue** | Celery 5, Redis 7 |
| **Storage** | S3-compatible (MinIO/R2) |
| **Auth** | Auth.js (NextAuth v5) |
| **Deploy** | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Node.js 20+ & pnpm
- Python 3.12+ & uv
- Docker & Docker Compose
- API keys (Groq, Cerebras, atau Gemini - minimal satu)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/ureport-ai.git
cd ureport-ai

# 2. Start infrastructure
docker compose -f infra/docker/compose.dev.yml up -d

# 3. Setup environment
cp .env.example .env
# Edit .env dengan API keys kamu

# 4. Install frontend dependencies
cd apps/web && pnpm install

# 5. Install backend dependencies
cd apps/api && uv sync

# 6. Run database migrations
cd apps/api && alembic upgrade head

# 7. Start development
pnpm --filter web dev          # Terminal 1: Next.js
cd apps/api && uvicorn app.main:app --reload  # Terminal 2: FastAPI
```

### Access

- **App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001

## Documentation

Dokumentasi lengkap tersedia di [`MASTERPLAN.md`](./MASTERPLAN.md) dan folder `docs/`:

| Document | Content |
|----------|---------|
| [MASTERPLAN.md](./MASTERPLAN.md) | Ringkasan produk, arsitektur, dan navigasi dokumentasi |
| [01-vision-and-scope.md](./docs/01-vision-and-scope.md) | Visi, target user, problem, scope |
| [02-tech-stack.md](./docs/02-tech-stack.md) | Pilihan tech & rasional per-teknologi |
| [03-architecture.md](./docs/03-architecture.md) | Arsitektur sistem & data flow |
| [04-features-and-user-flows.md](./docs/04-features-and-user-flows.md) | Fitur detail + user journey |
| [05-llm-providers.md](./docs/05-llm-providers.md) | Strategi multi-LLM |
| [06-rag-and-knowledge.md](./docs/06-rag-and-knowledge.md) | RAG: ingestion, chunking, retrieval |
| [07-data-analysis-engine.md](./docs/07-data-analysis-engine.md) | Excel/CSV analyzer, charting |
| [08-report-generation.md](./docs/08-report-generation.md) | PDF report generation |
| [09-database-schema.md](./docs/09-database-schema.md) | Database schema & ERD |
| [10-api-design.md](./docs/10-api-design.md) | API contract & endpoints |
| [11-frontend-design.md](./docs/11-frontend-design.md) | UI/UX & komponen frontend |
| [12-agent-skills-and-memory.md](./docs/12-agent-skills-and-memory.md) | Skill registry + memory |
| [13-roadmap-and-milestones.md](./docs/13-roadmap-and-milestones.md) | Roadmap MVP → V1 → V2 |
| [14-deployment-and-ops.md](./docs/14-deployment-and-ops.md) | Deployment & monitoring |
| [15-security-and-compliance.md](./docs/15-security-and-compliance.md) | Security & privacy |
| [16-skills-and-learning-path.md](./docs/16-skills-and-learning-path.md) | Skills & learning path |
| [17-development-guide.md](./docs/17-development-guide.md) | Development workflow |
| [decisions/ADR-001-to-006.md](./docs/decisions/ADR-001-to-006.md) | Architecture Decision Records |

## Project Structure

```
ureport-ai/
├── apps/
│   ├── web/                # Next.js 15 frontend
│   └── api/                # FastAPI backend
├── packages/
│   ├── shared-types/       # TypeScript types (auto-gen dari OpenAPI)
│   └── prompts/            # Prompt library (markdown)
├── infra/
│   └── docker/             # Docker Compose configs
├── docs/                   # Project documentation (17 files + decisions/)
├── scripts/                # Utility scripts
├── .kiro/                  # Steering & config
├── MASTERPLAN.md           # Project masterplan
└── README.md
```

## Development Phases

- **Phase 1:** MVP - Chat + File Upload + Basic Analysis
- **Phase 2:** Charts/Tables + Multi-LLM Support
- **Phase 3:** RAG + Report Generation + PDF Export
- **Phase 4:** Polish + Optimization + Deployment

Detail lengkap ada di [docs/13-roadmap-and-milestones.md](./docs/13-roadmap-and-milestones.md).

## Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Built with AI, for humans who want to understand their data better.**
