# uReport AI — Saran Pengembangan & Perbaikan

> Dokumen ini berisi rekomendasi pengembangan fitur dan perbaikan teknis setelah Phase 0–5 selesai. Dikelompokkan berdasarkan prioritas dan dilengkapi estimasi effort.

---

## Status Saat Ini

| Phase | Status | Commit |
|---|---|---|
| Phase 0 — Foundation | ✅ Selesai | `7a8a071` |
| Phase 1 — MVP Chat Multi-LLM | ✅ Selesai | `086affd` |
| Phase 2 — Data Analyst Mode | ✅ Selesai | `fcf57f6` |
| Phase 3 — RAG & Knowledge Base | ✅ Selesai | `9f81bc4` |
| Phase 4 — Report Generator | ✅ Selesai | `a2030e5` |
| Phase 5 — Polish & Beta | ✅ Selesai | `91c14d6` |

**Total**: ~30 commits, 133+ tests passing, 13 frontend pages, 15.000+ LOC.

---

## 🔴 Prioritas Tinggi (Perbaikan Penting)

Harus diselesaikan sebelum production launch. Terkait keamanan, reliabilitas, dan skalabilitas dasar.

### 1. Real Database Integration Testing

**Masalah**: Semua tests saat ini menggunakan mock. Belum tervalidasi bahwa Alembic migration, SQLAlchemy queries, dan foreign key constraints berjalan benar dengan PostgreSQL sesungguhnya.

**Solusi**:
- Tambah integration test suite menggunakan `testcontainers-python` (spin up real Postgres di Docker saat test)
- Test migration: `alembic upgrade head` + `alembic downgrade base` + `alembic upgrade head`
- Test CRUD operations end-to-end dengan real DB

**Effort**: 2–3 hari
**File terdampak**: `apps/api/tests/`, `apps/api/pyproject.toml`

---

### 2. Refresh Token & Secure Session

**Masalah**: JWT access token disimpan di `localStorage` — rentan terhadap XSS attack. Jika token dicuri, attacker punya akses penuh.

**Solusi**:
- Implementasi refresh token (long-lived) di `httpOnly` secure cookie
- Access token tetap di memory (bukan localStorage), short-lived (15 menit)
- Endpoint `POST /api/v1/auth/refresh` untuk rotate token
- Logout = revoke refresh token (blacklist di Redis sampai natural expiry)

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/router/auth.py`, `apps/api/app/service/auth.py`, `apps/web/src/lib/api.ts`, `apps/web/src/hooks/useAuth.ts`

---

### 3. File Storage → S3/MinIO

**Masalah**: File disimpan di local filesystem (`./storage/uploads/`) — tidak scalable, hilang saat container restart, tidak bisa multi-instance.

**Solusi**:
- Implementasi S3 client wrapper (`apps/api/app/storage/s3.py`)
- Upload file ke MinIO/S3 bucket
- Download via pre-signed URL (TTL 5 menit)
- Delete cascade: hapus dari S3 saat file/KB doc dihapus
- Fallback ke local filesystem jika `S3_ENDPOINT` tidak dikonfigurasi

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/service/files.py`, `apps/api/app/storage/`, `apps/api/app/router/files.py`, `apps/api/app/rag/ingest.py`

---

### 4. Celery Background Jobs

**Masalah**: Report generation dan KB document ingestion berjalan synchronous. Dokumen besar (100+ halaman) atau laporan kompleks (12+ section) akan timeout request.

**Solusi**:
- Setup Celery worker dengan Redis broker
- Tasks:
  - `ingest_document_task(document_id)` — async KB ingestion
  - `generate_report_task(report_id)` — async report writing
- Status tracking via Redis (or DB polling)
- Frontend polling atau WebSocket untuk progress
- Retry mechanism (max 3x) untuk transient failures

**Effort**: 3–4 hari
**File terdampak**: `apps/api/app/workers/`, `apps/api/app/rag/ingest.py`, `apps/api/app/report/writer.py`, `apps/api/app/router/reports.py`, `apps/api/app/router/knowledge.py`

---

### 5. Input Sanitization & Validation

**Masalah**: File upload hanya cek MIME type (header-based). User bisa rename malware jadi `.csv`. Message length tidak dibatasi.

**Solusi**:
- Magic byte verification (libmagic / python-magic) selain MIME check
- Max message length: 10.000 karakter
- Max file name length: 255 karakter
- Filename sanitization (strip path traversal, unicode normalization)
- Rate limit upload: max 10 files per jam per user
- Optional: ClamAV scan untuk production

**Effort**: 1–2 hari
**File terdampak**: `apps/api/app/router/files.py`, `apps/api/app/router/conversations.py`, `apps/api/pyproject.toml` (add python-magic)

---

## 🟡 Prioritas Sedang (Fitur Pengayaan)

Meningkatkan value produk dan UX. Selesaikan setelah perbaikan kritis.

### 6. Multi-Template Report

**Deskripsi**: Saat ini hanya ada `business_report_v1`. Tambah template untuk use case berbeda.

**Template yang disarankan**:
| Template ID | Nama | Target User |
|---|---|---|
| `academic_thesis_v1` | Skripsi/Tesis | Mahasiswa |
| `research_paper_v1` | Paper Riset | Peneliti |
| `executive_summary_v1` | Ringkasan Eksekutif | Pimpinan/C-level |
| `market_research_v1` | Riset Pasar | Marketing |

**Per template**: `meta.yaml` + `layout.html.j2` + `styles.css`

**Effort**: 2–3 hari (4 template)
**File terdampak**: `apps/api/app/report/templates/`

---

### 7. DOCX Export

**Deskripsi**: Banyak user perlu edit lanjutan di Microsoft Word setelah AI generate draft.

**Solusi**:
- Endpoint `GET /api/v1/reports/{id}/docx`
- Konversi dari Markdown ke DOCX menggunakan `python-docx`
- Preserve: heading, bold/italic, tabel, page break antar BAB
- Embed chart sebagai gambar (export Plotly → PNG via kaleido)

**Effort**: 3–4 hari
**File terdampak**: `apps/api/app/report/renderer.py` (tambah method), `apps/api/app/router/reports.py`

---

### 8. Conversation Search

**Deskripsi**: Power user kesulitan menemukan chat lama dari ratusan conversation.

**Solusi**:
- `GET /api/v1/conversations/search?q=...` — full-text search
- PostgreSQL `tsvector` + GIN index di kolom `messages.content`
- Search across conversation titles + message content
- Frontend: search bar di atas sidebar

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/router/conversations.py`, `apps/api/app/model/message.py` (index), Alembic migration, `apps/web/src/components/chat/ChatSidebar.tsx`

---

### 9. Reranker untuk RAG

**Deskripsi**: Saat ini RAG hanya menggunakan dense vector search. Relevansi bisa meningkat 20–40% dengan cross-encoder reranker.

**Solusi**:
- Tambah `sentence-transformers` (atau `fastembed` reranker jika tersedia)
- Model: `BAAI/bge-reranker-v2-m3` (atau lighter: `ms-marco-MiniLM-L-6-v2`)
- Pipeline: embed → top-20 → rerank → top-8
- Toggle: user bisa enable/disable reranker (trade-off speed vs quality)

**Effort**: 2 hari
**File terdampak**: `apps/api/app/rag/retriever.py`, `apps/api/app/rag/reranker.py` (new)

---

### 10. WebSocket untuk Report Progress

**Deskripsi**: Saat ini report progress via SSE. Untuk long-running report (5+ menit), SSE connection bisa drop.

**Solusi**:
- WebSocket endpoint `ws://localhost:8000/ws/reports/{id}`
- Real-time progress events (same format as SSE)
- Auto-reconnect di frontend
- Fallback: polling `GET /reports/{id}` setiap 5 detik

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/router/reports.py`, `apps/web/src/hooks/useReportProgress.ts`

---

### 11. Cost & Usage Dashboard

**Deskripsi**: User perlu tahu berapa token/biaya yang sudah dihabiskan.

**Solusi**:
- Halaman `/settings/usage` di frontend
- Grafik: token usage per hari (line chart)
- Breakdown per provider & per model
- Monthly total cost estimation
- Budget cap warning (hampir habis)
- Backend: `GET /api/v1/usage/me?period=month` → aggregated stats

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/router/usage.py` (new), `apps/web/src/app/(app)/settings/usage/page.tsx` (new)

---

### 12. Conversation Branching

**Deskripsi**: User ingin "edit & resubmit" pesan sebelumnya tanpa menghapus respons lama, mirip fitur ChatGPT.

**Solusi**:
- `messages.parent_id` sudah ada di schema
- Tambah endpoint `POST /messages/{id}/branch` — edit pesan, buat sibling
- Frontend: switcher "1/2/3" di message bubble untuk switch antar branch
- Max 5 sibling per parent (prevent abuse)

**Effort**: 3–4 hari
**File terdampak**: `apps/api/app/router/conversations.py`, `apps/web/src/components/chat/MessageBubble.tsx`

---

### 13. Multi-File Analysis

**Deskripsi**: User ingin gabung/bandingkan multiple file dalam satu analisis.

**Solusi**:
- Chat request accept multiple `file_ids`
- Sandbox: pre-load sebagai `df1`, `df2`, ... atau `dfs = {"sales_q1": df1, "sales_q2": df2}`
- LLM prompt include profile semua file
- UI: multi-select file di composer

**Effort**: 2–3 hari
**File terdampak**: `apps/api/app/data/sandbox.py`, `apps/api/app/data/prompts.py`, `apps/api/app/router/conversations.py`

---

### 14. Chart Export (PNG/SVG)

**Deskripsi**: User perlu embed chart di presentasi/laporan eksternal.

**Solusi**:
- Tombol "Download" di PlotlyChart component
- Client-side: `Plotly.downloadImage()` (PNG, SVG, JPEG)
- Atau server-side: `kaleido` library untuk headless Plotly export

**Effort**: 1 hari (client-side) / 2 hari (server-side)
**File terdampak**: `apps/web/src/components/charts/PlotlyChart.tsx`

---

## 🟢 Prioritas Rendah (Nice to Have / V2)

Fitur jangka panjang untuk skala enterprise. Kerjakan setelah product-market fit tercapai.

### 15. OAuth Google Login

**Deskripsi**: Simplifikasi onboarding — signup/signin dengan 1 klik via Google.

**Solusi**:
- Integrasi NextAuth v5 di frontend (sudah planned di steering)
- Backend: verify Google ID token, auto-create user jika belum ada
- Link/unlink akun OAuth ke email existing

**Effort**: 2–3 hari

---

### 16. Team & Workspace

**Deskripsi**: Multi-user collaboration dalam 1 workspace. Penting untuk enterprise.

**Solusi**:
- Model: `workspaces`, `workspace_members` (role: owner/admin/editor/viewer)
- Semua resource scoped per workspace (bukan per user)
- Invite via email, accept/reject
- Shared knowledge base & files

**Effort**: 5–7 hari

---

### 17. Scheduled Reports

**Deskripsi**: Auto-regenerate laporan secara berkala (weekly/monthly).

**Solusi**:
- Model: `report_schedules` (report_id, cron_expression, enabled)
- Celery Beat untuk periodic tasks
- Re-run report pipeline dengan data terbaru
- Email notifikasi setelah selesai

**Effort**: 3–4 hari

---

### 18. Voice Input

**Deskripsi**: Hands-free input via suara → text.

**Solusi**:
- Frontend: `MediaRecorder` API → kirim audio blob
- Backend: transkrip via Groq Whisper API (`groq/whisper-large-v3`)
- Hasil transkrip langsung jadi chat message

**Effort**: 2–3 hari

---

### 19. Database Connector

**Deskripsi**: Connect langsung ke database user (read-only) tanpa export CSV.

**Solusi**:
- UI: form input connection string (host, port, user, password, dbname)
- Backend: `asyncpg` / `aiomysql` connect → run SELECT query → return as DataFrame
- Security: whitelist query patterns, read-only connection, timeout 30s
- Encryption: store credentials encrypted (Fernet)

**Effort**: 4–5 hari

---

### 20. Fine-tuned Model (Domain-specific)

**Deskripsi**: Model yang lebih konsisten untuk Bahasa Indonesia formal & domain tertentu.

**Solusi**:
- Kumpulkan dataset: 500+ contoh laporan berkualitas
- Fine-tune via OpenAI API / LoRA di Llama
- Deploy sebagai Sumopod endpoint
- A/B test vs base model

**Effort**: 2–4 minggu (termasuk data collection)

---

### 21. Plugin/Skill System

**Deskripsi**: User atau admin bisa tambah custom "skill" (Python function) yang dipanggil agent.

**Solusi**:
- Manifest YAML + Python file per skill
- Skill registry per workspace
- Sandbox import & signature validation
- UI: manage installed skills di settings

**Effort**: 5–7 hari

---

### 22. Real-time Collaboration

**Deskripsi**: Multiple user edit report yang sama secara bersamaan.

**Solusi**:
- Operational Transform (OT) atau CRDT untuk conflict resolution
- WebSocket untuk sync state
- Presence indicator (siapa online)
- Library: Yjs atau Liveblocks

**Effort**: 2–3 minggu

---

## 🛠️ Technical Debt & Improvements

Perbaikan kode internal yang tidak terlihat user tapi penting untuk maintainability.

| # | Area | Perbaikan | Effort |
|---|---|---|---|
| TD-1 | **Integration Tests** | Tambah test suite dengan `testcontainers-python` (real Postgres + Qdrant) | 2 hari |
| TD-2 | **E2E Tests** | Playwright tests: signup → upload → chat → report → download | 3 hari |
| TD-3 | **API Versioning** | Ensure `/api/v1/` prefix konsisten, siapkan deprecation strategy | 0.5 hari |
| TD-4 | **Error Codes** | Standarisasi: `{"code": "FILE_TOO_LARGE", "message": "...", "details": {...}}` | 1 hari |
| TD-5 | **Pagination** | Audit semua list endpoints → pastikan cursor-based, bukan offset | 1 hari |
| TD-6 | **Redis Caching** | Cache: LLM response identik (5 min TTL), file profile, KB search results | 2 hari |
| TD-7 | **OpenAPI Type Gen** | Auto-generate TypeScript types dari FastAPI OpenAPI → `packages/shared-types/` | 1 hari |
| TD-8 | **CI/CD Pipeline** | GitHub Actions: lint → test → build image → push GHCR → deploy staging | 2 hari |
| TD-9 | **Dependency Updates** | Setup Renovate/Dependabot untuk auto-update packages | 0.5 hari |
| TD-10 | **Sandbox Hardening** | Migrate subprocess → gVisor/nsjail/Firecracker untuk production | 3–5 hari |
| TD-11 | **Logging Correlation** | Trace ID dari frontend → backend → LLM call (OpenTelemetry spans) | 2 hari |
| TD-12 | **Database Connection Pool** | Implement connection pooling (SQLAlchemy pool_size, max_overflow) | 0.5 hari |

---

## Rekomendasi Sprint Planning

### Sprint 1 — Security & Reliability (1 minggu)

| Task | Ref | Effort |
|---|---|---|
| Real DB integration testing | #1 | 2 hari |
| Refresh token & secure session | #2 | 2 hari |
| S3 storage integration | #3 | 2 hari |
| Input sanitization | #5 | 1 hari |

**Outcome**: App aman untuk production pilot.

---

### Sprint 2 — Scalability & Templates (1 minggu)

| Task | Ref | Effort |
|---|---|---|
| Celery background jobs | #4 | 3 hari |
| Multi-template report (2 tambahan) | #6 | 2 hari |
| Cost & usage dashboard | #11 | 2 hari |

**Outcome**: App bisa handle dokumen besar & user punya visibility cost.

---

### Sprint 3 — UX & Quality (1 minggu)

| Task | Ref | Effort |
|---|---|---|
| Conversation search | #8 | 2 hari |
| RAG reranker | #9 | 2 hari |
| Multi-file analysis | #13 | 2 hari |
| CI/CD Pipeline | TD-8 | 2 hari |

**Outcome**: Search cepat, RAG lebih akurat, multi-file support.

---

### Sprint 4 — Export & Polish (1 minggu)

| Task | Ref | Effort |
|---|---|---|
| DOCX export | #7 | 3 hari |
| Chart export PNG/SVG | #14 | 1 hari |
| Conversation branching | #12 | 3 hari |
| OpenAPI type gen | TD-7 | 1 hari |

**Outcome**: Export lengkap, branching mirip ChatGPT.

---

## Metrik Keberhasilan

| Metrik | Target Saat Ini | Target Setelah Sprint 1–4 |
|---|---|---|
| Test coverage (backend) | ~60% (mocked) | >80% (real + mocked) |
| Response time P95 (chat) | ~2s | <1s (dengan caching) |
| Report generation time | ~3 min (sync) | <5 min (async, 20 halaman) |
| Max concurrent users | ~10 (single process) | ~100 (multi-worker + queue) |
| RAG accuracy (subjective) | ~70% | ~85% (dengan reranker) |
| Uptime target | - | 99.5% |

---

## Changelog Dokumen Ini

| Tanggal | Perubahan |
|---|---|
| 2026-05-28 | Initial version setelah Phase 0–5 selesai |

---

> **Catatan**: Prioritas bisa berubah berdasarkan feedback beta tester. Review dokumen ini setiap 2 minggu.
