# uReport AI - Project Memory (Architecture Decision Records)

## Overview

Dokumen ini berisi catatan keputusan arsitektur (ADR - Architecture Decision Records), notes integrasi provider, dan tracking penting lainnya. Dokumen ini akan terus di-update seiring pengembangan project.

---

## Architecture Decision Records (ADR)

### ADR-001: Next.js sebagai Frontend Framework

**Status:** Accepted
**Date:** 2025-01-01
**Context:** Perlu memilih framework frontend yang mendukung SSR, streaming, dan memiliki ekosistem AI yang baik.

**Decision:** Menggunakan Next.js 14+ dengan App Router.

**Rationale:**
1. App Router mendukung React Server Components untuk performa optimal
2. Streaming (Suspense boundaries) native - penting untuk LLM streaming responses
3. Vercel AI SDK terintegrasi sempurna dengan Next.js
4. API Routes menghilangkan kebutuhan backend terpisah untuk banyak logic
5. Ekosistem terbesar (shadcn/ui, next-auth, dll. semua dirancang untuk Next.js)
6. Deployment ke Vercel sangat mudah (zero-config)
7. Edge Runtime support untuk low-latency API calls

**Consequences:**
- Developer harus memahami perbedaan Server vs Client Components
- Butuh pemahaman tentang streaming dan Suspense
- Lock-in ke React ecosystem (bukan masalah karena React dominan)

**Alternatives Rejected:**
- Remix: Ekosistem lebih kecil, kurang tooling AI
- SvelteKit: Ekosistem data visualization lebih terbatas
- Angular: Terlalu verbose, tidak cocok untuk rapid development

---

### ADR-002: Python Microservice untuk Data Processing

**Status:** Accepted
**Date:** 2025-01-01
**Context:** Perlu memproses file Excel/CSV, melakukan analisis statistik, dan generate chart data. Perlu memilih bahasa/framework yang paling cocok.

**Decision:** Menggunakan Python FastAPI sebagai microservice terpisah yang berkomunikasi via REST API dengan Next.js.

**Rationale:**
1. Python memiliki ekosistem data science terbaik (pandas, numpy, scipy, etc.)
2. pandas adalah standar industri untuk data manipulation
3. openpyxl adalah library terlengkap untuk parsing Excel
4. LangChain Python lebih mature dibanding JavaScript version (untuk RAG)
5. FastAPI menyediakan async support dan auto-docs
6. Memisahkan concern: Next.js handle UI/auth, Python handle data

**Consequences:**
- Butuh manage dua codebase (TypeScript + Python)
- Perlu containerization (Docker) untuk deployment yang konsisten
- Network overhead antara services (mitigated dengan caching)
- Developer perlu bisa Python dan TypeScript

**Alternatives Rejected:**
- Semua di Node.js: Library data processing JS (papaparse, xlsx) jauh lebih terbatas
- Django: Terlalu berat untuk microservice
- Go: Ekosistem data science sangat terbatas

---

### ADR-003: Multi-LLM Architecture (Strategy Pattern)

**Status:** Accepted
**Date:** 2025-01-01
**Context:** User ingin bisa memilih antara Cerebras, Groq, Gemini, dan Sumopod. Perlu arsitektur yang flexible untuk menambah/mengganti provider.

**Decision:** Menggunakan Strategy Pattern dengan LLM Router yang mendelegasi ke provider adapters.

**Rationale:**
1. Setiap provider memiliki API format yang sedikit berbeda
2. Adapter pattern memungkinkan penambahan provider baru tanpa mengubah code yang ada (Open/Closed Principle)
3. Router bisa implementasi fallback: jika satu provider down, otomatis switch ke yang lain
4. User bisa switch provider tanpa perlu restart/reconfigure
5. A/B testing antar provider jadi mudah

**Consequences:**
- Perlu maintain adapter untuk setiap provider
- Perlu handle perbedaan capabilities antar provider (context window, model list)
- Token counting perlu di-normalize antar provider
- Streaming format mungkin berbeda (perlu unified stream interface)

**Pattern:**
```
LLMRouter (Strategy Context)
  ├── GroqProvider (Concrete Strategy)
  ├── CerebrasProvider (Concrete Strategy)
  ├── GeminiProvider (Concrete Strategy)
  └── SumopodProvider (Concrete Strategy)
```

---

### ADR-004: pgvector Over Dedicated Vector Database

**Status:** Accepted
**Date:** 2025-01-01
**Context:** RAG pipeline membutuhkan vector storage dan similarity search. Harus memilih antara dedicated vector DB (Pinecone, Weaviate, Qdrant) atau extension PostgreSQL (pgvector).

**Decision:** Menggunakan pgvector (PostgreSQL extension).

**Rationale:**
1. Tidak perlu service tambahan untuk di-manage (ops simplicity)
2. Data relasional dan vector dalam satu database (simpler queries, ACID guarantees)
3. Cukup performant untuk skala yang ditarget (< 1 juta vectors)
4. Gratis dan open-source (no vendor lock-in, no usage costs)
5. Backup, monitoring, dan maintenance mengikuti PostgreSQL yang sudah established
6. HNSW index support sejak pgvector 0.5 (performance comparable to dedicated solutions)

**Consequences:**
- Performa mungkin tidak sebaik dedicated vector DB di skala sangat besar (> 10M vectors)
- Perlu upgrade jika skala melampaui kemampuan single PostgreSQL instance
- Memory usage PostgreSQL akan lebih tinggi karena vector data

**Migration Path:** Jika perlu scale:
1. Pertama: Upgrade ke PostgreSQL dengan lebih banyak RAM
2. Kedua: Read replicas khusus untuk vector search
3. Terakhir: Migrasi ke dedicated vector DB (Qdrant/Weaviate) jika benar-benar perlu

---

### ADR-005: Streaming Responses (SSE)

**Status:** Accepted
**Date:** 2025-01-01
**Context:** LLM responses bisa memakan waktu 5-30 detik untuk selesai. UX harus tetap responsive.

**Decision:** Menggunakan Server-Sent Events (SSE) untuk streaming respons AI token-by-token ke client.

**Rationale:**
1. User melihat respons real-time (tidak menunggu respons lengkap)
2. Perceived latency jauh lebih rendah (TTFB < 500ms vs TTL 5-30s)
3. User bisa membatalkan/stop generation jika sudah cukup
4. SSE lebih simple dibanding WebSocket untuk one-way streaming
5. Built-in reconnection di browser (EventSource API)
6. Kompatibel dengan semua LLM provider APIs (semua support streaming)
7. Vercel AI SDK sudah menyediakan primitives untuk ini

**Consequences:**
- Frontend perlu handle partial content rendering
- Error handling lebih complex (error bisa terjadi mid-stream)
- Token counting harus dilakukan setelah stream selesai
- Database write (save message) harus menunggu stream complete

**Implementation:**
- Server: ReadableStream + TextEncoder
- Client: Vercel AI SDK `useChat` hook (handles everything)
- Format: text/event-stream dengan custom events (content_delta, chart, message_end)

---

### ADR-006: Report Structure (BAB System)

**Status:** Accepted
**Date:** 2025-01-01
**Context:** User membutuhkan laporan terstruktur yang mengikuti format akademis/bisnis Indonesia dengan pembagian BAB.

**Decision:** Menggunakan template system dimana laporan dibagi menjadi sections (BAB) yang masing-masing di-generate secara independent oleh AI.

**Rationale:**
1. Pembagian BAB memungkinkan:
   - Generate per-BAB (lebih manageable untuk LLM context window)
   - Edit per-BAB tanpa regenerate seluruh laporan
   - Progress tracking yang jelas (BAB 3/5 selesai)
   - Parallel generation possible (BAB independent)
2. Template system memungkinkan:
   - Reusable report structures
   - Konsistensi antar laporan
   - Custom templates untuk kebutuhan berbeda
3. Setiap BAB bisa memiliki chart dan table embedded
4. RAG context bisa di-customize per BAB (BAB tinjauan pustaka butuh references berbeda dari BAB analisis)

**Consequences:**
- Perlu prompt engineering yang baik per-BAB
- Koherensi antar BAB harus dijaga (pass context dari BAB sebelumnya)
- PDF generation perlu handle page breaks, TOC, numbering
- Storage lebih complex (report -> sections -> content + charts + tables)

**Template Default:**
```
1. BAB I - Pendahuluan (Latar Belakang, Tujuan, Ruang Lingkup)
2. BAB II - Tinjauan/Landasan (Teori, Referensi, State of the Art)
3. BAB III - Metodologi (Sumber Data, Metode, Tools)
4. BAB IV - Hasil dan Pembahasan (Analisis, Visualisasi, Interpretasi)
5. BAB V - Kesimpulan dan Saran (Summary, Rekomendasi, Keterbatasan)
```

---

## LLM Provider Integration Notes

### Cerebras

```
API Format: OpenAI-compatible
Base URL: https://api.cerebras.ai/v1
Authentication: Bearer token
Streaming: SSE (same as OpenAI)
Key Features:
  - Fastest inference speed (>2000 tokens/second)
  - Models: LLaMA 3.1 (8B, 70B)
  - Context window: 8192 tokens
Limitations:
  - Smaller context window compared to others
  - Limited model selection
  - Relatively new service
Use Case di uReport AI:
  - Quick chat responses
  - Short analysis queries
  - Interactive Q&A about data
```

### Groq

```
API Format: OpenAI-compatible
Base URL: https://api.groq.com/openai/v1
Authentication: Bearer token
Streaming: SSE (same as OpenAI)
Key Features:
  - Very low latency (LPU hardware)
  - Models: LLaMA 3.1, Mixtral, Gemma
  - Context window: up to 131K tokens
  - Generous free tier
Limitations:
  - Rate limits on free tier (30 req/min)
  - Model availability bisa berubah
Use Case di uReport AI:
  - Default provider untuk chat
  - Data analysis conversations
  - Report generation (large context window)
```

### Gemini (Google Generative AI)

```
API Format: Google proprietary (different from OpenAI)
Base URL: https://generativelanguage.googleapis.com
Authentication: API key
Streaming: SSE (Google format)
Key Features:
  - Multimodal (text, image, video, audio)
  - Massive context window (1M+ tokens untuk Gemini 1.5 Pro)
  - Strong reasoning and analysis
  - Free tier yang generous
Limitations:
  - API format berbeda dari OpenAI (perlu adapter)
  - Rate limits yang ketat di free tier
  - Response time bisa lebih lambat dibanding Groq/Cerebras
Use Case di uReport AI:
  - Complex analysis (large context)
  - Report generation (bisa process banyak data sekaligus)
  - Multimodal: baca gambar chart yang sudah ada
```

### Sumopod (Custom)

```
API Format: TBD (kemungkinan OpenAI-compatible)
Base URL: Custom endpoint (user-defined)
Authentication: Custom (API key atau OAuth)
Streaming: TBD
Key Features:
  - Full control atas model
  - Data privacy (data tidak ke third party)
  - Customizable untuk domain spesifik
Limitations:
  - Perlu setup infrastructure sendiri
  - Performance tergantung hardware
  - Model quality tergantung fine-tuning
Implementation Notes:
  - Adapter harus flexible (configurable endpoint, auth method, format)
  - Perlu settings UI untuk configure endpoint dan credentials
  - Harus handle kasus dimana Sumopod tidak available (graceful fallback)
Use Case di uReport AI:
  - Use cases yang butuh data privacy
  - Domain-specific analysis
  - When third-party APIs are not preferred
```

---

## Known Constraints & Considerations

### Technical Constraints

1. **LLM Context Window:**
   - Untuk analisis data besar, perlu summarize data sebelum kirim ke LLM
   - Tidak bisa kirim seluruh spreadsheet 10K baris ke LLM langsung
   - Strategi: kirim schema + statistics + relevant subset

2. **File Size Limits:**
   - Excel: Max 50MB (bisa berisi ratusan ribu baris)
   - CSV: Max 100MB
   - Perlu streaming parse untuk file besar

3. **PDF Generation:**
   - Puppeteer butuh Chromium (berat untuk server)
   - Alternative: react-pdf untuk PDF yang lebih simple
   - Charts harus di-render sebagai image dulu sebelum embed ke PDF

4. **Real-time vs Queue:**
   - Chat responses: real-time streaming
   - Report generation: async queue (bisa menit)
   - File parsing: semi-async (beberapa detik)

### Business Constraints

1. **LLM Costs:**
   - Perlu track token usage per user
   - Perlu rate limiting per user
   - Consider caching untuk pertanyaan yang mirip

2. **Storage Costs:**
   - File uploads bisa accumulate cepat
   - Perlu retention policy (hapus file lama)
   - Compress dimana mungkin

3. **Privacy & Security:**
   - Data user adalah sensitif (financial data, business data)
   - Encryption at rest dan in transit wajib
   - Consider apakah data dikirim ke third-party LLM (compliance issue)

---

## Future Considerations

### Near-term (3-6 bulan setelah MVP)
- [ ] Collaborative features (share conversation/report)
- [ ] Export chart sebagai image
- [ ] More chart types (waterfall, funnel, treemap)
- [ ] Dark mode
- [ ] Mobile responsive optimization
- [ ] i18n (multi-language UI)

### Mid-term (6-12 bulan)
- [ ] Real-time collaboration (multiple users edit report)
- [ ] Plugin system untuk data sources (Google Sheets, Airtable)
- [ ] Scheduled reports (auto-generate weekly/monthly)
- [ ] Email notifications
- [ ] API access untuk third-party integration
- [ ] Custom fine-tuned models untuk domain spesifik

### Long-term (12+ bulan)
- [ ] Mobile native app
- [ ] Voice input/output
- [ ] Video explanation of data
- [ ] Multi-tenant/organization support
- [ ] Marketplace untuk report templates
- [ ] AI agent yang bisa menjalankan multi-step analysis autonomously

---

## Technical Debt Tracking

| ID | Description | Priority | Impact | Estimated Effort |
|----|-------------|----------|--------|------------------|
| TD-001 | - | - | - | - |

*Template - isi saat technical debt muncul selama development:*

```
| TD-XXX | Deskripsi masalah | High/Med/Low | Area yang terdampak | Estimasi waktu fix |
```

### Example Entries (akan diisi seiring development):
```
| TD-001 | Error handling belum consistent di semua API routes | Medium | API reliability | 2 hari |
| TD-002 | Chart rendering belum di-memoize, re-render unnecessary | Low | Performance | 1 hari |
| TD-003 | Python service belum ada health check endpoint | Medium | Monitoring | 0.5 hari |
```

---

## Environment-Specific Notes

### Development
- Gunakan `docker compose up -d postgres redis minio` untuk infrastructure
- Hot reload aktif di Next.js dan FastAPI
- Prisma Studio (`bunx prisma studio`) untuk inspect database
- MinIO Console di `localhost:9001` untuk manage files

### Staging
- Deploy ke Railway/Render untuk testing
- Gunakan database terpisah dari production
- Enable verbose logging
- Test dengan data yang mirip production

### Production
- Enable rate limiting
- Setup monitoring (health checks, error tracking)
- Database backups (daily)
- SSL/TLS wajib
- Environment variables via secrets manager
- Log aggregation (e.g., Better Stack, Datadog)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-01 | Initial document creation | - |

*Update dokumen ini setiap ada keputusan arsitektur baru atau perubahan signifikan.*
