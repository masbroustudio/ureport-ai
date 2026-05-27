# uReport AI

> Platform AI Assistant untuk Analisis Data dan Pembuatan Laporan Terstruktur

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square&logo=python)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

## Apa itu uReport AI?

uReport AI adalah aplikasi chat berbasis AI yang dirancang khusus untuk:

1. **Analisis Data** - Upload file Excel/CSV, tanyakan apa saja tentang data, AI menjawab dengan tabel dan grafik
2. **Visualisasi Interaktif** - AI menghasilkan chart (bar, line, pie, scatter, dll.) langsung di chat
3. **Pembuatan Laporan** - Generate laporan terstruktur (BAB I s/d BAB V) dengan bantuan AI dan export ke PDF
4. **Multi-LLM** - Pilih AI provider sesuai kebutuhan: Cerebras, Groq, Gemini, atau Sumopod (custom)
5. **RAG (Knowledge Base)** - Upload dokumen referensi, AI gunakan sebagai konteks untuk laporan yang lebih kaya

## Key Features

| Feature | Description |
|---------|-------------|
| Chat AI | Percakapan dengan AI (streaming real-time) |
| File Upload | Upload Excel (.xlsx) dan CSV untuk analisis |
| Table Response | AI merespons dengan tabel data interaktif |
| Chart Response | AI merespons dengan grafik (bar, line, pie, dll.) |
| Multi-LLM | Switch antara Cerebras, Groq, Gemini, Sumopod |
| Report Generation | Laporan otomatis dengan struktur BAB |
| PDF Export | Export laporan ke PDF profesional |
| RAG/Knowledge Base | Enrichment dengan dokumen referensi |
| Dark Mode | Tema gelap untuk kenyamanan mata |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14+, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend API** | Next.js API Routes, Vercel AI SDK |
| **Data Processing** | Python FastAPI, pandas, openpyxl |
| **Database** | PostgreSQL 16 + pgvector |
| **AI/LLM** | Cerebras, Groq, Gemini, Sumopod |
| **RAG** | LangChain, pgvector, text embeddings |
| **File Storage** | MinIO (S3-compatible) |
| **Queue** | Redis + BullMQ |
| **PDF** | Puppeteer |
| **Deployment** | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Node.js 20+
- Bun 1.0+
- Python 3.11+
- Docker & Docker Compose
- API keys (Groq, Cerebras, atau Gemini - minimal satu)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/ureport-ai.git
cd ureport-ai

# 2. Install dependencies
bun install

# 3. Start infrastructure
docker compose up -d postgres redis minio

# 4. Setup environment
cp .env.example .env
# Edit .env dengan API keys kamu

# 5. Setup database
bunx prisma generate
bunx prisma migrate dev

# 6. Start development
bun run dev                    # Terminal 1: Next.js
cd services/python && uvicorn main:app --reload  # Terminal 2: Python
```

### Access

- **App:** http://localhost:3000
- **Python API Docs:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001

## Documentation

Dokumentasi lengkap tersedia di folder `/docs`:

| Document | Content |
|----------|---------|
| [BLUEPRINT.md](./docs/BLUEPRINT.md) | Masterplan project, fitur, timeline, dan user flow |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Arsitektur teknis, diagram, dan design patterns |
| [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) | Database design, ER diagram, dan tabel |
| [TECHSTACK.md](./docs/TECHSTACK.md) | Penjelasan setiap teknologi dan learning resources |
| [SKILLS_REQUIRED.md](./docs/SKILLS_REQUIRED.md) | Skills yang dibutuhkan dan path belajar |
| [API_DESIGN.md](./docs/API_DESIGN.md) | Spesifikasi semua API endpoints |
| [DEVELOPMENT_GUIDE.md](./docs/DEVELOPMENT_GUIDE.md) | Panduan setup dan development |
| [MEMORY.md](./docs/MEMORY.md) | Keputusan arsitektur (ADR) dan catatan project |

### 📘 Alternative Blueprint (v2)

Tersedia juga blueprint **alternatif** dengan stack yang lebih AI-native (FastAPI + Qdrant + Plotly + WeasyPrint + LiteLLM + LangGraph) di folder [`docs/v2/`](./docs/v2/). Lihat [`docs/v2/README.md`](./docs/v2/README.md) untuk perbandingan & cara memilih antara blueprint awal vs v2.

## Project Structure

```
ureport-ai/
├── src/                    # Next.js application
│   ├── app/               # Pages & API routes
│   ├── components/        # UI components
│   ├── lib/               # Utilities & integrations
│   ├── hooks/             # Custom React hooks
│   ├── store/             # State management (Zustand)
│   └── types/             # TypeScript types
├── services/
│   └── python/            # FastAPI data processing service
├── prisma/                # Database schema & migrations
├── docs/                  # Project documentation
├── docker/                # Docker configurations
└── workers/               # Background job workers
```

## Development Phases

- **Phase 1:** MVP - Chat + File Upload + Basic Analysis
- **Phase 2:** Charts/Tables + Multi-LLM Support
- **Phase 3:** RAG + Report Generation + PDF Export
- **Phase 4:** Polish + Optimization + Deployment

Detail lengkap ada di [BLUEPRINT.md](./docs/BLUEPRINT.md).

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
