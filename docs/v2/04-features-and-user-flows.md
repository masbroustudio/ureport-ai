# 04 — Features & User Flows

## 4.1 Daftar Fitur

### A. Core
1. **Sign up / sign in** (email+password, Google OAuth)
2. **Workspace chat** (mirip ChatGPT: sidebar conversation, new chat, rename, delete)
3. **Multi-LLM provider switch** (dropdown: Cerebras, Groq, Gemini, Sumopod, + auto)
4. **Streaming response**
5. **Markdown rendering** (code block, table, math, mermaid)
6. **Persistensi history**

### B. File & Data
7. **Upload file** (drag-drop / click): xlsx, xls, csv, pdf, docx, txt, gambar (V2)
8. **File preview** di sidebar (sample 100 baris, schema, missing values)
9. **Data analyst chat**: ask pertanyaan tentang file → AI jawab dengan teks + tabel + grafik
10. **Code interpreter visible** (toggle "show code" untuk transparansi)

### C. Knowledge & RAG
11. **Personal knowledge base**: user bisa upload doc referensi sekali, jadi konteks chat berikutnya
12. **Citation** otomatis di jawaban (dari dokumen mana)
13. **Tagging & folder** untuk organize knowledge

### D. Report Generator
14. **One-click report** dari conversation/file → "Generate Report"
15. **Custom outline**: user atur BAB & section sebelum dijalankan
16. **Template laporan**: Akademik, Bisnis, Penjualan, Riset Pasar, Skripsi
17. **Branding** (logo, judul, nama, footer)
18. **Preview PDF in-browser**, download, share-link
19. **Edit setelah generate**: regenerate per section

### E. Productivity
20. **Prompt library** (template pertanyaan analisa siap pakai)
21. **Export chat** (Markdown, PDF)
22. **Search** di seluruh history
23. **Pin pesan / bookmark**

### F. Admin (V2)
24. **Tim & sharing** (multi-user workspace)
25. **Billing & quota**
26. **Audit log**

---

## 4.2 User Journey

### Journey 1 — First-time User Bikin Laporan Penjualan

```
[Sign up] → onboarding singkat (3 slide) →
[New chat] → upload sales-q1.xlsx
   ↓
AI auto-summary: "Saya melihat 5 kolom: Tanggal, Produk, Region, Qty, Revenue.
                   1.245 baris, periode 1 Jan – 31 Mar 2026.
                   Mau saya analisa apa?"
   ↓
User: "Top 5 produk by revenue, tren mingguan, dan rekomendasi"
   ↓
AI: tampilkan tabel + 2 chart + 3 bullet rekomendasi
   ↓
User klik tombol [Generate Report] di toolbar
   ↓
Modal: pilih template "Laporan Penjualan Bulanan"
       + edit outline (drag-drop BAB)
       + branding (upload logo)
   ↓
[Generate] → progress bar (BAB 1/5 ... done)
   ↓
PDF preview tampil → download → share link
```

### Journey 2 — Mahasiswa Tugas Akhir

```
Setup once:
  [Knowledge base] → upload 10 jurnal PDF + folder "Riset UMKM"
   ↓
  AI ingest → tag otomatis + ringkasan tiap jurnal

Workflow tiap kali:
  [New chat] → "Bantu tulis BAB 2 Tinjauan Pustaka tentang akses modal UMKM
              di Indonesia, rujuk dari knowledge base 'Riset UMKM'"
   ↓
  AI retrieve top 8 pasase relevan → tulis 4 paragraf + sitasi nomor
   ↓
  User: "Tambah pembahasan tentang fintech lending"
   ↓
  AI extend, citation ter-update
   ↓
  Export → DOCX (untuk diedit di Word)
```

### Journey 3 — Quick Analyst

```
Drag CSV → [New chat] (auto-attach)
   ↓
"Cari outlier kolom 'amount' pakai IQR. Visualisasi boxplot per kategori."
   ↓
AI: kode + boxplot interaktif + insight 3 bullet
   ↓
"Sekarang segmentasi customer pake K-Means k=4, tampilkan scatter PC1 vs PC2"
   ↓
AI: kode + chart + interpretasi tiap cluster
   ↓
[Pin] kedua jawaban → siap untuk meeting
```

---

## 4.3 Flow Detail Per Mode

### Mode 1 — General Chat
**Trigger**: tidak ada file attached & query bersifat umum.
**Pipeline**:
1. Klasifikasi intent → "general"
2. Retrieve memory user (fakta personal, preferensi)
3. LLM call (default: Groq llama-3.3-70b — cepat & murah)
4. Stream response
5. Persist

### Mode 2 — Data Analyst
**Trigger**: ada file data attached atau user ref ke data sebelumnya.
**Pipeline**:
1. Auto-profile: schema, dtype, head, describe
2. LLM call ke "code generator" model (Cerebras llama-3.3-70b)
3. Sandbox eksekusi
4. Result enrichment (LLM tulis penjelasan natural)
5. Stream: text + table_id + chart_id
6. FE fetch detail tabel/chart by id

### Mode 3 — Report Generator
**Trigger**: user klik tombol "Generate Report" atau prompt eksplisit.
**Pipeline** (async):
1. **Planner LLM** → outline JSON (interaktif: user bisa edit)
2. **Researcher** (per section): retrieve RAG + query data engine
3. **Writer LLM** → draft section
4. **Editor LLM** → polish & koherensi (opsional)
5. **Renderer** → HTML → PDF
6. **Notify** user (toast + email opsional)

---

## 4.4 Interaksi UI Penting

### Sidebar Conversation
- Group: Today / Yesterday / Last 7 days / Older
- Search box di atas
- Tombol "+ New chat"

### Chat composer
- Textarea autoresize
- Tombol attach file (multi-file)
- Dropdown model (default: Auto)
- Tombol "Generate Report" muncul jika ada file/data context

### Message bubble
- Avatar AI/user
- Tab: **Answer** | **Sources** | **Code** | **Data**
- Tombol: Copy, Regenerate, Continue, Pin

### Chart viewer
- Plotly interactive
- Tombol: Download PNG/SVG, Open in fullscreen, Re-prompt

### File panel (kanan, retractable)
- List file di conversation
- Klik file → preview tabel (DataGrid) + stats

### Report editor
- Outline tree di kiri
- Editor (markdown) + preview di tengah
- Tombol "Regenerate this section" per section
- Tombol "Export" → PDF, DOCX

---

## 4.5 Empty States & Onboarding

- **Empty chat**: tampilkan **prompt suggestions** kontekstual:
  - "Upload Excel & minta saya analisa"
  - "Bikin laporan penjualan dari data ini"
  - "Bandingkan 2 dataset"
  - "Eksplorasi statistik dasar"
- **Onboarding 3-step** (slide modal):
  1. Pilih provider LLM default
  2. Connect knowledge base (skip ok)
  3. Try sample data (kita siapkan `sample_sales.csv`)

---

## 4.6 Edge Cases yang Harus Ditangani

| Kasus | Behavior |
|---|---|
| File > 50MB | Tolak di UI, sarankan sample |
| File rusak | Pesan jelas + saran fix |
| Sandbox timeout | Tampilkan error + tawarkan retry dengan model lain |
| LLM rate limit | Auto-fallback ke provider lain |
| User offline saat generate report | Job tetap jalan, notifikasi saat user online |
| Bahasa campuran (id+en) | LLM harus support, default reply ikut bahasa user |
| PII di data | Warning sebelum upload, tawarkan auto-mask (V2) |
