# 📘 Blueprint v2 (Alternative) — uReport AI

> Folder ini berisi **blueprint alternatif** untuk uReport AI, hasil iterasi lanjutan.
> **TIDAK menggantikan** dokumen di `docs/` (root) — keduanya bisa di-compare.

## Beda v2 dengan Blueprint Awal

| Aspek | Blueprint Awal (`docs/`) | Blueprint v2 (folder ini) |
|---|---|---|
| **Backend dominan** | Next.js + Python FastAPI microservice | **FastAPI utama**, Next.js murni FE |
| **ORM** | Prisma (TypeScript) | SQLAlchemy + Alembic (Python) |
| **Vector DB** | pgvector (di Postgres) | **Qdrant** (terpisah) |
| **Charts** | Recharts | **Plotly.js** (interaktif lebih kaya) |
| **PDF Engine** | Puppeteer | **WeasyPrint** (CSS Paged Media native) |
| **LLM Layer** | Vercel AI SDK + per-provider SDK | **LiteLLM gateway** + LangGraph agent |
| **RAG Framework** | LangChain | **LlamaIndex** + reranker bge-v2-m3 |
| **Job Queue** | BullMQ (Node) | **Celery** (Python, broker Redis) |
| **Sandbox** | (tidak detail) | **E2B** managed → self-host nsjail di V2 |

## Kapan Pilih v2?

✅ Pilih v2 jika:
- Ingin ekosistem **Python AI/ML** native (langsung pakai pandas, numpy, scikit-learn di sandbox)
- Butuh **multi-provider failover** dengan 1 SDK (LiteLLM auto-handle Cerebras/Groq/Gemini/Sumopod)
- Mau **agent orkestrasi** state-machine (LangGraph) yang lebih predictable
- Skala laporan kompleks (BAB I–V) dengan **CSS Paged Media** profesional
- Sudah nyaman dengan Python untuk backend

✅ Tetap di blueprint awal jika:
- Lebih nyaman dengan **TypeScript end-to-end**
- Mau **single deployment** unit (Next.js+API routes)
- Tim lebih kuat di Node ekosistem
- Skala awal kecil, **less moving parts** lebih penting
- Sudah mulai coding dengan stack itu

## Daftar Dokumen v2

| File | Topik |
|---|---|
| [`MASTERPLAN.md`](./MASTERPLAN.md) | Entry point ringkas |
| [`01-vision-and-scope.md`](./01-vision-and-scope.md) | Visi, persona, scope |
| [`02-tech-stack.md`](./02-tech-stack.md) | Tech stack lengkap |
| [`03-architecture.md`](./03-architecture.md) | Arsitektur sistem |
| [`04-features-and-user-flows.md`](./04-features-and-user-flows.md) | Fitur + user journey |
| [`05-llm-providers.md`](./05-llm-providers.md) | Multi-LLM strategy |
| [`06-rag-and-knowledge.md`](./06-rag-and-knowledge.md) | RAG & knowledge base |
| [`07-data-analysis-engine.md`](./07-data-analysis-engine.md) | Data engine (Excel/CSV) |
| [`08-report-generation.md`](./08-report-generation.md) | Report PDF generator |
| [`09-data-model-and-api.md`](./09-data-model-and-api.md) | DB schema + API |
| [`10-frontend-design.md`](./10-frontend-design.md) | UI/UX & komponen |
| [`11-agent-skills-and-memory.md`](./11-agent-skills-and-memory.md) | Agent skills + memory |
| [`12-roadmap-and-milestones.md`](./12-roadmap-and-milestones.md) | Roadmap MVP → V2 |
| [`13-deployment-and-ops.md`](./13-deployment-and-ops.md) | Deployment & ops |
| [`14-security-and-compliance.md`](./14-security-and-compliance.md) | Security & privacy |

## Cara Decide

1. Baca [`MASTERPLAN.md`](./MASTERPLAN.md) v2 (~5 menit)
2. Compare dengan [`../BLUEPRINT.md`](../BLUEPRINT.md) lama (~5 menit)
3. Cek [`02-tech-stack.md`](./02-tech-stack.md) v2 vs [`../TECHSTACK.md`](../TECHSTACK.md) lama
4. Putuskan: keep lama, pakai v2, atau hybrid

> Tip: Hybrid juga valid, contoh ambil **LiteLLM + LangGraph + LlamaIndex** dari v2 tapi tetap **Next.js + Prisma + Recharts** dari blueprint awal.
