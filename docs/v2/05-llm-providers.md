# 05 — LLM Providers & Routing Strategy

uReport AI mendukung **4 provider** dari awal: **Cerebras**, **Groq**, **Google Gemini**, dan **Sumopod** (custom OpenAI-compatible). Dokumen ini menjelaskan cara integrasi, routing, dan fallback.

---

## 5.1 Profil Tiap Provider

| Provider | Tipikal Model | Kekuatan | Kelemahan | Cocok Untuk |
|---|---|---|---|---|
| **Cerebras** | `llama3.1-8b`, `llama-3.3-70b`, `qwen-3-coder` | Sangat cepat (output >2000 tok/s), ideal untuk reasoning panjang | Konteks model dibatasi, model terbatas | Code generation, data analysis (cepat) |
| **Groq** | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b`, `gemma2-9b` | Cepat (LPU), murah, tier gratis besar | Rate limit per menit | Chat default, ringan, streaming |
| **Google Gemini** | `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-2.5-flash` | Multimodal (vision), context window besar (1M tokens), bagus untuk doc panjang | Bisa lambat untuk task simple | Long-context, multimodal, planner laporan |
| **Sumopod** | model proprietary (OpenAI-compatible API) | Custom, mungkin domain-specific (Bahasa Indonesia?) | Bergantung uptime vendor | Backup atau use-case khusus |

> Catatan: nama model di atas adalah ilustratif. Final list di-resolve runtime via API list-models tiap provider.

---

## 5.2 Unified Gateway: LiteLLM

Daripada coding tiap SDK, kita pakai **[LiteLLM](https://github.com/BerriAI/litellm)** sebagai abstraction:

```python
from litellm import completion

response = completion(
    model="groq/llama-3.3-70b-versatile",  # atau "cerebras/...", "gemini/...", custom prefix
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
```

LiteLLM otomatis handle:
- Auth header per provider
- Format converter (OpenAI ↔ Anthropic ↔ Google)
- Streaming format normalization
- Retry & timeout

### Konfigurasi Sumopod (Custom OpenAI-compatible)

LiteLLM support custom endpoint via prefix `openai/`:

```python
import litellm

litellm.register_model({
    "sumopod/sumopod-pro": {
        "max_tokens": 8192,
        "litellm_provider": "openai",
        "api_base": "https://api.sumopod.example/v1",
        "api_key_env": "SUMOPOD_API_KEY",
    }
})
```

Atau via `config.yaml` LiteLLM proxy mode (lebih clean untuk produksi).

---

## 5.3 Konfigurasi Model di Backend

`apps/api/app/llm/registry.yaml`:

```yaml
providers:
  cerebras:
    api_key_env: CEREBRAS_API_KEY
    base_url: https://api.cerebras.ai/v1
    models:
      - id: cerebras/llama-3.3-70b
        context: 8192
        cost_per_1m_in: 0.85
        cost_per_1m_out: 1.20
        capabilities: [chat, tools, code]
  groq:
    api_key_env: GROQ_API_KEY
    models:
      - id: groq/llama-3.3-70b-versatile
        context: 32768
        cost_per_1m_in: 0.59
        cost_per_1m_out: 0.79
        capabilities: [chat, tools]
      - id: groq/llama-3.1-8b-instant
        context: 8192
        cost_per_1m_in: 0.05
        cost_per_1m_out: 0.08
        capabilities: [chat]
  gemini:
    api_key_env: GEMINI_API_KEY
    models:
      - id: gemini/gemini-2.0-flash
        context: 1000000
        cost_per_1m_in: 0.10
        cost_per_1m_out: 0.40
        capabilities: [chat, tools, vision, long-context]
      - id: gemini/gemini-1.5-pro
        context: 2000000
        cost_per_1m_in: 1.25
        cost_per_1m_out: 5.00
        capabilities: [chat, tools, vision, long-context]
  sumopod:
    api_key_env: SUMOPOD_API_KEY
    base_url: https://api.sumopod.example/v1
    openai_compatible: true
    models:
      - id: sumopod/sumopod-pro
        context: 16384
        capabilities: [chat]

routing:
  default: groq/llama-3.3-70b-versatile
  fallback_chain:
    - groq/llama-3.3-70b-versatile
    - cerebras/llama-3.3-70b
    - gemini/gemini-2.0-flash
    - sumopod/sumopod-pro
  task_overrides:
    code_generation: cerebras/llama-3.3-70b
    long_context_reasoning: gemini/gemini-1.5-pro
    cheap_classification: groq/llama-3.1-8b-instant
    report_planner: gemini/gemini-2.0-flash
    report_writer: cerebras/llama-3.3-70b
    embedding: gemini/text-embedding-004    # atau lokal bge-m3
```

> Update angka cost berkala — gunakan harga publik resmi di waktu deploy.

---

## 5.4 Strategi Routing

### A. Mode "Auto" (default)
Sistem pilih model berdasarkan **task type**:
- Klasifikasi intent → `cheap_classification` (8b)
- Code/data analysis → `code_generation`
- Long-context (laporan panjang) → `long_context_reasoning`
- Default chat → model `default`

### B. Mode "Manual"
User pilih provider+model dari dropdown. Setting tersimpan per conversation atau per user.

### C. Fallback Chain
Jika provider error (timeout, 429, 5xx):
1. Retry sekali (max 2 detik)
2. Switch ke model berikutnya di `fallback_chain`
3. Notify user halus: *"Beralih ke model alternatif untuk performa optimal"*
4. Log incident untuk monitoring

### D. Cost Guard
- Setiap user punya **monthly budget** (mis. $2 default).
- Sebelum tiap call: estimate token x cost.
- Jika lewat: degrade ke model murah (8b) atau minta upgrade.

---

## 5.5 Tool / Function Calling

Tidak semua provider support tool calling dengan kualitas sama:

| Provider | Tool calling quality | Catatan |
|---|---|---|
| Gemini | ⭐⭐⭐⭐⭐ | Native, paling reliable |
| Groq (Llama 3.3 70B) | ⭐⭐⭐⭐ | Bagus, kadang halusinasi nama tool |
| Cerebras (Llama 3.3 70B) | ⭐⭐⭐⭐ | Bagus, sangat cepat |
| Sumopod | ❓ | Tergantung model — uji dulu |

**Strategi**:
- Tool-heavy task (data analyst, report generator) → wajib pakai provider tier ⭐⭐⭐⭐ ke atas.
- Untuk Sumopod, jika tool calling lemah → fallback ke "structured output via JSON mode" + parse manual.

---

## 5.6 Streaming

LiteLLM normalize event stream menjadi format mirip OpenAI:

```python
for chunk in completion(model=..., messages=..., stream=True):
    delta = chunk.choices[0].delta.content
    if delta: yield delta
```

Backend FastAPI re-emit sebagai SSE ke frontend (lihat `docs/03-architecture.md` §3.4).

---

## 5.7 Embedding

**Default lokal**: `bge-m3` (multilingual, 8K seq) via `sentence-transformers`.
**Alternatif premium**: Gemini `text-embedding-004` (768d, multilingual, support task type).
**Pilihan**: di `registry.yaml` user/admin bisa toggle global atau per knowledge base.

---

## 5.8 Best Practices Implementasi

1. **Abstraksi 1 lapis lagi** di atas LiteLLM (`app.llm.client`) supaya gampang ganti library kalau perlu.
2. **Selalu set `timeout` & `max_retries`**.
3. **Selalu log**: `provider, model, prompt_tokens, completion_tokens, latency_ms, cost_usd, conversation_id`.
4. **Idempotency**: cache hash (model, messages) untuk request identik (Redis TTL 5 menit).
5. **Token counter** sebelum kirim — gunakan `tiktoken` atau native counter Gemini untuk hindari overflow context.
6. **Prompt versioning** — taruh di `packages/prompts/` dengan id seperti `prompts/data_analyst.v1.md`.

---

## 5.9 Environment Variables (sample `.env`)

```env
# Provider keys
CEREBRAS_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
SUMOPOD_API_KEY=
SUMOPOD_BASE_URL=https://api.sumopod.example/v1

# LiteLLM proxy (opsional)
LITELLM_PROXY_URL=
LITELLM_PROXY_KEY=

# Limits
DEFAULT_USER_MONTHLY_BUDGET_USD=2.00
LLM_REQUEST_TIMEOUT_S=60
LLM_MAX_RETRIES=2
```
