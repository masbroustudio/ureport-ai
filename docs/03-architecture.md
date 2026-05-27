# 03 — System Architecture

## 3.1 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser / PWA)                  │
│   Next.js · React · TailwindCSS · Vercel AI SDK · Plotly        │
└──────────────────┬──────────────────────────────────────────────┘
                   │ HTTPS · SSE streaming · multipart upload
┌──────────────────▼──────────────────────────────────────────────┐
│                      EDGE / CDN (Vercel / Cloudflare)           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                       API GATEWAY (Nginx)                       │
│            Rate-limit · TLS termination · routing               │
└──┬──────────────┬───────────────┬──────────────┬────────────────┘
   │              │               │              │
   ▼              ▼               ▼              ▼
┌──────┐    ┌──────────┐   ┌──────────┐   ┌──────────────┐
│ Auth │    │ Chat API │   │ File API │   │ Report API   │
│ svc  │    │ (FastAPI)│   │ (FastAPI)│   │ (FastAPI)    │
└──────┘    └────┬─────┘   └─────┬────┘   └──────┬───────┘
                 │               │               │
                 │ ┌─────────────┴───────────────┘
                 │ │
                 ▼ ▼
        ┌────────────────────────┐
        │  Agent Orchestrator    │   ← LangGraph state machine
        │  (LiteLLM gateway)     │
        └──┬──────┬──────┬───────┘
           │      │      │
           ▼      ▼      ▼
        ┌────┐ ┌────┐ ┌─────────┐
        │ RAG│ │Data│ │ Report  │
        │svc │ │svc │ │ svc     │
        └─┬──┘ └─┬──┘ └────┬────┘
          │      │         │
          ▼      ▼         ▼
        ┌─────┐┌──────────┐┌──────────┐
        │Qdr- ││Sandbox   ││WeasyPrint│
        │ant  ││(E2B/nsj) ││Worker    │
        └─────┘└──────────┘└──────────┘

        ┌────────┐  ┌────────┐  ┌────────────┐
        │Postgres│  │ Redis  │  │ S3/MinIO   │
        │(main)  │  │(cache+ │  │(file blob) │
        │        │  │ broker)│  │            │
        └────────┘  └────────┘  └────────────┘

        EXTERNAL LLMs:
        ┌──────────┐ ┌──────┐ ┌────────┐ ┌─────────┐
        │ Cerebras │ │ Groq │ │ Gemini │ │ Sumopod │
        └──────────┘ └──────┘ └────────┘ └─────────┘
```

---

## 3.2 Komponen Utama

### 3.2.1 Frontend (Next.js)
- **Pages**:
  - `/` — landing
  - `/app/chat/[id]` — chat workspace (mirip ChatGPT)
  - `/app/files` — file manager
  - `/app/reports/[id]` — report viewer/editor
  - `/app/settings` — provider/model & API keys per user (opsional)
- **State**: Zustand untuk UI state, server state via React Query / SWR.
- **Streaming**: `useChat` dari Vercel AI SDK, custom transport ke `/api/chat`.

### 3.2.2 API Gateway (Nginx)
- TLS termination
- Rate limiting per IP & per user (mis. 60 req/min)
- Routing ke service berdasarkan path

### 3.2.3 Auth Service
- Auth.js di Next.js handle sign-in
- JWT signed dengan secret share ke FastAPI
- FastAPI middleware verify JWT setiap request

### 3.2.4 Chat / File / Report API (FastAPI)
- Microservice atau monolith dengan modul terpisah (mulai monolith → split kalau perlu)
- Endpoint utama: lihat `docs/09-data-model-and-api.md`

### 3.2.5 Agent Orchestrator (LangGraph)
- State machine yang menentukan urutan tool calls:
  1. Klasifikasi intent (chat / analyze / report)
  2. Pilih tools yang relevan (RAG, data, report)
  3. Eksekusi tool
  4. Compile output → stream ke user

### 3.2.6 LLM Gateway (LiteLLM)
- 1 endpoint, banyak provider
- Router policy: cost-based, latency-based, fallback chain
- Caching response identik (Redis)
- Logging token usage per user

### 3.2.7 RAG Service
- Ingest: parse dokumen → chunk → embed → store di Qdrant
- Retrieve: query → embed → top-K + rerank → konteks
- Per-user collection + global knowledge base (opsional)

### 3.2.8 Data Service (Code Interpreter)
- Terima dataframe + instruksi
- Generate kode Python via LLM
- Eksekusi di sandbox terisolasi (E2B / nsjail)
- Capture: stdout, dataframe baru, gambar Plotly JSON
- Return ke agent

### 3.2.9 Report Service (Async via Celery)
- Terima outline laporan + data + konteks
- Agent isi tiap BAB sequential atau parallel
- Render Markdown → HTML (Jinja2) → PDF (WeasyPrint)
- Simpan PDF di S3 → URL pre-signed ke user

### 3.2.10 Storage
- **PostgreSQL**: user, conversation, message, file metadata, report metadata, usage log
- **Redis**: session, queue (Celery), cache LLM, rate-limit counter
- **S3/MinIO**: file binary (xlsx, csv, pdf, generated PDF)
- **Qdrant**: vektor & metadata chunk

---

## 3.3 Data Flow — 3 Skenario Utama

### Skenario A — Chat Biasa (text-only)

```
User: "Apa beda korelasi vs kausalitas?"
  ↓
Frontend  POST /api/chat (stream)
  ↓
Agent: intent = "general_chat" → no tools needed
  ↓
LiteLLM → Groq llama-3.3-70b (default cepat)
  ↓
Stream tokens → SSE → UI render
  ↓
Persist message di Postgres
```

### Skenario B — Data Analysis (Excel/CSV upload)

```
User upload sales.xlsx + "tampilkan top 5 produk Q1, plus chart"
  ↓
Frontend POST /api/files (multipart) → upload ke S3
  ↓
POST /api/chat dengan file_id reference
  ↓
Agent: intent = "data_analysis"
  ↓
Tool: read_dataframe(file_id) → load via pandas
  ↓
LLM (Cerebras llama-3.3-70b cepat) generate kode:
   df_top = df.groupby('product')['sales'].sum().nlargest(5)
   fig = px.bar(df_top)
  ↓
Sandbox eksekusi → capture: tabel + Plotly JSON
  ↓
Agent compile: jawaban natural + tabel + chart_id
  ↓
FE render Markdown + tabel + Plotly chart interaktif
```

### Skenario C — Generate Laporan PDF

```
User: "Buat laporan analisa penjualan Q1 2026, struktur lengkap BAB 1-5"
+ attach sales.xlsx
+ optionally pilih dokumen referensi dari knowledge base
  ↓
Frontend POST /api/reports (async)
  ↓
Agent step 1 (planner): generate outline JSON
  {
    "title": "...",
    "chapters": [
      {"id":"bab1","title":"Pendahuluan","sections":[...]},
      {"id":"bab2","title":"Metodologi","sections":[...]},
      ...
    ]
  }
  ↓
Show outline ke user → user approve / edit
  ↓
Celery task: untuk tiap section
   - retrieve konteks RAG (jika perlu)
   - panggil data engine (jika butuh chart/tabel)
   - LLM tulis paragraf
  ↓
Compile semua → Markdown master
  ↓
Jinja2 render ke HTML (template laporan)
  ↓
WeasyPrint HTML → PDF
  ↓
Upload PDF ke S3, push event ke FE via SSE/Webhook
  ↓
User download / preview di browser
```

---

## 3.4 Streaming Strategi

- **Chat biasa**: token-level streaming via SSE.
- **Tool calls**: stream "thinking..." status + tool result chunks.
- **Report generation**: progress per BAB via WebSocket atau polling job status.

Format event SSE (proposal):
```
event: token       data: {"text":"Hello"}
event: tool_start  data: {"tool":"read_dataframe","args":{...}}
event: tool_end    data: {"tool":"read_dataframe","output":"shape=(1000,5)"}
event: chart       data: {"id":"chart_abc","type":"plotly","spec":{...}}
event: done        data: {"message_id":"...", "usage":{"prompt":123,"completion":456}}
```

---

## 3.5 Skalabilitas

- **Stateless API** — bisa horizontal scale di belakang load balancer.
- **Worker pool** terpisah (Celery) untuk job berat.
- **Vector DB** (Qdrant) bisa cluster mode di V2.
- **DB read-replica** kalau read-heavy (V2).
- **CDN** untuk static asset & file PDF (R2/CloudFront).

---

## 3.6 Observability

- **Logs**: structured JSON logs → Loki
- **Metrics**: Prometheus exporters (FastAPI, Postgres, Redis, Qdrant)
- **Traces**: OpenTelemetry — terutama trace dari `request → LLM call → tool exec`
- **Dashboards**: Grafana
- **Alerting**: latency P95 LLM, error rate, queue length

---

## 3.7 Failure Modes & Mitigasi

| Failure | Mitigasi |
|---|---|
| LLM provider down | Fallback chain (Groq → Cerebras → Gemini → Sumopod) |
| Sandbox timeout | Default 30s, kill & retry sekali, lalu fail-soft pesan ke user |
| File upload corrupt | Validasi MIME + parse trial sebelum confirm |
| RAG hasil kosong | Tetap jawab tapi tag "tanpa konteks dokumen" |
| PDF render error | Fallback ke .docx atau .md download |
| Cost spike | Hard cap token per user per hari |
