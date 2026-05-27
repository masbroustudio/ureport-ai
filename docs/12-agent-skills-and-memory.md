# 11 — Agent Skills & Memory

> Dokumen ini menjelaskan **otak** uReport AI: skill (tool) registry, orkestrasi agent, dan strategi memory (short-term + long-term).

---

## 11.1 Konsep Agent

uReport AI bukan "1 LLM call menjawab semua". Kita pakai **agent loop** dengan state machine:

```
       ┌───────────────────┐
       │   Intent classifier│  ← murah & cepat (8B model)
       └─────────┬─────────┘
                 │
        ┌────────┴─────────┐
        │   Planner        │  ← decide tools + order
        └─────┬─────┬──────┘
              │     │
     ┌────────▼─┐ ┌─▼────────┐
     │ Tool 1   │ │ Tool 2   │  ← execute (parallel ok)
     └────┬─────┘ └─────┬────┘
          │             │
          └──────┬──────┘
                 ▼
         ┌──────────────┐
         │  Synthesizer │  ← compose final response
         └──────┬───────┘
                ▼
            stream → user
```

Implementasi: **LangGraph** (state machine eksplisit, mudah debug).

---

## 11.2 Skill Registry

Skill = capability spesifik yang bisa dipanggil agent. Tiap skill punya schema input/output yang strict.

### Daftar Skill MVP

| Skill | Module | Deskripsi |
|---|---|---|
| `chat_general` | core | Standar chat tanpa tool |
| `search_knowledge_base` | rag | Cari di KB user (top-K + rerank) |
| `list_documents` | rag | List dokumen di KB |
| `get_dataframe_profile` | data | Profile file Excel/CSV |
| `run_python` | data | Execute kode Python di sandbox |
| `make_chart` | data | High-level chart helper |
| `compose_report_outline` | report | Generate outline JSON |
| `write_report_section` | report | Tulis 1 section laporan |
| `render_pdf` | report | Markdown → HTML → PDF |
| `web_search` (V2) | external | Search internet (Tavily/SerpAPI) |
| `get_user_memory` | memory | Ambil fakta/preferensi user |
| `save_user_memory` | memory | Simpan fakta/preferensi baru |

Tiap skill ditulis sebagai Python function dengan decorator:

```python
from app.agent.skills import skill

@skill(
    name="run_python",
    description="Execute Python code in a sandbox with `df` pre-loaded.",
    cost="medium",
    requires=["sandbox"],
)
def run_python(file_id: str, code: str, sheet: str | None = None) -> ExecutionResult:
    ...
```

Skill registry otomatis expose schema ke LLM via tool-calling format (JSON schema OpenAI-compatible).

---

## 11.3 Intent Classifier

Cepat & murah (model 8B, max 200 tok output):

```
INTENT = one of:
- general_chat              (no file, no data ref)
- data_analysis             (file attached or referencing dataset)
- knowledge_qa              (asking about docs in KB)
- report_planning           (request lengkap laporan)
- report_section_write
- meta                      (cara pakai aplikasi)
```

Output JSON:
```json
{ "intent": "data_analysis", "confidence": 0.92, "needs_tools": ["get_dataframe_profile","run_python"] }
```

---

## 11.4 Planner

Untuk task non-trivial, planner LLM keluarkan **tool plan**:

```json
{
  "steps": [
    { "id": "s1", "tool": "get_dataframe_profile", "args": {"file_id": "f1"}},
    { "id": "s2", "tool": "search_knowledge_base", "args": {"query": "tren penjualan retail 2024"}},
    { "id": "s3", "tool": "run_python", "args": {"file_id":"f1","code":"..."}, "depends_on":["s1"]},
    { "id": "s4", "tool": "synthesize",  "depends_on":["s2","s3"]}
  ]
}
```

LangGraph engine eksekusi DAG ini, parallelize step yang independen.

---

## 11.5 Synthesizer

Mengambil hasil semua step + chat history → menghasilkan final response (markdown + reference ke chart/table).

Prompt:
```
SYSTEM:
Anda adalah asisten data analyst. Susun jawaban yang ringkas tapi informatif
dalam Bahasa Indonesia (atau Bahasa Inggris jika user pakai bahasa Inggris).
Selalu kutip sumber dengan [^id] jika data dari knowledge base.

TOOL OUTPUTS:
{tool_outputs_json}

USER QUESTION:
{user_question}

OUTPUT (markdown):
```

---

## 11.6 Memory Strategy

Tiga lapis memory:

### Lapis 1: **Short-term (per conversation)**
- Sliding window N message terbaru (default 20)
- Otomatis di-include di prompt context
- Tidak perlu storage ekstra

### Lapis 2: **Conversation summary** (compress saat panjang)
- Saat conversation > 30 message → summarize 20 message terlama menjadi 1 paragraf
- Disimpan di `conversations.summary` (kolom tambahan)
- Prompt: `[ringkasan awal] + [last N messages]`

### Lapis 3: **Long-term user memory**
- Tabel `user_memories` (lihat `docs/09`)
- Auto-extract "fakta tentang user" dari chat:
  - Profesi, organisasi, domain (mis. "saya manajer toko di Jakarta")
  - Preferensi (mis. "selalu pakai bahasa formal", "favoritnya bar chart")
  - Goals (mis. "sedang riset UMKM")
- Tools `save_user_memory` & `get_user_memory` dipanggil agent kapan perlu
- Saat new conversation: inject ringkasan memory di system prompt

**Auto-ekstraksi**: jalankan job ringan setiap N message via Celery → LLM kecil baca message → output JSON `{kind, content, confidence}`.

---

## 11.7 Persona & Style Memory

Selain fakta, simpan juga **gaya komunikasi** user:
- Bahasa default (id/en)
- Tingkat formalitas (formal / kasual)
- Panjang jawaban favorit (singkat / detail)
- Tipe chart favorit

Dipakai untuk **personalisasi** prompt.

---

## 11.8 Conversation Branching (V1)

User bisa **regenerate dari titik tertentu** atau **edit message lama**:
- Internal: `messages.parent_id` membentuk tree
- Saat regenerate: buat sibling message baru, UI tampilkan switcher 1/2/3
- Konsumsi token bisa naik → batasi max 5 sibling per parent

---

## 11.9 Safety & Guardrails

| Risk | Mitigasi |
|---|---|
| Prompt injection dari file user | Treat semua content file sebagai data, bukan instruksi (system prompt explicit) |
| Tool hallucination (panggil tool tidak ada) | Validate via JSON schema, reject + retry |
| Loop tak berhenti | Max iteration agent = 8 |
| Code injection di sandbox | Sandbox isolated, no host access |
| PII leak ke log | Redact field tertentu (email, NIK pattern) sebelum log |
| Kontroversial/illegal request | System prompt + content filter (kecil di FE & BE) |

---

## 11.10 Prompt Library

Semua prompt disimpan di `packages/prompts/` sebagai `.md` dengan front-matter:

```markdown
---
id: data_analyst.code_generator
version: 1
model_hint: cerebras/llama-3.3-70b
inputs: [profile_json, question]
---

## SYSTEM
Anda adalah data analyst Python expert...

## USER
{question}
```

Loader memuat by id + version. Versioning memudahkan A/B testing & rollback.

---

## 11.11 Logging & Tracing

Tiap agent run di-trace OpenTelemetry:
- Span: `agent.run` → child: `intent`, `plan`, `tool.run_python`, `synthesize`
- Atribut: model, tokens, latency, cost, tool name
- Bisa dilihat di Grafana Tempo / Jaeger

---

## 11.12 Skill Plug-in (V2)

V2: izinkan workspace tambah custom skill:
- Manifest YAML + Python file
- Sandbox import + signature check
- Registry per workspace
