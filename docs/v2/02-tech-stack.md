# 02 — Tech Stack

> Tujuan: pilih stack yang **modern, popular, well-documented, dan paling cocok untuk AI + data analytics**. Setiap pilihan disertai rasional & alternatif.

---

## 2.1 Ringkasan

| Layer | Pilihan Utama | Versi | Alternatif |
|---|---|---|---|
| Frontend Framework | **Next.js (App Router)** | 15.x | Remix, SvelteKit |
| UI Library | **React + TailwindCSS + shadcn/ui** | React 19 | Mantine, Chakra |
| Streaming AI di FE | **Vercel AI SDK** | 4.x | Custom SSE client |
| Charts | **Plotly.js** + **Recharts** | latest | Apache ECharts |
| Backend | **Python 3.11+ + FastAPI** | FastAPI 0.115+ | Node.js (NestJS), Go |
| LLM Orchestration | **LiteLLM** + **LangGraph** | latest | LangChain, raw SDK |
| RAG | **LlamaIndex** | latest | LangChain RAG |
| Vector DB | **Qdrant** | 1.12+ | Weaviate, pgvector, Chroma |
| Embeddings | **bge-m3** (lokal) atau **Gemini text-embedding** | — | OpenAI embeddings |
| Data Engine | **pandas + numpy + Plotly** | latest | Polars (untuk dataset besar) |
| Code Sandbox | **E2B Code Interpreter** atau **nsjail + Jupyter** | — | Pyodide (FE-side, terbatas) |
| Report Engine | **Jinja2 + WeasyPrint** | latest | ReportLab, Pandoc |
| Database | **PostgreSQL** | 16+ | MySQL, SQLite (dev) |
| Cache & Queue | **Redis** | 7.x | KeyDB |
| Background Jobs | **Celery** | 5.x | RQ, Arq |
| File Storage | **S3-compatible** (MinIO dev, R2/S3 prod) | — | Local FS (dev only) |
| Auth | **Auth.js (NextAuth v5)** | 5.x | Clerk, Supabase Auth |
| Container | **Docker + Docker Compose** | — | Podman |
| Reverse Proxy | **Nginx** atau **Caddy** | — | Traefik |
| Monitoring | **OpenTelemetry + Grafana + Loki** | — | Datadog, Sentry |
| CI/CD | **GitHub Actions** | — | GitLab CI |

---

## 2.2 Rasional Tiap Pilihan

### Frontend — Next.js 15 (App Router)
- **Kenapa**: ekosistem terbaik untuk AI chat (banyak boilerplate, Vercel AI SDK first-class), SSR/streaming kuat, deploy mudah.
- **Alternatif** SvelteKit menarik tapi ekosistem AI tooling masih kalah.

### UI — Tailwind + shadcn/ui
- **Kenapa**: shadcn/ui adalah **library copy-paste** (bukan dependency), sangat fleksibel & tidak vendor-lock, designer-friendly, modern look (mirip Linear/Vercel).
- Komponen yang akan banyak dipakai: `Dialog`, `Sheet`, `Tabs`, `ScrollArea`, `Tooltip`, `Command` (palette).

### Streaming AI — Vercel AI SDK
- **Kenapa**: hook `useChat` siap pakai, support tool-calling, streaming SSE/AsyncIterable. Backend kita di FastAPI tinggal expose endpoint kompatibel atau pakai custom transport.

### Charts — Plotly + Recharts
- **Plotly** untuk chart interaktif dengan banyak fitur (zoom, hover, export).
- **Recharts** untuk chart sederhana & lightweight di dashboard.
- Backend (Python) bisa generate Plotly JSON → FE render → konsisten.

### Backend — FastAPI (Python)
- **Kenapa**: Python adalah bahasa nomor 1 untuk AI/ML & data analysis. pandas, numpy, langchain, llamaindex semua native. FastAPI: cepat, async, auto-docs (OpenAPI).
- **Trade-off**: bukan bahasa tipikal untuk web kelas enterprise besar, tapi sangat cocok untuk AI-first product.

### LLM Orchestration — LiteLLM + LangGraph
- **LiteLLM**: 1 SDK, 100+ provider (Cerebras, Groq, Gemini, OpenAI-compat seperti Sumopod). Hemat kode & gampang ganti model.
- **LangGraph**: state-machine untuk agent yang reliable (retry, branching, human-in-the-loop). Lebih predictable dari plain LangChain.

### RAG — LlamaIndex
- **Kenapa**: LlamaIndex spesialisasi RAG (lebih matang dari LangChain di area ini), banyak readers (PDF, DOCX, Excel), abstraksi clean (Index, Retriever, Synthesizer).

### Vector DB — Qdrant
- **Kenapa**: open-source, performant, gampang di-self-host (Docker 1 baris), API clean, support hybrid search (BM25 + dense).
- **Alternatif** `pgvector` jika ingin minim infra (1 DB saja). Pilih Qdrant kalau dataset > 1jt vektor.

### Embeddings — bge-m3 (local) atau Gemini embeddings
- **bge-m3**: open-source, multilingual (termasuk Bahasa Indonesia), bisa run lokal dengan `sentence-transformers`. Hemat biaya.
- **Gemini text-embedding-004**: kualitas top, tapi ada biaya & latency network.
- Strategi: default lokal, override ke Gemini untuk user premium.

### Data Engine — pandas + Plotly + Code Sandbox
- **pandas**: standar data analysis Python.
- **Plotly**: native dengan pandas (`df.plot(backend='plotly')`).
- **Sandbox**: AI generate kode Python → eksekusi di environment terisolasi. Pilihan:
  - **E2B Code Interpreter** (managed, $$, sangat mudah)
  - **Self-hosted Jupyter kernel + nsjail/firejail/gVisor** (kontrol penuh, gratis, ribet awalnya)
  - MVP: pakai E2B; produksi nanti migrasi self-host kalau cost tinggi.

### Report Engine — Jinja2 + WeasyPrint
- **Kenapa**: HTML/CSS adalah bahasa layout yang AI paling jago. Jinja2 = templating standar Python. WeasyPrint convert HTML+CSS (termasuk page-break, header/footer) ke PDF rapi.
- **Alternatif** ReportLab lebih low-level (bagus untuk PDF kompleks pixel-perfect). Pandoc bagus jika sumber Markdown/LaTeX.

### Database — PostgreSQL 16
- **Kenapa**: standar industri, JSONB kuat (untuk simpan tool output), bisa pasang `pgvector` kalau mau gabung vector search ke 1 DB.

### Auth — Auth.js (NextAuth v5)
- **Kenapa**: integrasi Next.js terbaik, support email + OAuth (Google, GitHub), session JWT/database. Backend FastAPI tinggal verify JWT.

### Storage — S3-compatible
- **Dev**: MinIO (Docker) → kompatibel S3 API.
- **Prod**: AWS S3 / Cloudflare R2 (R2 lebih murah, tanpa egress fee).

### Background Jobs — Celery
- Report generation 10 halaman bisa makan 30–120 detik → harus async.
- Celery + Redis broker, task status tersimpan, bisa retry.

---

## 2.3 Struktur Monorepo (Direkomendasikan)

```
ureport-ai/
├── apps/
│   ├── web/                # Next.js frontend
│   └── api/                # FastAPI backend
├── packages/
│   ├── shared-types/       # TypeScript types (auto-gen dari OpenAPI)
│   └── prompts/            # Prompt library (markdown)
├── infra/
│   ├── docker/             # Dockerfile per service
│   ├── compose/            # docker-compose.dev.yml, prod.yml
│   └── k8s/                # (V2) manifest k8s
├── docs/                   # Dokumentasi ini
├── scripts/                # Utility scripts (seed, migrate)
├── .kiro/                  # Steering & config Kiro
├── MASTERPLAN.md
└── README.md
```

**Tooling monorepo**: gunakan **Turborepo** atau cukup `make` + `docker compose`. Untuk MVP: cukup folder structure + `make` saja.

---

## 2.4 Estimasi Biaya Bulanan (MVP, ~100 active users)

| Item | Estimasi |
|---|---|
| VPS 4vCPU/8GB (backend + DB + Qdrant + Redis) | $20–40 |
| Vercel free tier (frontend) | $0 |
| Object storage R2 (50GB) | $0.75 |
| LLM cost (mix Groq/Gemini Flash) | $20–60 |
| E2B sandbox (jika dipakai) | $20–50 |
| Domain + email | $5 |
| **Total** | **~$70–160 / bulan** |

> Bisa lebih murah jika self-host sandbox & pakai Gemini Flash gratis tier.

---

## 2.5 Hal yang TIDAK Dipakai (dan Alasannya)

| Tidak dipakai | Alasan |
|---|---|
| MongoDB | Schema-driven app ini cocok PostgreSQL; JSONB cukup untuk fleksibilitas |
| LangChain murni | LangGraph + LiteLLM lebih ringkas & predictable |
| OpenAI eksklusif | Tujuan kita multi-provider, OpenAI tidak ada di list user |
| Streamlit/Gradio | Bagus untuk prototype, tidak cukup untuk produk konsumen |
| ElasticSearch | Overkill untuk MVP; Qdrant + Postgres FTS sudah cukup |
