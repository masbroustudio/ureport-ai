# 06 — RAG & Knowledge Base

## 6.1 Tujuan RAG di uReport AI

1. **Memberi konteks domain** — user bisa upload SOP, jurnal, regulasi, data perusahaan, lalu chat & laporan akan refer ke sini.
2. **Cita pustaka otomatis** — saat menulis BAB tinjauan pustaka.
3. **Memori jangka panjang user** (lihat `docs/11-agent-skills-and-memory.md`).

---

## 6.2 Arsitektur RAG

```
        User upload doc (.pdf/.docx/.txt)
                  │
                  ▼
    ┌──────────────────────────────┐
    │   Loader (LlamaIndex Reader) │
    │   PyMuPDF, python-docx, etc  │
    └──────────────┬───────────────┘
                   ▼
    ┌──────────────────────────────┐
    │   Cleaner & Normalizer       │
    │   - dedupe whitespace        │
    │   - drop boilerplate         │
    │   - language detect          │
    └──────────────┬───────────────┘
                   ▼
    ┌──────────────────────────────┐
    │   Chunker                    │
    │   semantic + sliding window  │
    └──────────────┬───────────────┘
                   ▼
    ┌──────────────────────────────┐
    │   Embedder                   │
    │   bge-m3  (default)          │
    │   gemini  (premium)          │
    └──────────────┬───────────────┘
                   ▼
    ┌──────────────────────────────┐
    │   Store: Qdrant collection   │
    │   per user / per workspace   │
    │   payload = {chunk, meta}    │
    └──────────────────────────────┘

  Query → embed → top-K → rerank (BGE-reranker) → context
```

---

## 6.3 Document Loaders

| Format | Library | Catatan |
|---|---|---|
| PDF | `pymupdf` (cepat, bagus utk teks) atau `unstructured` (bagus utk layout kompleks) | Default: pymupdf; fallback: unstructured |
| DOCX | `python-docx` atau LlamaIndex `DocxReader` | |
| XLSX/CSV | pandas; tiap sheet jadi 1 dokumen, baris dirangkum | Lihat §6.6 |
| TXT/MD | built-in | |
| HTML | `trafilatura` atau `readability-lxml` | |
| PPTX | `python-pptx` (V2) | |
| Image (OCR) | `pytesseract` (V2) | |

---

## 6.4 Chunking Strategy

### Default: Semantic + Sliding Window
- Chunk size target: **512–800 tokens**
- Overlap: **15%**
- Pisahkan di **boundary natural** (paragraf/heading), bukan di tengah kalimat.
- Library: `llama-index` `SemanticSplitterNodeParser` atau `tiktoken-based RecursiveCharacterTextSplitter`.

### Khusus dokumen panjang (>50 halaman)
- Dua-level: **summary chunk per bab** + **detail chunks**
- Saat retrieval: cari summary dulu, expand ke detail relevan (hierarchical retrieval)

### Khusus tabular (Excel/CSV) yang dimasukkan ke knowledge
- Tiap sheet → header + sample 5 baris + statistik (`describe`)
- Ditambah natural-language description (LLM-generated): *"Sheet 'Penjualan' berisi 1.245 transaksi periode Jan–Mar 2026 dengan kolom..."*
- Embed text description, bukan raw row.

---

## 6.5 Embedding

| Model | Dim | Multilingual | Speed | Cost |
|---|---|---|---|---|
| `bge-m3` (lokal) | 1024 | ✅ (id+en kuat) | sedang (CPU bisa, GPU 5x cepat) | gratis |
| `gemini text-embedding-004` | 768 | ✅ | cepat (API) | $0.02/1M tokens |

**Rekomendasi**: bge-m3 default, Gemini premium toggle.

Implementasi lokal:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-m3")
vectors = model.encode(chunks, normalize_embeddings=True)
```

---

## 6.6 Vector Store: Qdrant

### Collection scheme
- 1 **collection per workspace** (atau per user di V1).
- Nama: `kb_{workspace_id}`
- Vector size: 1024 (bge-m3) atau 768 (gemini)

### Payload (metadata) wajib disimpan
```json
{
  "chunk_id": "uuid",
  "doc_id": "uuid",
  "doc_name": "JUKNIS-2024.pdf",
  "doc_type": "pdf",
  "page": 12,
  "section": "Bab III",
  "chunk_index": 47,
  "tags": ["regulasi", "umkm"],
  "language": "id",
  "uploaded_at": "2026-05-27T10:30:00Z",
  "text": "isi chunk lengkap untuk display"
}
```

### Filtering saat retrieval
- Filter `doc_id IN [...]` jika user pilih dokumen spesifik.
- Filter `tags` jika user organize folder.
- Filter `language` jika diperlukan.

---

## 6.7 Retrieval Pipeline

```python
def retrieve(query: str, kb_id: str, top_k: int = 8) -> list[Chunk]:
    # 1. Query expansion (opsional): LLM rewrite query jadi 2-3 paraphrase
    queries = [query] + llm_paraphrase(query, n=2)

    # 2. Embed
    qvecs = embed(queries)

    # 3. Hybrid search (dense + BM25 keyword) di Qdrant
    candidates = qdrant.search(kb_id, vectors=qvecs, top_k=20)

    # 4. Rerank dengan cross-encoder (bge-reranker-v2-m3)
    reranked = rerank(query, candidates)[:top_k]

    return reranked
```

### Reranker
- Model: `BAAI/bge-reranker-v2-m3` (lokal)
- Boost relevansi 20–40% vs pure dense retrieval.

---

## 6.8 Synthesizer (Generate Answer)

Strategi yang dipakai:

### A. **Compact** (default untuk chat)
- Concat context → 1 prompt → 1 LLM call.
- Cocok jika total context < 8K tokens.

### B. **Refine** (untuk laporan panjang)
- Iteratif: jawaban awal → refine dengan chunk berikutnya.
- Cocok untuk synthesize >10 chunk.

### C. **Tree-summarize**
- Summarize per chunk → summarize gabungan.
- Cocok untuk QA dokumen sangat panjang.

LlamaIndex menyediakan ketiga strategi ini built-in.

---

## 6.9 Citation Strategy

Setiap kalimat output yang merujuk dokumen akan di-tag dengan ID chunk:

```
"Penyaluran KUR mikro tahun 2024 mengalami kenaikan 12% [^1][^2]."

[^1]: JUKNIS-2024.pdf, hal. 12
[^2]: BPS-Riset-UMKM-2024.pdf, hal. 5
```

Frontend render footnote sebagai badge yang clickable → buka modal dengan teks chunk asli.

---

## 6.10 Lifecycle Document

| Aksi | Behavior |
|---|---|
| Upload | Dispatch ke Celery → ingest async, status `processing` |
| Proses selesai | Status `ready`, user bisa pakai |
| Update doc | Re-ingest, hapus chunk lama, insert baru |
| Delete | Hapus dari Qdrant + S3 + Postgres metadata |
| Re-embed (ganti model) | Bulk job ulangi embedding seluruh chunk |

---

## 6.11 Performance & Cost

- Cache hasil retrieval untuk query identik (Redis, TTL 5 menit).
- Limit maksimum dokumen per workspace MVP: **100 file** atau **500 MB total**.
- Indexing time target: < 30 detik per 100 halaman.
- Retrieval latency target: < 300 ms untuk 1 collection.

---

## 6.12 Tools API yang Diekspos ke Agent

```python
@tool
def search_knowledge_base(query: str, kb_id: str, top_k: int = 8) -> list[Chunk]:
    """Cari potongan dokumen relevan dari knowledge base user."""

@tool
def list_documents(kb_id: str, tag: str | None = None) -> list[DocMeta]:
    """List dokumen yg tersedia di knowledge base."""

@tool
def get_document_summary(doc_id: str) -> str:
    """Ambil ringkasan otomatis sebuah dokumen."""
```

---

## 6.13 Quality Evaluation (later)

Saat MVP+ stabil, pasang eval pipeline:
- Dataset internal: 50 query + jawaban gold standard
- Metric: hit-rate@k, MRR, faithfulness (LLM-as-judge dari Gemini)
- Run nightly setelah change ke pipeline.
