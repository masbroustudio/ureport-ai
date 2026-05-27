---
inclusion: always
---

# uReport AI — Product Steering

> **Catatan**: Repo ini punya 2 set dokumentasi blueprint:
> - `docs/` (root) — blueprint awal (Next.js + Prisma + pgvector + Recharts + Puppeteer stack)
> - `docs/v2/` — blueprint alternatif yang lebih AI-native (FastAPI + Qdrant + Plotly + WeasyPrint + LiteLLM stack)
>
> Lihat `docs/v2/README.md` untuk perbandingan. Belum ada keputusan final — Kiro harus tanya user dulu sebelum mulai coding.

## Apa itu uReport AI

uReport AI adalah aplikasi chat AI multi-LLM yang fokus pada **analisa data** dan **generasi laporan PDF berstruktur BAB**. Layaknya ChatGPT/Gemini/Claude, tapi:

uReport AI adalah aplikasi chat AI multi-LLM yang fokus pada **analisa data** dan **generasi laporan PDF berstruktur BAB**. Layaknya ChatGPT/Gemini/Claude, tapi:

1. **Mode 1 — Smart Chat**: chat biasa, multi-provider (Cerebras, Groq, Gemini, Sumopod).
2. **Mode 2 — Data Analyst**: user upload Excel/CSV, AI jawab dengan insight, tabel, dan grafik.
3. **Mode 3 — Report Generator**: AI bikin laporan PDF lengkap dengan struktur BAB I–V plus Daftar Pustaka, dibantu RAG dari knowledge base user.

## Target User
- Mahasiswa & peneliti (skripsi, jurnal)
- Manajer/UKM (laporan operasional)
- Analis junior/menengah
- Konsultan & freelancer

## Bahasa
- **Bahasa Indonesia** adalah bahasa default produk & dokumentasi.
- AI harus tetap bisa balas dalam Bahasa Inggris jika user pakai Bahasa Inggris.

## Prinsip Produk
1. **Familiar UX** — mirip ChatGPT, kurva belajar minimum.
2. **Transparan** — selalu kasih lihat sumber & kode (toggle).
3. **Privacy-first** — file user tidak dikirim utuh ke LLM, hanya profile + sample.
4. **Multi-provider** — tidak vendor-lock; auto-fallback saat provider down.
5. **Cost-aware** — routing per task type, budget cap per user.

## Out of Scope (MVP)
- Kolaborasi real-time multi-user
- Mobile native app
- Voice I/O
- Connection langsung ke database produksi (V2)
- Plugin marketplace (V2)

## Success Metrics MVP
- Time to first insight < 30 detik
- Time to PDF report 10 halaman < 3 menit
- Cost per active user < $1/bulan
- 7-day retention > 30%

## Referensi Lengkap
Lihat `MASTERPLAN.md` dan folder `docs/` di root repo.
