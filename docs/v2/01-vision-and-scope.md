# 01 — Vision & Scope

## 1.1 Visi

> **uReport AI memberdayakan siapapun untuk berbicara dengan data mereka dan menghasilkan laporan profesional dalam hitungan menit, bukan hari.**

uReport AI adalah asisten AI yang menggabungkan tiga peran sekaligus:

1. **Conversational Assistant** — seperti ChatGPT
2. **Data Analyst** — meramu data Excel/CSV menjadi insight
3. **Report Writer** — menulis laporan formal berstruktur BAB dalam PDF

---

## 1.2 Problem yang Diselesaikan

| Masalah Saat Ini | Solusi uReport AI |
|---|---|
| Analisa Excel butuh waktu & skill (pivot, formula, chart) | Cukup chat: *"tunjukkan tren penjualan per region 6 bulan terakhir"* |
| Bikin laporan formal (skripsi, laporan keuangan, riset) makan waktu berhari-hari | AI generate draft lengkap dengan BAB I–V plus tabel & grafik |
| Pakai ChatGPT/Gemini biasa: konteks terbatas, tidak bisa pakai data internal | RAG dengan knowledge base sendiri |
| Vendor-lock ke 1 LLM, mahal & rentan downtime | Multi-LLM (Cerebras, Groq, Gemini, Sumopod) dengan fallback otomatis |
| Tools data analysis (Tableau, PowerBI) mahal & kurva belajar curam | Cukup ngobrol bahasa natural |

---

## 1.3 Target User

### Primary
- **Mahasiswa & peneliti** — laporan riset, skripsi, tugas akhir
- **Analis data junior/menengah** — eksplorasi cepat data internal
- **Manajer & pimpinan UKM** — laporan operasional, penjualan, marketing tanpa staf khusus
- **Konsultan & freelancer** — bikin laporan klien lebih cepat

### Secondary
- Instansi pemerintah (laporan rutin)
- Tim BI/analytics yang butuh quick draft

---

## 1.4 Persona Singkat

**Persona 1 — "Manajer Toko"**
> Bu Sarah, 38, pemilik 3 toko offline. Tiap akhir bulan harus bikin laporan penjualan untuk dievaluasi. Tidak paham pivot table. Punya export Excel dari kasir.
>
> ✅ Upload `penjualan-feb.xlsx` → minta "Buat laporan penjualan bulanan, fokus produk terlaris dan jam ramai" → dapat PDF lengkap.

**Persona 2 — "Mahasiswa Tugas Akhir"**
> Andi, 21, sedang riset survei UMKM. Punya CSV 500 responden dan beberapa jurnal PDF.
>
> ✅ Upload data + jurnal ke knowledge base → minta "Buat BAB IV pembahasan dengan analisa korelasi modal vs omzet, rujuk literatur yang ada" → dapat draft BAB siap revisi.

**Persona 3 — "Analis Junior"**
> Rina, 25, baru kerja. Disuruh bos cari anomali di data transaksi.
>
> ✅ Upload CSV → "Cari outlier transaksi, segmentasi by customer, tampilkan heatmap" → langsung dapat chart interaktif.

---

## 1.5 Scope (V1 / MVP)

### ✅ In Scope
- Akun & autentikasi (email + Google OAuth)
- Multi-conversation chat seperti ChatGPT
- Pemilihan provider/model (Cerebras, Groq, Gemini, Sumopod)
- Streaming response
- Upload file: `.xlsx`, `.xls`, `.csv`, `.pdf`, `.docx`, `.txt`
- Data analyst mode: tabel, summary stat, grafik (Plotly)
- Report mode: PDF dengan template BAB standar
- Knowledge base personal (per user) untuk RAG
- History percakapan
- Export chat ke Markdown/PDF

### ❌ Out of Scope (V1)
- Kolaborasi real-time multi-user di 1 chat
- Plugin/marketplace third-party
- Mobile native app (cukup PWA dulu)
- Voice input/output
- Fine-tuning model sendiri
- Realtime data source (database connection langsung) — V2
- Workflow automation / scheduling — V2

---

## 1.6 Success Metrics

| Metric | Target MVP |
|---|---|
| Time to first insight (dari upload → jawaban pertama) | < 30 detik |
| Time to generate report 10 halaman | < 3 menit |
| User retention 7-day | > 30% |
| Cost per active user / bulan | < $1 (rata-rata) |
| Akurasi analisa numerik (vs hand-check) | > 95% |

---

## 1.7 Asumsi Kritikal

1. User bersedia upload data ke server kita (perlu trust + clear privacy policy).
2. Provider LLM (Cerebras/Groq/Gemini/Sumopod) tetap accessible & affordable.
3. Sandboxing eksekusi kode aman & cepat (< 5 detik per cell biasa).
4. Mayoritas file user < 50MB (di luar itu masuk premium tier nanti).
