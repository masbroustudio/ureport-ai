# 08 — Report Generation (PDF dengan struktur BAB)

## 8.1 Tujuan

User minta laporan → AI menghasilkan **PDF berstruktur** lengkap:
- Cover (judul, penulis, tanggal, logo)
- Kata Pengantar (opsional)
- Daftar Isi (auto-generate dari heading)
- BAB I Pendahuluan
- BAB II Tinjauan Pustaka / Landasan Teori
- BAB III Metodologi
- BAB IV Pembahasan / Analisa
- BAB V Kesimpulan & Saran
- Daftar Pustaka
- Lampiran (tabel raw, kode)

Struktur **fleksibel** — user bisa override jumlah BAB & section.

---

## 8.2 Pipeline Report Generation

```
[1] User trigger generate report
    - dari conversation aktif (auto-collect file & chat history)
    - atau dari menu khusus "New Report"
       │
       ▼
[2] Planner LLM (Gemini 2.0 Flash, long-context)
    Input: user request + profile data + dokumen RAG yg dipilih
    Output: outline JSON
       │
       ▼
[3] Outline review modal (user approve/edit)
       │
       ▼
[4] Dispatch Celery task (background)
       │
       ▼
[5] Untuk tiap section:
       a) Retrieve konteks (RAG search)
       b) Run data tool (jika butuh chart/tabel)
       c) Writer LLM (Cerebras 70B) draft section
       d) Editor LLM (Gemini Flash) polish & cek koherensi
       │
       ▼
[6] Compile master Markdown + asset (chart PNG, tabel)
       │
       ▼
[7] Render: Markdown → HTML (Jinja2 template) → PDF (WeasyPrint)
       │
       ▼
[8] Upload PDF ke S3, push notif ke FE (SSE/Webhook)
       │
       ▼
[9] User preview & download
```

---

## 8.3 Outline JSON Schema

```json
{
  "id": "rpt_01H...",
  "title": "Analisa Penjualan Q1 2026 — Toko ABC",
  "subtitle": "Periode 1 Jan – 31 Mar 2026",
  "author": "Sarah W.",
  "organization": "Toko ABC",
  "date": "2026-04-05",
  "language": "id",
  "template": "business_report_v1",
  "branding": {
    "logo_url": "s3://...",
    "primary_color": "#1F4E8C"
  },
  "chapters": [
    {
      "id": "ch1",
      "number": "BAB I",
      "title": "Pendahuluan",
      "sections": [
        {
          "id": "s1.1",
          "title": "Latar Belakang",
          "instruction": "Jelaskan konteks bisnis & tujuan laporan",
          "use_rag": true,
          "use_data": false,
          "target_words": 250
        },
        { "id": "s1.2", "title": "Tujuan", "instruction": "...", "target_words": 150 },
        { "id": "s1.3", "title": "Ruang Lingkup", "...": "..." }
      ]
    },
    {
      "id": "ch4",
      "number": "BAB IV",
      "title": "Pembahasan",
      "sections": [
        {
          "id": "s4.1",
          "title": "Top Produk Terlaris",
          "use_data": true,
          "data_request": {
            "files": ["file_123"],
            "task": "Top 10 produk by revenue, dengan bar chart"
          },
          "target_words": 300
        }
      ]
    },
    { "id": "ch5", "number": "BAB V", "title": "Kesimpulan & Saran", "sections": [...] }
  ],
  "references": "auto",
  "appendix": ["raw_table_full"]
}
```

---

## 8.4 Template Library

Template ditulis sebagai **Jinja2 + CSS**. Default templates:

| ID | Nama | Cocok Untuk |
|---|---|---|
| `business_report_v1` | Laporan Bisnis | Penjualan, marketing, operasional |
| `academic_thesis_v1` | Skripsi/Tesis | Akademik formal |
| `research_paper_v1` | Paper Riset | Jurnal sederhana |
| `market_research_v1` | Riset Pasar | Survey, analisa kompetitor |
| `executive_summary_v1` | Ringkasan Eksekutif | 2–4 halaman, untuk pimpinan |

Struktur folder:
```
apps/api/app/report/templates/
├── business_report_v1/
│   ├── layout.html.j2
│   ├── cover.html.j2
│   ├── toc.html.j2
│   ├── chapter.html.j2
│   ├── styles.css
│   └── meta.yaml
└── ...
```

`meta.yaml`:
```yaml
id: business_report_v1
name: "Laporan Bisnis"
description: "Template formal untuk laporan operasional bisnis"
default_chapters:
  - "Pendahuluan"
  - "Metodologi"
  - "Pembahasan"
  - "Kesimpulan & Saran"
fonts: ["Inter", "Source Serif Pro"]
page_size: A4
margins: {top: 25mm, bottom: 25mm, left: 30mm, right: 25mm}
```

---

## 8.5 HTML → PDF dengan WeasyPrint

WeasyPrint mendukung CSS Paged Media penuh:
- `@page` rules (margin, size)
- Page break `break-before: page`
- Running header/footer (`@page :first`, `@page main`)
- Auto page numbering (`counter(page)`)
- TOC otomatis dari `target-counter()`

### Contoh CSS
```css
@page {
  size: A4;
  margin: 25mm 25mm 30mm 25mm;
  @bottom-center { content: counter(page) " / " counter(pages); }
  @top-right { content: string(report-title); font-size: 9pt; color: #888; }
}
@page :first { @top-right { content: none; } @bottom-center { content: none; } }

h1.chapter { string-set: report-title content(); break-before: page; }
.toc a::after { content: leader('.') target-counter(attr(href), page); }
```

Library wrapper: pakai **`weasyprint`** Python, atau **Paged.js** kalau mau render di FE.

---

## 8.6 Penyusunan Konten Per Section

Algoritma agent untuk tiap section:

```python
def write_section(section: Section, ctx: ReportContext) -> str:
    materials = []

    if section.use_rag:
        chunks = rag.search(query=section.instruction, kb_id=ctx.kb_id, top_k=8)
        materials += [c.text for c in chunks]

    if section.use_data:
        result = data_engine.run(section.data_request)
        materials.append(format_table(result.table))
        if result.chart:
            ctx.charts.append(result.chart)
            materials.append(f"[chart:{result.chart.id}]")

    prompt = WRITER_PROMPT.format(
        section_title=section.title,
        instruction=section.instruction,
        target_words=section.target_words,
        materials="\n\n".join(materials),
        language=ctx.language,
    )
    draft = llm.complete(prompt, model="cerebras/llama-3.3-70b")
    return draft
```

---

## 8.7 Citations & References

- Setiap fakta dari RAG: tandai dengan `[^id]`
- Saat compile: kumpulkan semua `[^id]` unik → generate Daftar Pustaka section dengan style **APA 7** (default), Vancouver, Chicago (opsional)
- Auto-detect jika user dokumen punya metadata (judul, penulis, tahun) — kalau tidak, ambil dari nama file & first page heuristik.

---

## 8.8 Asset Embedding

| Asset | Cara |
|---|---|
| Chart (Plotly) | Render ke PNG via Kaleido (server-side) → embed sebagai `<img>` |
| Tabel | Render sebagai `<table>` HTML, styled dengan Tailwind-like CSS |
| Logo | Inline base64 di HTML untuk reproducibility offline |
| Font | Embed di PDF via `@font-face` |

---

## 8.9 Async Job Status

Status laporan disimpan di Postgres + Redis:

```
created → planning → outline_ready → writing (3/12) → rendering → done | failed
```

API:
- `POST /api/reports` → buat job
- `GET /api/reports/{id}` → status & metadata
- `GET /api/reports/{id}/outline` → outline JSON
- `PUT /api/reports/{id}/outline` → user edit
- `POST /api/reports/{id}/start` → start writing
- `GET /api/reports/{id}/sse` → stream progress
- `POST /api/reports/{id}/regenerate-section` → ulang 1 section
- `GET /api/reports/{id}/pdf` → download URL

---

## 8.10 Editing Setelah Generate

User bisa:
- Klik section di outline → edit instruksi → "Regenerate this section"
- Edit Markdown manual → re-render PDF (skip LLM)
- Tambah/hapus section dinamis

Kita simpan **Markdown master** di Postgres (atau S3) supaya non-LLM re-render cepat.

---

## 8.11 Cost Estimate Per Laporan

| Komponen | Estimasi |
|---|---|
| Planner (1 call, ~3K tokens) | $0.005 |
| Writer (12 section x 2K tokens) | $0.05 |
| Editor (12 section x 1K tokens) | $0.02 |
| RAG search (12x) | < $0.01 |
| Data engine | tergantung |
| **Total laporan ~15 halaman** | **~$0.10** |

Dengan Groq/Gemini Flash, bisa lebih murah lagi.

---

## 8.12 QA Checklist Laporan

Sebelum render PDF, jalankan auto-check:
- ✅ Tidak ada placeholder `[TODO]` / `{{var}}`
- ✅ Setiap claim numerik bisa di-trace ke data atau RAG
- ✅ Sitasi konsisten (no broken `[^id]`)
- ✅ Daftar isi cocok dengan heading
- ✅ Tidak ada gambar pecah / tabel overflow halaman

---

## 8.13 Roadmap Report Engine

| Fase | Fitur |
|---|---|
| MVP | Outline → write → PDF (1 template `business_report_v1`) |
| V1 | 5 template, branding, citation APA, edit ulang |
| V2 | Collaborative editing, version history, DOCX export, Google Slides export |
| V3 | Multi-language report, voice narration, animated chart (HTML output) |
