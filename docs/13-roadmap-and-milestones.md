# 12 — Roadmap & Milestones

> Estimasi diasumsikan **1–2 developer fullstack** dengan komitmen menengah. Bisa lebih cepat dengan tim lebih besar.

---

## 12.1 Fase Singkat

| Fase | Durasi | Outcome |
|---|---|---|
| **Phase 0 — Foundation** | 1 minggu | Repo siap, infra dev jalan, akun siap |
| **Phase 1 — MVP Chat Multi-LLM** | 2–3 minggu | Chat layaknya ChatGPT dengan 4 provider |
| **Phase 2 — Data Analyst Mode** | 2–3 minggu | Upload Excel/CSV → tabel + chart |
| **Phase 3 — RAG & Knowledge Base** | 2 minggu | Upload doc → cite di chat |
| **Phase 4 — Report Generator** | 3 minggu | PDF dengan struktur BAB |
| **Phase 5 — Polish & Beta Launch** | 2 minggu | UI polish, monitoring, deploy prod |
| **Total MVP** | **~3 bulan** | Public Beta |

---

## 12.2 Phase 0 — Foundation (Minggu 1)

### Tujuan
Project siap di-coding, semua dev environment running.

### Deliverable
- [ ] Monorepo struktur (`apps/web`, `apps/api`, `packages/*`)
- [ ] Docker Compose dev (postgres, redis, qdrant, minio)
- [ ] FastAPI skeleton + healthcheck
- [ ] Next.js skeleton + Tailwind + shadcn/ui setup
- [ ] Auth.js + email signup + Google OAuth
- [ ] CI: lint, format, typecheck, test
- [ ] `.env.example` & dokumentasi setup
- [ ] Akun & API keys: Cerebras, Groq, Gemini, Sumopod, S3/R2

### Acceptance
Developer baru bisa clone → 1 command → app jalan lokal.

---

## 12.3 Phase 1 — MVP Chat Multi-LLM (Minggu 2–4)

### Tujuan
User bisa chat seperti ChatGPT, ganti-ganti provider.

### Deliverable
- [ ] DB schema: users, workspaces, conversations, messages
- [ ] LiteLLM gateway terkonfigurasi (4 provider)
- [ ] Endpoint `POST /conversations/{id}/messages` SSE streaming
- [ ] Frontend chat UI (sidebar + composer + bubble)
- [ ] Markdown rendering (code highlight, table, math)
- [ ] Multi-conversation, rename, delete, archive
- [ ] Settings page: pilih default provider/model
- [ ] Usage logging & cost tracking dasar
- [ ] Rate limit per user

### Acceptance
- Bisa chat 100 message tanpa error
- Pilih provider via dropdown, fallback otomatis kalau provider down
- Konsumsi tercatat di `usage_logs`

---

## 12.4 Phase 2 — Data Analyst Mode (Minggu 5–7)

### Tujuan
Upload Excel/CSV → AI analisa → tabel + chart.

### Deliverable
- [ ] Endpoint `POST /files` (S3 upload)
- [ ] Auto-profiling (pandas)
- [ ] Sandbox integration (E2B account & wrapper)
- [ ] Skills: `get_dataframe_profile`, `run_python`, `make_chart`
- [ ] Agent: intent classifier + planner + synthesizer (LangGraph)
- [ ] Frontend: file upload UI, file panel preview
- [ ] Plotly viewer & data grid
- [ ] Custom SSE event handler (chart, table)

### Acceptance
- Upload 1 MB CSV (10K rows) → chat "top 5 by X" → dapat tabel + chart < 30 detik
- Kode generate bisa dilihat user (tab "Code")
- Sandbox isolated (tidak bisa akses internet/host)

---

## 12.5 Phase 3 — RAG & Knowledge Base (Minggu 8–9)

### Tujuan
User upload PDF/DOCX → AI bisa rujuk ke dokumen tersebut di jawaban.

### Deliverable
- [ ] Endpoint `POST /kb/documents` (async ingest via Celery)
- [ ] Loaders: PDF (pymupdf), DOCX (python-docx), TXT
- [ ] Chunker (semantic + sliding window)
- [ ] Embedding lokal (bge-m3) + Qdrant store
- [ ] Reranker (bge-reranker-v2-m3)
- [ ] Skill `search_knowledge_base`
- [ ] Frontend page `/knowledge` (manage docs)
- [ ] Citation rendering di message bubble (footnote modal)

### Acceptance
- Upload 5 PDF (50 hal) selesai ingest < 3 menit
- Tanya "menurut dokumen X, apa Y?" → jawaban dengan citation [^1]
- Klik citation → modal teks chunk asli

---

## 12.6 Phase 4 — Report Generator (Minggu 10–12)

### Tujuan
User minta laporan → dapat PDF berstruktur BAB.

### Deliverable
- [ ] Endpoint `POST /reports`, `PUT /outline`, `POST /start`, SSE progress
- [ ] Skill: `compose_report_outline`, `write_report_section`, `render_pdf`
- [ ] Template: `business_report_v1` (Jinja2 + CSS Paged Media)
- [ ] WeasyPrint integrasi
- [ ] Celery worker untuk job berat
- [ ] Frontend: outline editor, progress UI, PDF preview & download

### Acceptance
- Generate laporan 10-15 halaman dari Excel + KB doc dalam < 5 menit
- PDF rapi (TOC otomatis, page number, header/footer)
- Bisa edit outline sebelum start, regenerate per section

---

## 12.7 Phase 5 — Polish & Beta (Minggu 13–14)

### Deliverable
- [ ] Onboarding 3-step
- [ ] Empty states & prompt suggestions
- [ ] Error handling halus + retry
- [ ] Mobile responsive + PWA
- [ ] Dark mode polish
- [ ] Monitoring (Grafana + alerts)
- [ ] Privacy policy + ToS halaman
- [ ] Domain produksi + HTTPS + backup harian DB
- [ ] Beta invite system (waitlist + code redeem)

### Acceptance
- Lighthouse score > 90
- Uptime > 99% dalam 7 hari testing
- 10 beta tester sukses bikin laporan tanpa bantuan

---

## 12.8 Roadmap V1 (Pasca-MVP, Bulan 4–6)

| Item | Deskripsi |
|---|---|
| Multi template laporan | 4 template tambahan (akademik, riset, eksekutif, marketing) |
| Edit Markdown manual | Editor di-page report, re-render PDF tanpa LLM |
| DOCX export | Pandoc atau python-docx |
| Branding kustom | Upload logo, set warna |
| Custom Python lib di sandbox | Per workspace, whitelist controlled |
| Conversation branching | Regenerate sibling, switcher UI |
| Memory page | User lihat & edit fakta yang AI tahu tentang dia |
| Sharing & link publik | View-only link untuk laporan/chat |
| Search global | Search di seluruh chat & file |
| Voice input | Whisper (Groq) |

---

## 12.9 Roadmap V2 (Bulan 7–12)

| Item | Deskripsi |
|---|---|
| Tim & multi-user workspace | Invite anggota, role |
| Connector DB | Postgres/MySQL/Sheet read-only |
| Scheduled report | Cron-based regenerate (mis. weekly) |
| Plugin marketplace | Custom skill upload |
| Mobile native (Expo) | iOS + Android |
| Fine-tune model lokal | Untuk klien enterprise |
| On-premise deploy | Air-gapped option |
| BI dashboard mode | Multiple chart on canvas |

---

## 12.10 Risiko & Asumsi

| Risiko | Mitigasi |
|---|---|
| Provider LLM ubah pricing | Multi-provider sudah memitigasi |
| Sandbox cost tinggi | Self-host nsjail/gVisor di V1 jika E2B mahal |
| Adopsi rendah | Beta tester active feedback loop, pivot fitur cepat |
| RAG kualitas rendah | Eval pipeline + tuning chunk size + reranker |
| PDF rendering bug | Snapshot test (visual diff) per template |

---

## 12.11 Definition of Done (Tiap Phase)

Sebuah phase dianggap selesai kalau:
1. Semua deliverable check ✅
2. Unit test coverage > 60% area baru
3. E2E test happy path lulus (Playwright)
4. Dokumentasi update
5. Review minimal 1 reviewer
6. Deploy ke staging & smoke test 1 hari
