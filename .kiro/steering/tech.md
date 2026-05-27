---
inclusion: always
---

# Tech Stack — uReport AI

> **Catatan penting**: Tech stack di bawah ini berasal dari **blueprint v2** (`docs/v2/`).
> Blueprint awal di `docs/TECHSTACK.md` memilih stack yang berbeda (Next.js + Prisma + pgvector + Recharts + Puppeteer + BullMQ).
>
> Tunggu konfirmasi user sebelum mulai coding dengan stack manapun. Lihat `docs/v2/README.md` untuk perbandingan.

## Stack Resmi (Blueprint v2)

| Layer | Pilihan |
|---|---|
| Frontend | **Next.js 15 (App Router)**, React 19, TypeScript |
| UI | **TailwindCSS** + **shadcn/ui** (Radix primitives) |
| Streaming AI di FE | **Vercel AI SDK** v4 (`useChat`) |
| Charts | **Plotly.js** (`react-plotly.js`) — primary; Recharts untuk dashboard ringan |
| State | Zustand (client) + TanStack Query (server) |
| Markdown | `react-markdown` + `remark-gfm` + `rehype-katex` + `mermaid` |
| Backend | **Python 3.12** + **FastAPI** + **Pydantic v2** |
| LLM Gateway | **LiteLLM** (unified, support Cerebras/Groq/Gemini/Sumopod) |
| Agent Orchestration | **LangGraph** |
| RAG | **LlamaIndex** + **Qdrant** + reranker `bge-reranker-v2-m3` |
| Embeddings | `bge-m3` (default lokal) atau Gemini `text-embedding-004` |
| Data Engine | pandas + numpy + Plotly + sandbox (E2B managed di MVP) |
| Report Engine | Jinja2 → HTML → **WeasyPrint** (PDF) |
| Database | **PostgreSQL 16** (utama) |
| Cache & Queue | **Redis 7** |
| Background Jobs | **Celery 5** (broker = Redis) |
| Storage | S3-compatible (MinIO dev, **Cloudflare R2** prod) |
| Auth | **Auth.js (NextAuth v5)** — email + Google OAuth |
| Migrations | **Alembic** |
| Container | Docker + docker compose |
| Monorepo tooling | Workspace via pnpm (FE) + uv (BE), orkestrasi via `make` |
| CI/CD | GitHub Actions |
| Observability | OpenTelemetry + Loki + Prometheus + Grafana + Sentry |

## Konvensi Kode

### Python (Backend)
- Format: `ruff` + `ruff format` (replace black/isort/flake8)
- Type check: `mypy --strict` di module agent & llm
- Test: `pytest` + `pytest-asyncio` + `httpx`
- Naming: `snake_case` modules/functions, `PascalCase` classes
- Folder: `app/{router,service,model,schema,agent,llm,rag,data,report}`

### TypeScript (Frontend)
- Format: `prettier`
- Lint: `eslint` (next/core-web-vitals)
- Path alias: `@/*` → `apps/web/src/*`
- Komponen UI di `src/components/ui/` (shadcn) dan `src/components/<domain>/`
- Server actions hanya untuk write yang sederhana; sebagian besar via REST/SSE ke FastAPI

### Naming
- File komponen React: `PascalCase.tsx`
- File util/hook: `camelCase.ts`
- Endpoint API: `kebab-case`, plural noun (`/conversations`, `/files`)
- DB table: `snake_case` plural

## Aturan untuk Asisten/Kiro

1. **Selalu pakai stack di atas** kecuali user eksplisit minta lain.
2. **Streaming default** di tiap endpoint chat → SSE.
3. **Multi-provider via LiteLLM** — JANGAN hard-code 1 SDK provider.
4. **Tool-calling first**: agen pakai tool schema, bukan parsing teks bebas.
5. **Tidak commit secret** — semua via env var.
6. **Bahasa Indonesia** untuk dokumentasi & komentar yang user-facing; **Bahasa Inggris** untuk identifier kode (variable, function, comment teknis).
7. **Test untuk module kritikal**: agent loop, sandbox runner, rag retrieval, pdf renderer.
8. **PR singkat & fokus** — 1 PR = 1 fitur/fix.

## Penggunaan LLM untuk Tiap Task Type
(default routing, bisa di-override user)

| Task | Model default |
|---|---|
| Intent classifier | `groq/llama-3.1-8b-instant` |
| Default chat | `groq/llama-3.3-70b-versatile` |
| Code generation (data analyst) | `cerebras/llama-3.3-70b` |
| Long-context reasoning / planner laporan | `gemini/gemini-2.0-flash` |
| Report writer per section | `cerebras/llama-3.3-70b` |
| Editor/polish | `gemini/gemini-2.0-flash` |
| Embeddings (default) | local `bge-m3` |

Lihat `docs/05-llm-providers.md` untuk detail.
