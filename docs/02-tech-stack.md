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

---

## 2.6 Pendalaman Per-Teknologi

Bagian ini memberikan penjelasan mendalam untuk setiap teknologi utama: apa itu, kenapa dipilih untuk uReport AI, konsep kunci, dan sumber belajar.

---

### 2.6.1 Next.js 15 (App Router)

**Apa itu:** Framework React full-stack dari Vercel. Versi 15 memperkenalkan App Router sebagai default, React Server Components (RSC), dan streaming response bawaan.

**Kenapa dipilih untuk uReport AI:**
- App Router mendukung streaming natively, krusial untuk menampilkan token AI secara real-time.
- RSC mengurangi JavaScript bundle di browser, mempercepat load halaman dashboard/laporan.
- Integrasi mulus dengan Vercel AI SDK untuk chat streaming.
- Ekosistem middleware, layout nesting, dan parallel routes mempermudah UI kompleks.

**Konsep kunci:**
- Server Components vs Client Components (kapan pakai `"use client"`)
- Streaming dan Suspense boundaries
- Route Groups dan parallel routes
- Server Actions untuk mutasi sederhana
- Metadata API dan SEO

**Sumber belajar:**
1. [Next.js Documentation - App Router](https://nextjs.org/docs/app)
2. [React Server Components - Vercel Blog](https://vercel.com/blog/understanding-react-server-components)
3. [Next.js Learn Course](https://nextjs.org/learn)
4. [Lee Robinson - Next.js App Router Explained (YouTube)](https://www.youtube.com/watch?v=DrxiNfbr63s)

---

### 2.6.2 React 19

**Apa itu:** Library UI deklaratif dari Meta. Versi 19 menambahkan fitur transitions, improved Suspense, use() hook, dan form actions.

**Kenapa dipilih untuk uReport AI:**
- Transitions memungkinkan UI tetap responsif saat AI sedang memproses.
- Suspense yang lebih matang untuk loading state chart dan data.
- use() hook menyederhanakan fetching di komponen.
- Ekosistem terbesar: banyak library siap pakai (chat UI, chart, file upload).

**Konsep kunci:**
- Hooks (useState, useEffect, useCallback, useMemo, useRef)
- Suspense dan lazy loading
- Transitions (useTransition, startTransition)
- Context API untuk state ringan
- Concurrent rendering

**Sumber belajar:**
1. [React Documentation](https://react.dev/)
2. [React 19 Blog Post](https://react.dev/blog/2024/12/05/react-19)
3. [Overreacted (Dan Abramov's Blog)](https://overreacted.io/)
4. [Epic React by Kent C. Dodds](https://epicreact.dev/)

---

### 2.6.3 TailwindCSS + shadcn/ui

**Apa itu:** TailwindCSS adalah utility-first CSS framework. shadcn/ui adalah koleksi komponen React yang bisa di-copy langsung ke project (bukan npm dependency).

**Kenapa dipilih untuk uReport AI:**
- Utility-first mempercepat styling tanpa context-switch ke file CSS terpisah.
- shadcn/ui memberikan komponen berkualitas produksi (Dialog, Sheet, Command palette) yang bisa dikustomisasi sepenuhnya.
- Tidak ada vendor lock-in: kode komponen ada di project kita.
- Desain konsisten mirip Linear/Vercel tanpa effort desain dari nol.

**Konsep kunci:**
- Utility classes dan responsive design (sm:, md:, lg:)
- CSS variables untuk theming (dark mode)
- Radix UI primitives (accessibility bawaan)
- Class Variance Authority (CVA) untuk variants

**Sumber belajar:**
1. [TailwindCSS Documentation](https://tailwindcss.com/docs)
2. [shadcn/ui Documentation](https://ui.shadcn.com/)
3. [Radix UI Primitives](https://www.radix-ui.com/)
4. [Tailwind Labs YouTube Channel](https://www.youtube.com/@TailwindLabs)

---

### 2.6.4 Vercel AI SDK

**Apa itu:** SDK TypeScript dari Vercel untuk membangun aplikasi AI. Menyediakan hooks (`useChat`, `useCompletion`) dan adapters untuk streaming dari berbagai backend.

**Kenapa dipilih untuk uReport AI:**
- `useChat` hook menangani streaming, retry, dan state management secara otomatis.
- Support tool-calling dan structured output.
- Backend-agnostic: bisa connect ke FastAPI endpoint kita via custom transport.
- Menangani edge cases (abort, reconnect, token counting).

**Konsep kunci:**
- useChat hook dan message protocol
- Streaming protocol (text, tool-call, tool-result)
- Custom providers dan transport layer
- AI State dan UI State

**Sumber belajar:**
1. [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
2. [AI SDK Examples Repository](https://github.com/vercel/ai/tree/main/examples)
3. [Vercel AI SDK 4.0 Announcement](https://vercel.com/blog/ai-sdk-4)

---

### 2.6.5 Plotly.js

**Apa itu:** Library charting interaktif open-source. Mendukung 40+ tipe chart dengan zoom, hover, export, dan animasi.

**Kenapa dipilih untuk uReport AI:**
- Interaktivitas tinggi: zoom, pan, hover tooltips - cocok untuk explorasi data.
- Python Plotly dan JS Plotly share format JSON yang sama - backend generate, frontend render.
- Export ke PNG/SVG untuk embed di laporan PDF.
- Tipe chart lengkap termasuk heatmap, 3D, dan statistical charts.

**Konsep kunci:**
- Traces dan layout (data + style terpisah)
- Figure JSON schema (portable antara Python dan JS)
- React wrapper (`react-plotly.js`)
- Responsive dan config options

**Sumber belajar:**
1. [Plotly.js Documentation](https://plotly.com/javascript/)
2. [react-plotly.js GitHub](https://github.com/plotly/react-plotly.js)
3. [Plotly Python (backend side)](https://plotly.com/python/)
4. [Plotly Community Forum](https://community.plotly.com/)

---

### 2.6.6 Python 3.12 + FastAPI

**Apa itu:** Python adalah bahasa pemrograman #1 untuk AI/ML/Data. FastAPI adalah web framework async modern dengan auto-dokumentasi OpenAPI.

**Kenapa dipilih untuk uReport AI:**
- Python memiliki ekosistem AI/data terlengkap (pandas, numpy, langchain, llamaindex).
- FastAPI: performa tinggi (async/await native), type-safe (Pydantic), auto-generate API docs.
- Semua LLM SDK tersedia di Python first.
- Python 3.12: performa lebih baik, improved error messages, type parameter syntax baru.

**Konsep kunci:**
- Async/await dan event loop
- Dependency injection di FastAPI
- Path operations, request/response models
- Middleware dan exception handlers
- Background tasks

**Sumber belajar:**
1. [FastAPI Documentation](https://fastapi.tiangolo.com/)
2. [Python 3.12 What's New](https://docs.python.org/3/whatsnew/3.12.html)
3. [FastAPI Full Course - freeCodeCamp (YouTube)](https://www.youtube.com/watch?v=7t2alSnE2-I)
4. [Real Python - FastAPI Guide](https://realpython.com/fastapi-python-web-apis/)

---

### 2.6.7 Pydantic v2

**Apa itu:** Library validasi data dan settings management untuk Python. Versi 2 ditulis ulang di Rust (pydantic-core) untuk performa 5-50x lebih cepat.

**Kenapa dipilih untuk uReport AI:**
- Validasi request/response otomatis di FastAPI.
- Schema generation untuk OpenAPI docs.
- Settings management dengan .env file support.
- Serialization/deserialization cepat untuk high-throughput API.

**Konsep kunci:**
- BaseModel dan Field validators
- model_validator (before/after)
- Computed fields
- Settings dengan env var binding
- JSON Schema generation

**Sumber belajar:**
1. [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
2. [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
3. [ArjanCodes - Pydantic v2 (YouTube)](https://www.youtube.com/watch?v=502XOB0u8OY)

---

### 2.6.8 SQLAlchemy 2.0 + Alembic

**Apa itu:** SQLAlchemy adalah ORM Python paling mature. Alembic adalah migration tool resminya. Versi 2.0 memperkenalkan style baru yang lebih type-safe.

**Kenapa dipilih untuk uReport AI:**
- ORM paling fleksibel di Python: bisa raw SQL, Core, atau ORM style.
- Async support native (asyncpg driver).
- Alembic: auto-generate migration dari model diff.
- Mature dan battle-tested di production besar.

**Konsep kunci:**
- Declarative mapping (Mapped, mapped_column)
- Async session dan unit of work pattern
- Relationships dan lazy/eager loading
- Alembic revision dan autogenerate
- Connection pooling

**Sumber belajar:**
1. [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
2. [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
3. [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
4. [Talk Python - SQLAlchemy Course](https://training.talkpython.fm/courses/sqlalchemy-for-enterprise-applications)

---

### 2.6.9 LiteLLM

**Apa itu:** Unified SDK untuk memanggil 100+ LLM provider dengan satu interface. Satu baris kode, ganti model tanpa ganti kode.

**Kenapa dipilih untuk uReport AI:**
- Support Cerebras, Groq, Gemini, dan OpenAI-compatible (Sumopod) dalam 1 SDK.
- Fallback otomatis antar provider.
- Cost tracking dan rate limiting bawaan.
- Proxy server mode untuk centralized gateway.

**Konsep kunci:**
- completion() dan acompletion() interface
- Model naming convention (provider/model)
- Fallback dan routing strategies
- Budget dan rate limit config
- Streaming responses

**Sumber belajar:**
1. [LiteLLM Documentation](https://docs.litellm.ai/)
2. [LiteLLM GitHub Repository](https://github.com/BerriAI/litellm)
3. [LiteLLM Proxy Server Guide](https://docs.litellm.ai/docs/simple_proxy)

---

### 2.6.10 LangGraph

**Apa itu:** Framework dari LangChain untuk membangun agent sebagai state machine (graph). Lebih predictable dan debuggable dibanding chain-based approach.

**Kenapa dipilih untuk uReport AI:**
- Agent uReport butuh branching logic (data analyst vs report writer vs chat).
- State machine memudahkan retry, checkpoint, dan human-in-the-loop.
- Visualisasi graph membantu debugging agent flow.
- Tool-calling terintegrasi dengan state management.

**Konsep kunci:**
- StateGraph dan nodes
- Edges (conditional routing)
- Checkpointing dan persistence
- Tool nodes dan tool-calling
- Human-in-the-loop interrupts

**Sumber belajar:**
1. [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
2. [LangGraph Tutorial - Build an Agent](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
3. [LangGraph Examples Repository](https://github.com/langchain-ai/langgraph/tree/main/examples)
4. [LangChain YouTube - LangGraph Deep Dive](https://www.youtube.com/watch?v=9BPCV5TYPmg)

---

### 2.6.11 LlamaIndex

**Apa itu:** Framework khusus RAG (Retrieval-Augmented Generation). Menyediakan pipeline lengkap: document loading, chunking, indexing, retrieval, dan synthesis.

**Kenapa dipilih untuk uReport AI:**
- Spesialisasi RAG lebih matang dibanding LangChain untuk use case ini.
- Banyak document readers bawaan (PDF, DOCX, Excel, TXT).
- Abstraksi clean: VectorStoreIndex, Retriever, ResponseSynthesizer.
- Support hybrid search (dense + sparse) out of the box.

**Konsep kunci:**
- Documents dan Nodes (chunking)
- Index types (VectorStore, Summary, Keyword)
- Retriever dan query engines
- Response synthesizers
- Ingestion pipeline dan transformations

**Sumber belajar:**
1. [LlamaIndex Documentation](https://docs.llamaindex.ai/)
2. [LlamaIndex Starter Tutorial](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/)
3. [LlamaIndex GitHub](https://github.com/run-llama/llama_index)
4. [Jerry Liu - RAG Best Practices (YouTube)](https://www.youtube.com/watch?v=TRjq7t2Ms5I)

---

### 2.6.12 Qdrant

**Apa itu:** Vector database open-source yang didesain untuk similarity search. Mendukung filtering, hybrid search, dan multi-tenancy.

**Kenapa dipilih untuk uReport AI:**
- Performa tinggi untuk similarity search di skala besar.
- Self-host mudah (1 Docker container).
- Support payload filtering (filter by user_id, file_type, dll.).
- Hybrid search: combine dense vectors + sparse (BM25).
- Collection-based multi-tenancy cocok untuk isolasi per-user.

**Konsep kunci:**
- Collections dan points
- Dense vs sparse vectors
- Payload filtering dan indexing
- HNSW index parameters
- Snapshot dan backup

**Sumber belajar:**
1. [Qdrant Documentation](https://qdrant.tech/documentation/)
2. [Qdrant Tutorial - Getting Started](https://qdrant.tech/documentation/quick-start/)
3. [Qdrant GitHub](https://github.com/qdrant/qdrant)
4. [Qdrant Blog - Vector Search Explained](https://qdrant.tech/articles/)

---

### 2.6.13 bge-m3 Embeddings

**Apa itu:** Model embedding multilingual dari BAAI (Beijing Academy of AI). Mendukung dense, sparse (lexical), dan multi-vector retrieval dalam satu model.

**Kenapa dipilih untuk uReport AI:**
- Multilingual: performa bagus untuk Bahasa Indonesia dan Inggris.
- Bisa jalan lokal dengan sentence-transformers (hemat biaya).
- Output dense + sparse sekaligus, ideal untuk hybrid search di Qdrant.
- Dimensi 1024, ukuran model reasonable (~600MB).

**Konsep kunci:**
- Dense embeddings vs sparse embeddings
- Sentence-transformers library
- Batch encoding untuk efisiensi
- Normalization dan similarity metrics (cosine, dot product)
- Model quantization untuk deployment ringan

**Sumber belajar:**
1. [bge-m3 on HuggingFace](https://huggingface.co/BAAI/bge-m3)
2. [FlagEmbedding GitHub](https://github.com/FlagOpen/FlagEmbedding)
3. [Sentence-Transformers Documentation](https://www.sbert.net/)
4. [MTEB Leaderboard (benchmark)](https://huggingface.co/spaces/mteb/leaderboard)

---

### 2.6.14 pandas + numpy

**Apa itu:** pandas adalah library data manipulation tabular. numpy adalah library komputasi numerik. Keduanya adalah fondasi data science di Python.

**Kenapa dipilih untuk uReport AI:**
- pandas: read Excel/CSV, filter, aggregate, pivot -- semua yang Data Analyst mode butuhkan.
- numpy: operasi statistik cepat (mean, std, korelasi).
- Integrasi native dengan Plotly untuk visualisasi.
- AI (LLM) sangat familiar generate kode pandas -- training data berlimpah.

**Konsep kunci:**
- DataFrame dan Series
- GroupBy, merge, pivot_table
- Handling missing data (NaN)
- Vectorized operations (hindari loop)
- Memory management untuk dataset besar

**Sumber belajar:**
1. [pandas Documentation](https://pandas.pydata.org/docs/)
2. [numpy Documentation](https://numpy.org/doc/)
3. [Python for Data Analysis (Wes McKinney)](https://wesmckinney.com/book/)
4. [Kaggle Learn - Pandas](https://www.kaggle.com/learn/pandas)
5. [Real Python - pandas Tutorial](https://realpython.com/pandas-python-explore-dataset/)

---

### 2.6.15 E2B / nsjail (Code Sandbox)

**Apa itu:** E2B adalah managed sandbox service untuk eksekusi kode aman. nsjail adalah Linux namespace sandbox untuk isolasi proses. Keduanya mencegah kode berbahaya merusak sistem.

**Kenapa dipilih untuk uReport AI:**
- AI-generated code HARUS dijalankan di environment terisolasi (security requirement).
- E2B: mudah dipakai (API call), tapi berbayar. Cocok untuk MVP.
- nsjail: gratis, kontrol penuh, tapi setup lebih kompleks. Cocok untuk produksi.
- Strategi: MVP pakai E2B, migrasi ke self-hosted nsjail saat scale.

**Konsep kunci:**
- Container isolation vs namespace isolation
- Resource limits (CPU, memory, time)
- Filesystem restrictions (read-only root)
- Network isolation
- Artifact extraction (output files, plots)

**Sumber belajar:**
1. [E2B Documentation](https://e2b.dev/docs)
2. [E2B Code Interpreter SDK](https://github.com/e2b-dev/code-interpreter)
3. [nsjail GitHub](https://github.com/google/nsjail)
4. [Linux Namespaces Explained](https://man7.org/linux/man-pages/man7/namespaces.7.html)

---

### 2.6.16 Jinja2 + WeasyPrint

**Apa itu:** Jinja2 adalah template engine Python (HTML templating). WeasyPrint mengkonversi HTML+CSS ke PDF dengan dukungan paged media (page breaks, headers, footers).

**Kenapa dipilih untuk uReport AI:**
- HTML/CSS adalah format yang AI paling jago generate.
- Jinja2: template inheritance, loop, conditional -- cocok untuk struktur BAB laporan.
- WeasyPrint: CSS Paged Media support (page-break, @page, running headers).
- Hasil PDF profesional tanpa perlu low-level PDF manipulation.

**Konsep kunci:**
- Jinja2 template syntax ({{ }}, {% %}, filters)
- Template inheritance (base layout + child blocks)
- CSS Paged Media (@page, page-break-before)
- WeasyPrint fonts dan asset embedding
- PDF metadata (title, author)

**Sumber belajar:**
1. [Jinja2 Documentation](https://jinja.palletsprojects.com/)
2. [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
3. [CSS Paged Media Specification](https://www.w3.org/TR/css-page-3/)
4. [WeasyPrint Samples](https://github.com/nicholasgasior/report-templates-weasyprint)

---

### 2.6.17 PostgreSQL 16

**Apa itu:** Relational database open-source paling advanced. Versi 16 menambahkan logical replication improvement, better parallelism, dan pg_stat_io.

**Kenapa dipilih untuk uReport AI:**
- JSONB untuk menyimpan structured output (tool results, chart configs) secara fleksibel.
- pgvector extension tersedia jika ingin simplifikasi infra (vector search tanpa Qdrant terpisah).
- Full-text search bawaan (tsvector) untuk pencarian dokumen sederhana.
- Battle-tested, komunitas besar, tooling lengkap.

**Konsep kunci:**
- JSONB operations dan indexing (GIN)
- Connection pooling (PgBouncer)
- Indexing strategies (B-tree, GIN, GiST)
- EXPLAIN ANALYZE untuk query optimization
- Partitioning untuk tabel besar

**Sumber belajar:**
1. [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
2. [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
3. [Use The Index, Luke](https://use-the-index-luke.com/)
4. [pgvector Extension](https://github.com/pgvector/pgvector)

---

### 2.6.18 Redis 7

**Apa itu:** In-memory data store yang bisa dipakai sebagai cache, message broker, dan session store. Versi 7 menambahkan Redis Functions dan improved ACL.

**Kenapa dipilih untuk uReport AI:**
- Cache: LLM response caching, session data, rate limit counters.
- Broker: Celery membutuhkan message broker -- Redis paling simple.
- Pub/Sub: notifikasi real-time (report selesai, file processed).
- Satu service untuk 3 kebutuhan, mengurangi kompleksitas infra.

**Konsep kunci:**
- Data structures (strings, hashes, lists, sets, sorted sets)
- TTL dan eviction policies
- Pub/Sub dan Streams
- Persistence (RDB vs AOF)
- Cluster dan Sentinel (HA)

**Sumber belajar:**
1. [Redis Documentation](https://redis.io/docs/)
2. [Redis University (free courses)](https://university.redis.io/)
3. [Redis Best Practices](https://redis.io/docs/management/optimization/)

---

### 2.6.19 Celery 5

**Apa itu:** Distributed task queue untuk Python. Menjalankan background jobs (report generation, file processing) secara async dengan retry dan scheduling.

**Kenapa dipilih untuk uReport AI:**
- Report generation bisa 30-120 detik -- tidak boleh blocking API request.
- Retry logic bawaan untuk job yang gagal.
- Task routing: bisa assign job berat ke worker khusus.
- Monitoring via Flower (web UI) atau Prometheus exporter.

**Konsep kunci:**
- Tasks dan task signatures
- Worker dan concurrency (prefork, eventlet, gevent)
- Result backends
- Task routing dan priority queues
- Periodic tasks (celery beat)

**Sumber belajar:**
1. [Celery Documentation](https://docs.celeryq.dev/en/stable/)
2. [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
3. [Real Python - Celery Guide](https://realpython.com/asynchronous-tasks-with-django-and-celery/)
4. [Flower - Celery Monitoring](https://flower.readthedocs.io/)

---

### 2.6.20 Docker + Docker Compose

**Apa itu:** Docker mengemas aplikasi dalam container yang reproducible. Docker Compose mengorkestrasi multi-container untuk development dan deployment.

**Kenapa dipilih untuk uReport AI:**
- Reproducible environment: semua developer pakai stack yang sama.
- Multi-service orchestration: web + api + postgres + redis + qdrant dalam 1 command.
- Production-ready: deploy ke VPS dengan docker compose atau migrate ke K8s.
- Isolasi service: setiap komponen punya resource limits sendiri.

**Konsep kunci:**
- Dockerfile best practices (multi-stage builds, layer caching)
- Docker Compose services, networks, volumes
- Health checks dan depends_on
- Environment variables dan secrets
- Volume mounts untuk development (hot reload)

**Sumber belajar:**
1. [Docker Documentation](https://docs.docker.com/)
2. [Docker Compose Documentation](https://docs.docker.com/compose/)
3. [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
4. [Play with Docker (interactive lab)](https://labs.play-with-docker.com/)

---

### 2.6.21 Auth.js (NextAuth v5)

**Apa itu:** Library autentikasi untuk Next.js. Versi 5 (Auth.js) mendukung Edge Runtime, berbagai OAuth providers, dan session management via JWT atau database.

**Kenapa dipilih untuk uReport AI:**
- Integrasi terbaik dengan Next.js App Router.
- Support email + password dan Google OAuth out of the box.
- Session JWT bisa diverifikasi oleh FastAPI backend tanpa round-trip ke auth server.
- Middleware-based protection untuk route groups.

**Konsep kunci:**
- Providers (credentials, OAuth)
- Session strategies (JWT vs database)
- Callbacks (jwt, session, signIn)
- Middleware untuk route protection
- CSRF protection

**Sumber belajar:**
1. [Auth.js Documentation](https://authjs.dev/)
2. [NextAuth.js v5 Migration Guide](https://authjs.dev/getting-started/migrating-to-v5)
3. [Auth.js GitHub](https://github.com/nextauthjs/next-auth)
4. [Vercel - Authentication Patterns](https://nextjs.org/docs/app/building-your-application/authentication)
