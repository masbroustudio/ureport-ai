# 07 — Data Analysis Engine

> Komponen ini membuat AI mampu **membaca, memahami, dan menganalisa file Excel/CSV** seperti seorang data analyst.

---

## 7.1 Tujuan

User upload `.xlsx`/`.csv` → AI bisa:
- Profil otomatis (schema, missing, dtypes)
- Statistik deskriptif & insight
- Filter, group-by, pivot
- Korelasi, distribusi, tren waktu
- Outlier detection, segmentasi (clustering)
- Visualisasi: bar, line, pie, scatter, heatmap, boxplot
- Generate kode Python yang bisa dilihat user (transparansi)

---

## 7.2 Pipeline End-to-End

```
[1] Upload file (.xlsx/.csv)
      │
      ▼
[2] Validasi & sanitasi
      - cek MIME, ukuran, malware-scan (clamav opsional)
      - simpan blob ke S3
      - extract metadata (nama sheet, ukuran)
      │
      ▼
[3] Auto-profiling (sync, < 3 detik)
      - load via pandas
      - schema, dtypes, n_rows, n_cols
      - missing %, unique counts
      - first 100 rows sample
      - simpan profile JSON di Postgres
      │
      ▼
[4] User chat dengan referensi file
      "Tampilkan top 5 produk by revenue, plus chart"
      │
      ▼
[5] Agent decide tool: run_python(file_id, instruction)
      │
      ▼
[6] Code Generator LLM (Cerebras 70B, prompt khusus)
      generate kode pandas + plotly
      │
      ▼
[7] Sandbox eksekusi (E2B atau self-host)
      - timeout 30s
      - capture stdout, return value, plotly fig
      - tidak ada akses internet (kecuali whitelist)
      │
      ▼
[8] Result enrichment
      - tabel → format markdown / JSON
      - chart → Plotly JSON spec
      - LLM tulis penjelasan natural
      │
      ▼
[9] Stream ke user: text + table + chart
```

---

## 7.3 Auto Profiling

Saat file di-upload, langsung jalankan:

```python
def auto_profile(path: str) -> dict:
    df = read_any(path)  # detect xlsx/csv
    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": [
            {
                "name": c,
                "dtype": str(df[c].dtype),
                "missing_pct": df[c].isna().mean(),
                "n_unique": df[c].nunique(),
                "sample_values": df[c].dropna().head(5).tolist(),
                "stats": describe_col(df[c]),  # min/max/mean atau top categories
            }
            for c in df.columns
        ],
        "head_preview": df.head(20).to_dict(orient="records"),
        "memory_mb": df.memory_usage(deep=True).sum() / 1e6,
    }
```

Profile ini akan **diumpan ke prompt LLM** sebagai konteks (bukan raw data) — hemat token & privacy-friendly.

---

## 7.4 Tools yang Diekspos ke Agent

```python
@tool
def list_files(conversation_id: str) -> list[FileMeta]:
    """List file yang attached di conversation ini."""

@tool
def get_dataframe_profile(file_id: str, sheet: str | None = None) -> Profile:
    """Ambil profile dataframe (schema, stats, sample)."""

@tool
def run_python(file_id: str, code: str, sheet: str | None = None) -> ExecutionResult:
    """
    Eksekusi kode Python dengan dataframe pre-loaded sebagai variable `df`.
    Returns: stdout, stderr, table (jika ada), chart (Plotly JSON), variables yg di-update.
    """

@tool
def make_chart(
    file_id: str,
    chart_type: str,  # bar/line/pie/scatter/heatmap/box
    x: str, y: str | list[str],
    color: str | None = None,
    aggregation: str = "sum",  # sum/mean/count/...
    filters: dict | None = None,
    title: str | None = None,
) -> ChartSpec:
    """
    Helper level tinggi untuk chart umum tanpa user code.
    Lebih reliable & cepat untuk request standar.
    """
```

> **Strategi**: untuk request umum (bar chart sederhana) → pakai `make_chart` (deterministik). Untuk analisa kompleks → `run_python` dengan kode generated.

---

## 7.5 Sandbox Execution

### Pilihan Implementasi

| Pilihan | Pro | Con | Cocok |
|---|---|---|---|
| **E2B Code Interpreter** (managed) | Setup 5 menit, secure, mature | Bayar per detik | MVP & startup |
| **Self-host: Jupyter kernel + nsjail/firejail** | Murah, kontrol penuh | Setup ribet, harus harden | Skala besar |
| **Self-host: gVisor + container per request** | Sangat aman | Overhead start container | Enterprise |
| **Pyodide (FE-side)** | Tanpa server, instan | Subset library, max ~50MB data | Ringan only |

**Rekomendasi**: MVP pakai **E2B**, V2 evaluasi self-host kalau cost tinggi.

### Whitelist Library (sandbox image)
```
pandas, numpy, scipy, scikit-learn, statsmodels,
plotly, matplotlib, seaborn,
openpyxl, xlrd, pyarrow,
nltk (data terpasang), regex,
networkx
```

### Hard Limits
- CPU: 1 core, 2 GB RAM
- Wallclock: 30 detik default (bisa naik 60 detik untuk task ML)
- Disk: 200 MB workspace
- Network: **disabled** (kecuali whitelist domain saat dibutuhkan)

### Security
- Tidak boleh akses filesystem host
- Tidak boleh shell command (`subprocess` di-block)
- Tidak boleh `eval` ke external code
- Output max 1 MB (selain file binary chart)

---

## 7.6 Charting

### Format Standar: Plotly JSON
Backend hasilkan dict Plotly:
```python
import plotly.express as px
fig = px.bar(df, x="product", y="revenue", color="region")
spec = fig.to_dict()  # dict JSON-serializable
```

Frontend render via `react-plotly.js`:
```tsx
<Plot data={spec.data} layout={spec.layout} config={{ responsive: true }} />
```

### Tipe Chart yang Didukung MVP
- Bar, Stacked Bar, Grouped Bar
- Line, Multi-line, Area
- Pie, Donut
- Scatter, Bubble
- Heatmap, Correlation matrix
- Box plot, Violin
- Histogram, Density
- Geo (V2)

### Theme
- Mengikuti palette uReport AI (warna primary)
- Mode terang/gelap mengikuti UI
- Font: sama dengan font app (Inter / system)

---

## 7.7 Prompt untuk Code Generator (sketsa)

```
SYSTEM:
Anda adalah data analyst Python expert. Tugas Anda generate kode pandas + plotly
yang menjawab pertanyaan user terhadap dataframe `df`.

ATURAN:
- Selalu tulis komentar singkat di tiap blok.
- Selalu return: tabel dengan `result_table = df_xxx`, dan/atau chart dengan `fig = ...`.
- Variable yg di-expose: result_table, fig.
- Jangan pakai `subprocess`, `os.system`, atau IO file di luar `df`.
- Jika perlu agregasi waktu, parse kolom date dengan `pd.to_datetime`.
- Jika ada missing value, sebutkan strategi (drop / fillna).

CONTEXT FILE PROFILE:
{profile_json}

USER QUESTION:
{question}

OUTPUT (kode Python saja, tanpa penjelasan):
```

---

## 7.8 Response Format ke User

Agent merangkai jawaban dengan struktur:

```markdown
## Ringkasan
Top 5 produk by revenue Q1 2026 didominasi oleh kategori Elektronik...

## Tabel
| Produk | Revenue (Rp) | Share |
|---|---|---|
| Laptop X | 1.2M | 23% |
| ... |

[chart:abc-123]

## Insight
- Produk teratas menyumbang 65% total revenue
- Penjualan naik 12% MoM di kuartal ini
- Kategori Fashion tertinggal jauh

> Lihat kode: [show code ▾]
```

`[chart:abc-123]` adalah placeholder yang FE replace dengan komponen Plotly interactive.

---

## 7.9 Caching

- Hash `(file_id, sheet, code)` → simpan hasil di Redis (TTL 1 jam)
- Hindari rerun saat user re-render UI
- Invalidate kalau file di-update

---

## 7.10 Error Handling

| Error | Behavior |
|---|---|
| Kode tidak compile | LLM auto-fix (1 retry) → kalau masih gagal, tampilkan ke user |
| Kolom tidak ada | LLM didorong "fuzzy-match" nama kolom dari profile |
| Timeout | Tampilkan: "Analisa terlalu kompleks, coba sederhanakan" |
| Memory exceed | Sample data → 100K baris → ulang |
| Chart kosong | Beri fallback teks-only summary |

---

## 7.11 Privacy & Data Handling

- File user **tidak pernah dikirim utuh ke LLM** — hanya profile + sample 5–20 baris.
- Jika user meminta "jelaskan baris 1-100", baru kirim lebih banyak (warning ditampilkan).
- File di S3 dienkripsi at-rest (SSE-S3 / SSE-KMS).
- Auto-purge file > 30 hari (kecuali pinned).
- User bisa hapus file kapan saja → cascade delete chunk RAG, cache, dll.

---

## 7.12 Roadmap Data Engine

| Fase | Fitur |
|---|---|
| MVP | Read xlsx/csv, profile, run_python, basic charts, make_chart helper |
| V1 | Multi-file join, scheduled refresh, custom Python lib install per workspace |
| V2 | Connect ke DB (Postgres/MySQL), Google Sheets sync, BI dashboard mode |
| V3 | Auto-ML (anomaly, forecasting), causal inference assistant |
