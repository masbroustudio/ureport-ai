# uReport AI — Masterplan (Blueprint v2 / Alternative)

> ⚠️ **Ini adalah blueprint ALTERNATIF (v2).** Blueprint awal ada di [`../BLUEPRINT.md`](../BLUEPRINT.md).
> Lihat [`README.md`](./README.md) di folder ini untuk perbedaan & cara memilih.

> **uReport AI** adalah aplikasi chat AI yang berfokus pada **analisa data** dan **generasi laporan otomatis (PDF)**. Layaknya ChatGPT/Gemini/Claude, tapi disuntik kemampuan Data Analyst + Report Writer dengan dukungan multi-LLM (Cerebras, Groq, Gemini, Sumopod) dan RAG.

---

## 1. Ringkasan Produk

| Aspek | Deskripsi |
|---|---|
| **Nama** | uReport AI |
| **Kategori** | Conversational AI + Data Analytics + Report Automation |
| **Target user** | Analis, manajer, peneliti, mahasiswa, UKM, instansi |
| **Input** | Teks, file Excel (`.xlsx`), CSV (`.csv`), dan dokumen referensi (PDF/DOCX/TXT) |
| **Output** | Jawaban teks, tabel, grafik interaktif, dan **laporan PDF berstruktur BAB** |
| **LLM Provider** | Cerebras, Groq, Google Gemini, Sumopod (custom OpenAI-compatible) |
| **Mode kerja** | (1) Chat biasa, (2) Data Analyst mode, (3) Report Generator mode |

---

## 2. Tiga Pilar Fitur

### Pilar 1 — Smart Chat (multi-LLM)
Chat layaknya ChatGPT, user bisa pilih provider/model. Mendukung streaming, history, multi-konversasi, dan attachment.

### Pilar 2 — Data Analyst Chat
User upload Excel/CSV → AI:
- Mendeteksi schema, tipe data, missing value, outlier
- Menjawab pertanyaan analitik (mean, korelasi, segmentasi, trend)
- Menampilkan **tabel** + **grafik** (bar, line, pie, scatter, heatmap)
- Bisa generate kode Python yang dieksekusi di sandbox aman

### Pilar 3 — Report Generator (PDF)
User minta "buatkan laporan penjualan Q1 2026" → AI:
- Plan struktur laporan (Cover, Daftar Isi, BAB I Pendahuluan, BAB II Metodologi, BAB III Analisis, BAB IV Kesimpulan, Daftar Pustaka)
- Pakai **RAG** untuk pull konteks dari knowledge base/dokumen referensi
- Pakai **data engine** untuk grafik & tabel
- Render ke **PDF** rapi dengan branding

---

## 3. Tech Stack (ringkas)

| Layer | Pilihan |
|---|---|
| **Frontend** | Next.js 15 (App Router) + React + TailwindCSS + shadcn/ui + Vercel AI SDK |
| **Backend** | Python 3.11+ + FastAPI + Pydantic v2 |
| **Orkestrasi LLM** | LiteLLM (unified gateway) + LangGraph (agent) |
| **RAG** | LlamaIndex / LangChain + Qdrant (vector DB) + bge-m3 / Gemini embeddings |
| **Data Engine** | pandas + numpy + Plotly + sandboxed Python (E2B / Jupyter kernel terisolasi) |
| **Report Engine** | Jinja2 → HTML → WeasyPrint (PDF) |
| **Database** | PostgreSQL (data utama) + Redis (cache/queue/session) |
| **Storage** | S3-compatible (MinIO untuk self-host, atau S3/R2) |
| **Auth** | NextAuth (Auth.js) — email/password + OAuth Google |
| **Queue** | Celery + Redis (untuk job berat: report generation) |
| **Deploy** | Docker Compose (dev) → Kubernetes / VPS + Nginx (prod) |

> Detail rasional pilihan tech ada di [`02-tech-stack.md`](./02-tech-stack.md).

---

## 4. Arsitektur Tingkat Tinggi

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js)                    │
│   Chat UI · File Upload · Chart Viewer · PDF Preview        │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS / SSE (streaming)
┌────────────────▼────────────────────────────────────────────┐
│                  Backend API (FastAPI)                      │
│  Auth · Conversations · Files · Reports · Tools registry    │
└──┬─────────┬──────────┬──────────┬───────────┬──────────────┘
   │         │          │          │           │
   ▼         ▼          ▼          ▼           ▼
┌─────┐  ┌──────┐  ┌────────┐  ┌────────┐  ┌──────────┐
│ LLM │  │ RAG  │  │ Data   │  │ Report │  │ Storage  │
│Gate-│  │(Qdr- │  │Engine  │  │Engine  │  │(S3/MinIO)│
│way  │  │ant)  │  │(sand-  │  │(Weasy- │  │ + Redis  │
│Lite-│  │      │  │boxed)  │  │Print)  │  │ + PG     │
│LLM  │  │      │  │        │  │        │  │          │
└─────┘  └──────┘  └────────┘  └────────┘  └──────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│  Cerebras · Groq · Gemini · Sumopod (OpenAI-compat)  │
└──────────────────────────────────────────────────────┘
```

> Detail di [`03-architecture.md`](./03-architecture.md).

---

## 5. Struktur Dokumentasi

| File | Isi |
|---|---|
| [`01-vision-and-scope.md`](./01-vision-and-scope.md) | Visi, target user, problem, scope |
| [`02-tech-stack.md`](./02-tech-stack.md) | Pilihan tech & rasional |
| [`03-architecture.md`](./03-architecture.md) | Arsitektur sistem & data flow |
| [`04-features-and-user-flows.md`](./04-features-and-user-flows.md) | Fitur detail + user journey |
| [`05-llm-providers.md`](./05-llm-providers.md) | Strategi multi-LLM (Cerebras/Groq/Gemini/Sumopod) |
| [`06-rag-and-knowledge.md`](./06-rag-and-knowledge.md) | RAG: ingestion, chunking, retrieval |
| [`07-data-analysis-engine.md`](./07-data-analysis-engine.md) | Excel/CSV analyzer, code interpreter, charting |
| [`08-report-generation.md`](./08-report-generation.md) | PDF report dengan struktur BAB |
| [`09-data-model-and-api.md`](./09-data-model-and-api.md) | DB schema + API contract |
| [`10-frontend-design.md`](./10-frontend-design.md) | UI/UX & komponen frontend |
| [`11-agent-skills-and-memory.md`](./11-agent-skills-and-memory.md) | Skill registry + memory strategy |
| [`12-roadmap-and-milestones.md`](./12-roadmap-and-milestones.md) | Roadmap MVP → V1 → V2 |
| [`13-deployment-and-ops.md`](./13-deployment-and-ops.md) | Deployment, monitoring, biaya |
| [`14-security-and-compliance.md`](./14-security-and-compliance.md) | Security & data privacy |

---

## 6. Cara Membaca Dokumen Ini

1. **Wajib pertama**: `01-vision-and-scope.md` (paham produk dulu)
2. **Wajib kedua**: `02-tech-stack.md` + `03-architecture.md` (paham teknik)
3. **Lalu**: `04-features-and-user-flows.md` (paham yang akan dibangun)
4. **Lanjut deep-dive** sesuai minat: LLM, RAG, Data, Report
5. **Terakhir**: `12-roadmap-and-milestones.md` (paham urutan eksekusi)

---

## 7. Status

| Tahap | Status |
|---|---|
| Blueprint / Masterplan | ✅ Selesai (dokumen ini) |
| Scaffolding monorepo | ⏳ Belum dimulai |
| MVP Backend | ⏳ Belum dimulai |
| MVP Frontend | ⏳ Belum dimulai |
| Beta Release | ⏳ Belum dimulai |

---

## 8. Next Step yang Disarankan

1. Review semua dokumen di folder ``.
2. Konfirmasi pilihan tech stack (boleh di-override sesuai preferensi).
3. Pilih scope MVP (lihat `12-roadmap-and-milestones.md`).
4. Mulai scaffolding repo: `apps/web/`, `apps/api/`, `packages/shared/`.
5. Setup environment (Docker Compose dev) + LLM API keys.
