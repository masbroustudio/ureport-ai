# uReport AI - Complete Tech Stack Breakdown

## Overview

Dokumen ini menjelaskan secara detail setiap teknologi yang digunakan dalam uReport AI, alasan pemilihan, alternatif yang dipertimbangkan, dan resource untuk mempelajari masing-masing teknologi.

---

## Frontend Technologies

### 1. Next.js 14/15 (React Framework)

**Apa itu:** Framework React full-stack yang menyediakan server-side rendering (SSR), static site generation (SSG), API routes, dan file-based routing.

**Mengapa dipilih:**
- App Router dengan React Server Components untuk performa optimal
- Built-in API Routes sehingga tidak perlu backend terpisah untuk most logic
- Streaming support yang native (penting untuk LLM streaming responses)
- Edge Runtime untuk low-latency API calls
- Excellent developer experience dan ekosistem terbesar

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Remix | Ekosistem lebih kecil, kurang resources untuk belajar |
| Nuxt.js (Vue) | Vue ecosystem lebih kecil untuk AI/data tooling |
| SvelteKit | Ekosistem masih berkembang, kurang library AI |

**Learning Resources:**
- [Next.js Official Docs](https://nextjs.org/docs) - Dokumentasi resmi (wajib baca)
- [Next.js App Router Tutorial](https://nextjs.org/learn) - Tutorial interaktif
- [Vercel YouTube Channel](https://youtube.com/@vercel) - Video tutorial
- [Next.js GitHub Examples](https://github.com/vercel/next.js/tree/canary/examples) - Contoh project

---

### 2. TypeScript

**Apa itu:** Superset JavaScript yang menambahkan static typing. Kode TypeScript di-compile menjadi JavaScript.

**Mengapa dipilih:**
- Type safety mencegah bugs sebelum runtime
- IntelliSense/autocomplete yang jauh lebih baik di IDE
- Refactoring jadi aman karena compiler akan menangkap error
- Standar industri untuk project medium-large
- Dokumentasi "hidup" melalui type definitions

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| JavaScript (plain) | Terlalu banyak runtime errors untuk project kompleks |
| Flow | Sudah kalah populer, ecosystem kurang |

**Learning Resources:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) - Official handbook
- [Total TypeScript by Matt Pocock](https://www.totaltypescript.com/) - Course advanced
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/) - Free ebook

---

### 3. Tailwind CSS

**Apa itu:** Utility-first CSS framework dimana kamu menulis class langsung di HTML/JSX, bukan menulis CSS terpisah.

**Mengapa dipilih:**
- Development sangat cepat (no context switching antara file CSS dan component)
- Consistent design system out of the box
- File CSS production sangat kecil (purging unused classes)
- Mudah membuat responsive design
- Kompatibilitas excellent dengan shadcn/ui

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| CSS Modules | Lebih lambat development, butuh naming |
| Styled Components | Runtime overhead, less performant |
| Vanilla CSS | Terlalu banyak boilerplate |

**Learning Resources:**
- [Tailwind CSS Docs](https://tailwindcss.com/docs) - Dokumentasi resmi
- [Tailwind UI](https://tailwindui.com/) - Component examples (berbayar)
- [Tailwind Play](https://play.tailwindcss.com/) - Online playground

---

### 4. shadcn/ui

**Apa itu:** Bukan library/dependency, melainkan koleksi reusable components yang kamu copy-paste ke project. Built on top of Radix UI primitives + Tailwind CSS.

**Mengapa dipilih:**
- Full kontrol atas kode (bukan black box)
- Accessible by default (WAI-ARIA compliant)
- Beautiful design out of the box
- Customizable tanpa fighting dengan library
- Tidak menambah bundle size sebagai dependency

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Material UI (MUI) | Terlalu opinionated, berat, susah customize |
| Chakra UI | Kurang modern dibanding shadcn |
| Ant Design | Terlalu enterprise, kurang flexible |

**Learning Resources:**
- [shadcn/ui Docs](https://ui.shadcn.com/) - Dokumentasi dan contoh
- [shadcn/ui GitHub](https://github.com/shadcn-ui/ui) - Source code

---

### 5. Recharts

**Apa itu:** Library charting untuk React yang declarative, composable, dan mudah digunakan. Built on D3.js.

**Mengapa dipilih:**
- React-native (bukan wrapper DOM manipulation)
- Declarative API yang mudah dipahami
- Responsif by default
- Banyak chart types: Bar, Line, Pie, Scatter, Area, Radar, etc.
- Mudah di-customize dan theme-able

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Chart.js | Bukan React-native, imperative API |
| Nivo | Lebih complex API, steeper learning curve |
| Victory | Kurang populer, less community support |
| D3.js (raw) | Terlalu low-level, overkill untuk kebutuhan ini |

**Learning Resources:**
- [Recharts Official Docs](https://recharts.org/) - Dokumentasi dan contoh
- [Recharts Examples](https://recharts.org/en-US/examples) - Gallery contoh

---

### 6. TanStack Table (React Table v8)

**Apa itu:** Headless table library yang menyediakan logic untuk sorting, filtering, pagination tanpa UI opinionated.

**Mengapa dipilih:**
- Headless: Full kontrol atas rendering
- Fitur lengkap: sort, filter, pagination, column resize, virtual scroll
- TypeScript-first
- Kombinasi sempurna dengan shadcn/ui table component

**Learning Resources:**
- [TanStack Table Docs](https://tanstack.com/table/latest) - Official docs
- [shadcn/ui Data Table](https://ui.shadcn.com/docs/components/data-table) - shadcn integration

---

### 7. react-markdown + react-syntax-highlighter

**Apa itu:** Library untuk render markdown content dan syntax highlighting code blocks di React.

**Mengapa dipilih:**
- AI responses sering dalam format markdown
- Support code blocks, tables, lists, headings
- XSS-safe rendering
- Customizable renderers (bisa override cara render table, code, etc.)

**Learning Resources:**
- [react-markdown GitHub](https://github.com/remarkjs/react-markdown) - Docs dan contoh
- [react-syntax-highlighter](https://github.com/react-syntax-highlighter/react-syntax-highlighter) - Code highlighting

---

### 8. Zustand (State Management)

**Apa itu:** Lightweight state management library untuk React. Minimalist, tanpa boilerplate.

**Mengapa dipilih:**
- Sangat simple dibanding Redux (no actions, reducers, middleware)
- Bundle size tiny (~1KB)
- TypeScript support excellent
- Tidak perlu Provider wrapping
- Cocok untuk state: active conversation, selected provider, UI state

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Redux Toolkit | Terlalu banyak boilerplate untuk project ini |
| Jotai | Atomic model kurang cocok untuk conversation state |
| Context API | Performance issues dengan frequent updates |

**Learning Resources:**
- [Zustand GitHub](https://github.com/pmndrs/zustand) - Docs dan contoh

---

## Backend Technologies

### 9. Next.js API Routes

**Apa itu:** Backend endpoints yang bisa dibuat langsung di dalam project Next.js menggunakan file-based routing.

**Mengapa dipilih:**
- Tidak perlu server terpisah
- Type sharing antara frontend dan backend
- Mudah deploy sebagai satu unit
- Support streaming responses (ReadableStream)
- Edge Runtime untuk low latency

**Learning Resources:**
- [Next.js Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers) - Official docs

---

### 10. Python FastAPI (Microservice)

**Apa itu:** Modern, fast Python web framework untuk building APIs. Sangat cocok untuk data science workload.

**Mengapa dipilih:**
- Python ecosystem terbaik untuk data processing (pandas, numpy, etc.)
- Async by default (excellent performance)
- Automatic API documentation (Swagger/OpenAPI)
- Type hints + Pydantic untuk data validation
- Sangat cepat (salah satu framework Python tercepat)

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Flask | Sync by default, kurang modern |
| Django | Terlalu berat untuk microservice |
| Express.js | Python ecosystem lebih kuat untuk data |

**Learning Resources:**
- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Excellent documentation
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) - Step-by-step tutorial

---

### 11. Prisma ORM

**Apa itu:** Next-generation ORM untuk Node.js dan TypeScript. Menyediakan type-safe database access.

**Mengapa dipilih:**
- Schema-first approach yang readable
- Auto-generated TypeScript types
- Migration system yang robust
- Excellent DX (Prisma Studio untuk GUI)
- Support PostgreSQL features (JSON, arrays, etc.)

**Learning Resources:**
- [Prisma Docs](https://www.prisma.io/docs) - Official documentation
- [Prisma Examples](https://github.com/prisma/prisma-examples) - Example projects

---

### 12. NextAuth.js (Authentication)

**Apa itu:** Authentication library untuk Next.js yang mendukung berbagai providers (credentials, OAuth, etc.).

**Mengapa dipilih:**
- Dibuat khusus untuk Next.js
- Session management built-in
- Support credentials (email/password) dan OAuth
- JWT dan database sessions
- Middleware protection untuk routes

**Learning Resources:**
- [NextAuth.js Docs](https://next-auth.js.org/) - Official documentation
- [Auth.js (v5)](https://authjs.dev/) - Next generation

---

## AI/ML Technologies

### 13. Vercel AI SDK

**Apa itu:** SDK dari Vercel untuk membangun AI-powered applications. Menyediakan unified interface untuk multiple LLM providers dan streaming built-in.

**Mengapa dipilih:**
- Unified API untuk semua LLM providers
- Streaming responses out of the box
- React hooks (useChat, useCompletion)
- Tool calling support
- Mudah switch antar provider

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| LangChain.js | Lebih complex, overkill untuk chat routing |
| Raw fetch | Terlalu banyak boilerplate per provider |

**Learning Resources:**
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) - Official documentation
- [AI SDK Examples](https://sdk.vercel.ai/docs/getting-started) - Getting started

---

### 14. Cerebras SDK

**Apa itu:** SDK untuk mengakses Cerebras inference engine yang menawarkan kecepatan inference sangat tinggi.

**Mengapa dipilih:**
- Inference speed tercepat di market
- Cocok untuk interactive chat yang butuh respons cepat
- Compatible dengan OpenAI API format

**Learning Resources:**
- [Cerebras API Docs](https://docs.cerebras.ai/) - Official documentation
- [Cerebras Cloud](https://cloud.cerebras.ai/) - Dashboard dan API keys

---

### 15. Groq SDK

**Apa itu:** SDK untuk mengakses Groq's LPU (Language Processing Unit) inference engine dengan latency sangat rendah.

**Mengapa dipilih:**
- Latency terendah untuk LLM inference
- Support model populer (LLaMA, Mixtral, etc.)
- Free tier yang generous untuk development
- OpenAI-compatible API

**Learning Resources:**
- [Groq Docs](https://console.groq.com/docs) - Official documentation
- [GroqCloud Console](https://console.groq.com/) - Dashboard

---

### 16. Google Generative AI (Gemini)

**Apa itu:** SDK untuk mengakses Google's Gemini model family yang multimodal (text, image, video, code).

**Mengapa dipilih:**
- Multimodal capabilities (bisa baca gambar/chart)
- Context window sangat besar (1M+ tokens)
- Free tier yang generous
- Strong reasoning capabilities

**Learning Resources:**
- [Google AI for Developers](https://ai.google.dev/) - Official docs
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs) - API reference

---

### 17. Sumopod (Custom Provider)

**Apa itu:** Custom/self-hosted LLM provider yang dikembangkan sendiri atau menggunakan infrastruktur sendiri.

**Mengapa dipilih:**
- Full control atas model dan data
- Tidak tergantung pada third-party service
- Bisa fine-tune untuk use case spesifik
- Data privacy (data tidak keluar ke third party)

**Implementation Notes:**
- Harus implement interface LLMProvider yang sama
- Kemungkinan menggunakan OpenAI-compatible API format
- Perlu dokumentasi endpoint dan authentication

---

### 18. LangChain (Python)

**Apa itu:** Framework untuk building LLM applications. Menyediakan tools untuk chaining, RAG, agents, dan document processing.

**Mengapa dipilih:**
- Best-in-class RAG pipeline implementation
- Document loaders untuk berbagai format
- Text splitters yang smart
- Vector store integrations
- Chain-of-thought dan agent capabilities

**Learning Resources:**
- [LangChain Python Docs](https://python.langchain.com/docs/get_started/introduction) - Official docs
- [LangChain GitHub](https://github.com/langchain-ai/langchain) - Source code dan examples

---

## Data Processing Technologies

### 19. pandas

**Apa itu:** Library Python paling populer untuk data manipulation dan analysis. "Swiss army knife" untuk data.

**Mengapa dipilih:**
- De facto standard untuk data analysis di Python
- DataFrame abstraction yang powerful
- Read/write Excel, CSV, JSON, SQL, dan banyak format lain
- GroupBy, pivot, merge, statistical functions
- Mudah generate chart data

**Learning Resources:**
- [pandas Official Docs](https://pandas.pydata.org/docs/) - Documentation
- [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) - Quick start
- [Python for Data Analysis (O'Reilly)](https://wesmckinney.com/book/) - Book by pandas creator

---

### 20. openpyxl

**Apa itu:** Library Python untuk read/write file Excel (.xlsx).

**Mengapa dipilih:**
- Full support untuk Excel format (.xlsx)
- Bisa baca sheets, formulas, charts di Excel
- Integrasi dengan pandas (pandas.read_excel menggunakan openpyxl)

**Learning Resources:**
- [openpyxl Docs](https://openpyxl.readthedocs.io/) - Official documentation

---

### 21. numpy

**Apa itu:** Library fundamental untuk numerical computing di Python.

**Mengapa dipilih:**
- Fondasi pandas dan semua library data science Python
- Fast numerical operations (C-level speed)
- Statistical functions (mean, median, std, correlation, etc.)

**Learning Resources:**
- [NumPy Docs](https://numpy.org/doc/) - Official documentation
- [NumPy Quickstart](https://numpy.org/doc/stable/user/quickstart.html) - Quick start

---

### 22. matplotlib / plotly

**Apa itu:** Libraries untuk data visualization di Python. matplotlib untuk static charts, plotly untuk interactive charts.

**Mengapa dipilih:**
- Server-side chart generation (untuk embed di PDF reports)
- matplotlib: standard, semua tutorial data science menggunakannya
- plotly: interactive, bisa export sebagai HTML/JSON

**Learning Resources:**
- [Matplotlib Docs](https://matplotlib.org/stable/contents.html) - Official docs
- [Plotly Python Docs](https://plotly.com/python/) - Interactive charts

---

## Database & Infrastructure

### 23. PostgreSQL 16

**Apa itu:** Database relasional open-source paling advanced. Support JSONB, full-text search, dan extensions.

**Mengapa dipilih:**
- Reliable dan battle-tested
- JSONB support untuk flexible data
- pgvector extension untuk vector search (RAG)
- Excellent performance dengan proper indexing
- Free dan open source

**Learning Resources:**
- [PostgreSQL Docs](https://www.postgresql.org/docs/16/) - Official docs
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/) - Beginner-friendly

---

### 24. pgvector

**Apa itu:** PostgreSQL extension yang menambahkan vector data type dan similarity search capabilities.

**Mengapa dipilih:**
- Tidak perlu service terpisah (dalam PostgreSQL yang sudah dipakai)
- Support cosine similarity, L2 distance, inner product
- Index types: IVFFlat, HNSW
- Cukup performant untuk < 10 juta vectors
- Operasional lebih simple (satu database untuk semua)

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| Pinecone | Biaya, vendor lock-in |
| Weaviate | Service tambahan untuk maintain |
| Qdrant | Overkill untuk skala awal |
| ChromaDB | Kurang mature untuk production |

**Learning Resources:**
- [pgvector GitHub](https://github.com/pgvector/pgvector) - Documentation
- [pgvector with Prisma](https://www.prisma.io/docs/orm/prisma-client/queries/full-text-search) - Integration guide

---

### 25. Redis

**Apa itu:** In-memory data structure store. Digunakan sebagai cache, message broker, dan job queue backend.

**Mengapa dipilih:**
- Sangat cepat (in-memory)
- Sebagai backend untuk BullMQ job queue
- Session caching
- Rate limiting counter
- Pub/Sub untuk real-time notifications

**Learning Resources:**
- [Redis Docs](https://redis.io/docs/) - Official documentation
- [Redis University](https://university.redis.com/) - Free courses

---

### 26. MinIO / S3

**Apa itu:** Object storage yang S3-compatible. MinIO bisa self-hosted, atau gunakan AWS S3/Cloudflare R2.

**Mengapa dipilih:**
- Menyimpan file uploads (Excel, CSV, PDF)
- S3-compatible API (standard industri)
- MinIO bisa di-self-host dengan Docker
- Scalable tanpa limit penyimpanan

**Learning Resources:**
- [MinIO Docs](https://min.io/docs/) - Official documentation
- [MinIO Quickstart](https://min.io/docs/minio/linux/index.html) - Getting started

---

### 27. BullMQ (Job Queue)

**Apa itu:** Queue system untuk Node.js yang menggunakan Redis sebagai backend. Untuk menjalankan background jobs.

**Mengapa dipilih:**
- Report generation butuh waktu lama - harus async
- Retry mechanism built-in
- Job priority dan scheduling
- Progress tracking
- Dashboard monitoring (Bull Board)

**Learning Resources:**
- [BullMQ Docs](https://docs.bullmq.io/) - Official documentation

---

### 28. Docker & Docker Compose

**Apa itu:** Platform containerization untuk package dan deploy aplikasi. Docker Compose untuk orchestrate multiple containers.

**Mengapa dipilih:**
- Consistent environment (dev = production)
- Easy deployment ke VPS manapun
- Isolasi service (Next.js, FastAPI, PostgreSQL, Redis, MinIO)
- Reproducible builds

**Learning Resources:**
- [Docker Docs](https://docs.docker.com/) - Official documentation
- [Docker Compose Docs](https://docs.docker.com/compose/) - Multi-container

---

## PDF Generation

### 29. Puppeteer

**Apa itu:** Library Node.js yang mengontrol headless Chrome/Chromium. Bisa digunakan untuk generate PDF dari HTML.

**Mengapa dipilih:**
- Render HTML to PDF dengan CSS penuh
- Charts bisa di-render sebagai gambar dalam PDF
- Full CSS support (flexbox, grid, @page rules)
- Consistent output across environments

**Alternatif yang dipertimbangkan:**
| Alternatif | Alasan Tidak Dipilih |
|-----------|---------------------|
| @react-pdf/renderer | Kurang flexible CSS, no chart rendering |
| wkhtmltopdf | Outdated rendering engine |
| jsPDF | Terlalu manual, kurang powerful |
| Prince XML | Mahal (commercial license) |

**Learning Resources:**
- [Puppeteer Docs](https://pptr.dev/) - Official documentation
- [Puppeteer PDF Generation](https://pptr.dev/guides/pdf-generation) - PDF guide

---

## Tech Stack Summary Table

| Layer | Technology | Version | Priority |
|-------|-----------|---------|----------|
| Frontend Framework | Next.js | 14/15 | Critical |
| Language | TypeScript | 5.x | Critical |
| CSS | Tailwind CSS | 3.x/4.x | Critical |
| UI Components | shadcn/ui | Latest | Critical |
| Charts | Recharts | 2.x | High |
| Tables | TanStack Table | 8.x | High |
| State Management | Zustand | 4.x | Medium |
| Markdown | react-markdown | 9.x | High |
| Backend Framework | Next.js API Routes | - | Critical |
| Data Service | Python FastAPI | 0.100+ | Critical |
| ORM | Prisma | 5.x | Critical |
| Auth | NextAuth.js | 4.x/5.x | Critical |
| AI SDK | Vercel AI SDK | 3.x | Critical |
| LLM - Cerebras | @cerebras/sdk | Latest | High |
| LLM - Groq | groq-sdk | Latest | High |
| LLM - Gemini | @google/generative-ai | Latest | High |
| LLM - Sumopod | Custom adapter | - | High |
| RAG Framework | LangChain (Python) | 0.1+ | High |
| Data Processing | pandas | 2.x | Critical |
| Excel Parser | openpyxl | 3.x | Critical |
| Database | PostgreSQL | 16 | Critical |
| Vector DB | pgvector | 0.5+ | High |
| Cache/Queue | Redis | 7.x | High |
| Job Queue | BullMQ | 5.x | Medium |
| File Storage | MinIO | Latest | High |
| PDF | Puppeteer | 21+ | Medium |
| Containerization | Docker | 24+ | Medium |

---

## Learning Path (Urutan Belajar yang Disarankan)

### Phase 1: Foundation (2-3 minggu)
1. TypeScript basics
2. React fundamentals
3. Next.js App Router
4. Tailwind CSS
5. shadcn/ui components

### Phase 2: Backend & Database (2-3 minggu)
1. PostgreSQL basics
2. Prisma ORM
3. Next.js API Routes
4. NextAuth.js authentication
5. REST API design patterns

### Phase 3: AI Integration (2-3 minggu)
1. Vercel AI SDK
2. Groq API (paling mudah untuk mulai)
3. Streaming responses (SSE)
4. Prompt engineering basics
5. Multi-provider pattern

### Phase 4: Data Processing (2-3 minggu)
1. Python basics (jika belum)
2. FastAPI fundamentals
3. pandas for data analysis
4. openpyxl for Excel
5. Chart data preparation

### Phase 5: Advanced Features (3-4 minggu)
1. RAG concepts & pgvector
2. LangChain for document processing
3. Recharts for visualization
4. BullMQ for background jobs
5. Puppeteer for PDF generation

### Phase 6: DevOps (1-2 minggu)
1. Docker basics
2. Docker Compose
3. Deployment strategies
4. CI/CD basics
