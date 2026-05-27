# uReport AI - Technical Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Browser - Next.js SSR/CSR]
    end

    subgraph "Frontend Application - Next.js 14+"
        Pages[Pages & Layouts]
        Components[UI Components - shadcn/ui]
        ChatUI[Chat Interface]
        ChartComp[Chart Components - Recharts]
        TableComp[Data Table - TanStack Table]
        FileUpload[File Upload Component]
        ReportView[Report Viewer/Editor]
        MDRenderer[Markdown Renderer]
    end

    subgraph "API Layer - Next.js API Routes"
        AuthAPI[Auth API - NextAuth.js]
        ChatAPI[Chat API - Streaming SSE]
        FileAPI[File Upload API]
        AnalysisAPI[Analysis API]
        ReportAPI[Report Generation API]
        LLMAPI[LLM Provider API]
        RAGAPI[RAG Search API]
    end

    subgraph "LLM Orchestration Layer"
        Router[LLM Router - Strategy Pattern]
        Cerebras[Cerebras Adapter]
        Groq[Groq Adapter]
        Gemini[Gemini Adapter]
        Sumopod[Sumopod Adapter - Custom]
        StreamHandler[Stream Handler]
        PromptManager[Prompt Template Manager]
    end

    subgraph "Python Microservice - FastAPI"
        DataEndpoints[REST Endpoints]
        PandasProc[Pandas Processor]
        ExcelParser[Excel/CSV Parser - openpyxl]
        ChartDataGen[Chart Data Generator]
        StatAnalysis[Statistical Analysis]
        DataCleaner[Data Cleaning Pipeline]
    end

    subgraph "RAG Pipeline"
        DocIngest[Document Ingestion]
        Chunker[Text Chunker]
        Embedder[Embedding Generator]
        VectorSearch[Vector Similarity Search]
        ContextBuilder[Context Builder]
    end

    subgraph "Data & Storage Layer"
        PG[(PostgreSQL 16 + pgvector)]
        Redis[(Redis - Cache & Queue)]
        MinIO[(MinIO/S3 - File Storage)]
        BullMQ[BullMQ Job Queue]
    end

    subgraph "Infrastructure"
        Docker[Docker Compose]
        Nginx[Nginx Reverse Proxy]
        Monitor[Health Monitoring]
    end

    Browser --> Pages
    Pages --> Components
    Components --> ChatUI
    Components --> ChartComp
    Components --> TableComp
    Components --> FileUpload
    Components --> ReportView

    ChatUI --> ChatAPI
    FileUpload --> FileAPI
    ReportView --> ReportAPI
    
    ChatAPI --> Router
    AnalysisAPI --> Router
    ReportAPI --> Router
    
    Router --> Cerebras
    Router --> Groq
    Router --> Gemini
    Router --> Sumopod
    Router --> StreamHandler
    Router --> PromptManager
    
    FileAPI --> DataEndpoints
    AnalysisAPI --> DataEndpoints
    DataEndpoints --> PandasProc
    DataEndpoints --> ExcelParser
    DataEndpoints --> ChartDataGen
    PandasProc --> StatAnalysis
    PandasProc --> DataCleaner

    RAGAPI --> DocIngest
    DocIngest --> Chunker
    Chunker --> Embedder
    Embedder --> PG
    VectorSearch --> PG
    ContextBuilder --> VectorSearch
    Router --> ContextBuilder

    AuthAPI --> PG
    ChatAPI --> PG
    FileAPI --> MinIO
    ReportAPI --> Redis
    ReportAPI --> BullMQ
    BullMQ --> Redis
```

---

## Recommended Tech Stack with Justification

### Frontend

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **Next.js 14/15** | App Router, SSR/SSG, API Routes built-in, excellent DX | Nuxt.js, Remix, SvelteKit |
| **TypeScript** | Type safety, better DX, catch bugs early | JavaScript (plain) |
| **Tailwind CSS** | Utility-first, rapid UI development, consistent styling | Styled Components, CSS Modules |
| **shadcn/ui** | Beautiful, accessible, copy-paste components (not a dependency) | Radix UI, Chakra UI, MUI |
| **Recharts** | React-native charts, declarative, good docs, customizable | Chart.js, Nivo, Victory |
| **TanStack Table** | Headless table, sorting/filtering/pagination built-in | AG Grid, React Table v7 |
| **react-markdown** | Render AI markdown responses safely | marked + DOMPurify |
| **Zustand** | Lightweight state management, simple API | Redux Toolkit, Jotai |

### Backend

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **Next.js API Routes** | Same deployment, no CORS issues, type sharing | Express.js, Fastify |
| **Python FastAPI** | Best for data science (pandas ecosystem), async, fast | Flask, Django |
| **Prisma ORM** | Type-safe DB access, migrations, great DX | Drizzle ORM, TypeORM |
| **NextAuth.js** | Easy auth with multiple providers, session management | Clerk, Auth0, Lucia |
| **WebSocket/SSE** | Real-time streaming responses from LLM | Polling (worse UX) |

### AI/ML Layer

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **Vercel AI SDK** | Unified interface, streaming built-in, multi-provider | LangChain.js, raw fetch |
| **LangChain (Python)** | RAG pipeline, document processing, chain-of-thought | LlamaIndex, Haystack |
| **Cerebras SDK** | Ultra-fast inference for quick responses | - |
| **Groq SDK** | Very low latency, good for interactive chat | - |
| **Google Generative AI** | Multimodal (bisa baca gambar), powerful | - |
| **Sumopod (Custom)** | Kontrol penuh, customizable | - |

### Data Processing

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **pandas** | De facto standard data manipulation, powerful | Polars (faster tapi less mature) |
| **openpyxl** | Read/write Excel files (.xlsx) | xlrd (read-only) |
| **numpy** | Numerical computing, statistics | scipy |
| **matplotlib/plotly** | Server-side chart generation jika needed | seaborn |

### Database & Storage

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **PostgreSQL 16** | Reliable, feature-rich, pgvector extension | MySQL, MongoDB |
| **pgvector** | Vector search dalam PostgreSQL, no extra service | Pinecone, Weaviate, Qdrant |
| **Redis** | Caching, session store, job queue backend | Memcached (no persistence) |
| **MinIO** | S3-compatible, self-hosted file storage | AWS S3, Cloudflare R2 |
| **BullMQ** | Job queue untuk async tasks (PDF generation) | Celery (Python) |

### PDF & Report Generation

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **Puppeteer** | HTML to PDF, full CSS support, accurate rendering | wkhtmltopdf |
| **@react-pdf/renderer** | Programmatic PDF creation dengan React components | PDFKit, jsPDF |

### Infrastructure

| Technology | Alasan Dipilih | Alternatif |
|-----------|----------------|------------|
| **Docker** | Consistent environment, easy deployment | Podman |
| **Docker Compose** | Multi-service orchestration locally | Kubernetes (overkill for start) |
| **Nginx** | Reverse proxy, SSL termination, load balancing | Caddy, Traefik |

---

## Data Flow Diagrams

### 1. Chat Message Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Next.js API
    participant LLM as LLM Router
    participant Provider as Active LLM Provider
    participant DB as PostgreSQL

    User->>Frontend: Ketik pesan + Enter
    Frontend->>API: POST /api/chat/messages (stream: true)
    API->>DB: Simpan message (role: user)
    API->>DB: Ambil conversation history
    API->>LLM: Forward message + context
    LLM->>LLM: Select active provider
    LLM->>Provider: Send prompt + history
    
    loop Streaming Response
        Provider-->>LLM: Token chunk
        LLM-->>API: Forward chunk
        API-->>Frontend: SSE event: chunk
        Frontend-->>User: Render token by token
    end
    
    Provider-->>LLM: [DONE]
    LLM-->>API: Stream complete
    API->>DB: Simpan message (role: assistant)
    API-->>Frontend: SSE event: done
    Frontend-->>User: Response complete
```

### 2. File Upload + Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Next.js API
    participant Storage as MinIO/S3
    participant Python as FastAPI Service
    participant LLM as LLM Router
    participant DB as PostgreSQL

    User->>Frontend: Drag & Drop file Excel/CSV
    Frontend->>Frontend: Validate file (type, size)
    Frontend->>API: POST /api/files/upload (multipart/form-data)
    API->>Storage: Upload file binary
    Storage-->>API: File URL/key
    API->>Python: POST /parse (file_url)
    
    Python->>Storage: Download file
    Python->>Python: pandas.read_excel() / read_csv()
    Python->>Python: Generate schema info
    Python->>Python: Generate preview (first 10 rows)
    Python->>Python: Basic statistics (describe())
    Python-->>API: {schema, preview, stats, row_count, col_count}
    
    API->>DB: Save attachment metadata + schema
    API-->>Frontend: {file_id, preview, schema, stats}
    Frontend-->>User: Show data preview + "Ask anything about this data"

    Note over User, DB: User asks a question about the data
    
    User->>Frontend: "Berapa rata-rata penjualan per kategori?"
    Frontend->>API: POST /api/chat/messages {message, file_id}
    API->>Python: POST /analyze {file_url, query}
    Python->>Python: pandas query/groupby/aggregate
    Python-->>API: {result_data, suggested_chart_type}
    API->>LLM: "Explain this data result: {result_data}"
    LLM-->>API: Natural language explanation (streaming)
    API-->>Frontend: {explanation_stream, table_data, chart_config}
    Frontend-->>User: Tampilkan tabel + chart + penjelasan AI
```

### 3. Chart Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Next.js API
    participant Python as FastAPI
    participant LLM as LLM Router

    User->>Frontend: "Buatkan pie chart penjualan per region"
    Frontend->>API: POST /api/chat/messages
    API->>LLM: Analyze intent: chart generation
    LLM-->>API: {intent: "chart", chart_type: "pie", dimensions: ["region"], metrics: ["penjualan"]}
    
    API->>Python: POST /chart-data {file_id, chart_type, config}
    Python->>Python: pandas groupby + aggregate
    Python->>Python: Format data for Recharts
    Python-->>API: {labels: [...], datasets: [...], options: {...}}
    
    API->>LLM: "Describe insight from this chart data"
    LLM-->>API: Insight text (streaming)
    
    API-->>Frontend: {type: "chart", chart_type: "pie", data: {...}, insight: "..."}
    Frontend->>Frontend: Render <PieChart> with Recharts
    Frontend-->>User: Interactive Pie Chart + AI Insight
```

### 4. Report Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Next.js API
    participant Queue as BullMQ/Redis
    participant Worker as Report Worker
    participant RAG as RAG Pipeline
    participant LLM as LLM Provider
    participant PDF as Puppeteer
    participant DB as PostgreSQL

    User->>Frontend: "Generate laporan analisis Q1 2024"
    User->>Frontend: Select template (5 BAB)
    Frontend->>API: POST /api/reports/generate
    API->>DB: Create report record (status: processing)
    API->>Queue: Add job: generate-report
    API-->>Frontend: {report_id, status: "processing"}

    Queue->>Worker: Process job
    
    loop Setiap BAB (1 to 5)
        Worker->>RAG: Search relevant context for BAB N
        RAG->>DB: Vector similarity search
        DB-->>RAG: Relevant document chunks
        RAG-->>Worker: Context for BAB N
        
        Worker->>LLM: Generate BAB N content + context
        LLM-->>Worker: BAB N content (markdown)
        Worker->>DB: Save report_section (bab_n)
        Worker-->>Frontend: WebSocket: progress update
        Frontend-->>User: "BAB N selesai (N/5)"
    end
    
    Worker->>DB: Update report status: completed
    Worker-->>Frontend: WebSocket: report ready
    Frontend-->>User: "Laporan selesai! Review & Export"

    Note over User, PDF: User reviews and exports

    User->>Frontend: Click "Export PDF"
    Frontend->>API: POST /api/reports/{id}/export-pdf
    API->>DB: Get all report sections
    API->>PDF: Render HTML to PDF (with styling)
    PDF-->>API: PDF buffer
    API->>Storage: Save PDF file
    API-->>Frontend: {pdf_url}
    Frontend-->>User: Download PDF
```

---

## Multi-LLM Provider Architecture (Adapter/Strategy Pattern)

### Pattern Design

```mermaid
classDiagram
    class LLMRouter {
        -providers: Map~string, LLMProvider~
        -activeProvider: string
        +chat(messages, options): AsyncStream
        +switchProvider(name): void
        +getProviders(): ProviderInfo[]
        +testConnection(name): boolean
    }

    class LLMProvider {
        <<interface>>
        +name: string
        +chat(messages, options): AsyncStream
        +generateEmbedding(text): number[]
        +isAvailable(): boolean
        +getModels(): Model[]
    }

    class CerebrasProvider {
        -apiKey: string
        -baseUrl: string
        +chat(messages, options): AsyncStream
        +generateEmbedding(text): number[]
        +isAvailable(): boolean
        +getModels(): Model[]
    }

    class GroqProvider {
        -apiKey: string
        +chat(messages, options): AsyncStream
        +generateEmbedding(text): number[]
        +isAvailable(): boolean
        +getModels(): Model[]
    }

    class GeminiProvider {
        -apiKey: string
        +chat(messages, options): AsyncStream
        +generateEmbedding(text): number[]
        +isAvailable(): boolean
        +getModels(): Model[]
    }

    class SumopodProvider {
        -apiKey: string
        -endpoint: string
        +chat(messages, options): AsyncStream
        +generateEmbedding(text): number[]
        +isAvailable(): boolean
        +getModels(): Model[]
    }

    LLMRouter --> LLMProvider
    LLMProvider <|.. CerebrasProvider
    LLMProvider <|.. GroqProvider
    LLMProvider <|.. GeminiProvider
    LLMProvider <|.. SumopodProvider
```

### Implementation Pattern (TypeScript)

```typescript
// Interface yang harus diimplementasi setiap provider
interface LLMProvider {
  name: string;
  
  chat(params: ChatParams): AsyncGenerator<string>;
  
  generateEmbedding(text: string): Promise<number[]>;
  
  isAvailable(): Promise<boolean>;
  
  getModels(): Model[];
}

// Router yang mengelola semua provider
class LLMRouter {
  private providers = new Map<string, LLMProvider>();
  private activeProvider: string;

  register(provider: LLMProvider) {
    this.providers.set(provider.name, provider);
  }

  async *chat(messages: Message[], options?: ChatOptions) {
    const provider = this.providers.get(this.activeProvider);
    if (!provider) throw new Error(`Provider ${this.activeProvider} not found`);
    
    yield* provider.chat({ messages, ...options });
  }

  // Fallback: jika provider gagal, coba provider lain
  async *chatWithFallback(messages: Message[], options?: ChatOptions) {
    const providerOrder = [this.activeProvider, ...this.getFallbackOrder()];
    
    for (const name of providerOrder) {
      try {
        const provider = this.providers.get(name)!;
        yield* provider.chat({ messages, ...options });
        return; // Success, stop trying
      } catch (error) {
        console.warn(`Provider ${name} failed, trying next...`);
        continue;
      }
    }
    throw new Error('All providers failed');
  }
}
```

---

## RAG Pipeline Detail

```mermaid
graph LR
    subgraph "Ingestion Pipeline"
        A[Upload Document] --> B[Extract Text]
        B --> C[Clean & Preprocess]
        C --> D[Chunk Text]
        D --> E[Generate Embeddings]
        E --> F[Store in pgvector]
    end

    subgraph "Retrieval Pipeline"
        G[User Query] --> H[Generate Query Embedding]
        H --> I[Vector Similarity Search]
        I --> J[Re-rank Results]
        J --> K[Build Context]
        K --> L[Send to LLM with Context]
    end

    subgraph "Chunking Strategy"
        D --> D1[Fixed Size: 500 tokens]
        D --> D2[Overlap: 50 tokens]
        D --> D3[Semantic Boundaries]
    end
```

### RAG Configuration

```
Chunking Strategy:
- Chunk size: 500 tokens (optimal untuk most embedding models)
- Overlap: 50 tokens (menjaga konteks antar chunk)
- Separator: paragraph boundaries > sentence boundaries > fixed size

Embedding Model:
- Primary: text-embedding-3-small (OpenAI) atau all-MiniLM-L6-v2 (local)
- Dimension: 384 atau 1536 tergantung model
- Stored in: pgvector column type vector(384)

Retrieval:
- Top-K: 5 chunks (default)
- Similarity threshold: 0.7
- Re-ranking: Cross-encoder (optional, untuk accuracy)
- Context window: Max 4000 tokens dari retrieved chunks
```

---

## PDF Generation Pipeline

```mermaid
graph TD
    A[Report Content - Markdown] --> B[Convert to HTML]
    B --> C[Apply PDF Template/CSS]
    C --> D{Generation Method}
    
    D -->|Puppeteer| E[Launch Headless Chrome]
    E --> F[Load HTML Page]
    F --> G[Wait for Render]
    G --> H[page.pdf - Generate PDF]
    
    D -->|React-PDF| I[React Components]
    I --> J[PDF Document Structure]
    J --> K[renderToStream]
    
    H --> L[PDF Buffer]
    K --> L
    
    L --> M[Save to Storage]
    M --> N[Return Download URL]

    subgraph "PDF Template"
        C --> T1[Cover Page]
        C --> T2[Table of Contents]
        C --> T3[Header/Footer]
        C --> T4[Page Numbers]
        C --> T5[Charts as Images]
    end
```

### PDF Template Structure

```
Laporan PDF Structure:
+---------------------------+
|      COVER PAGE           |
|  Judul Laporan            |
|  Tanggal, Penulis         |
+---------------------------+
|    DAFTAR ISI             |
|  BAB I ............. 1    |
|  BAB II ............ 5    |
|  BAB III ........... 12   |
+---------------------------+
|    BAB I - PENDAHULUAN    |
|  1.1 Latar Belakang       |
|  1.2 Tujuan              |
|  1.3 Ruang Lingkup       |
+---------------------------+
|    BAB II - ...           |
|  (Content with tables     |
|   and charts embedded)    |
+---------------------------+
|    ...                    |
+---------------------------+
|    LAMPIRAN               |
|  (Raw data, charts)      |
+---------------------------+
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production - Docker Compose / VPS"
        Nginx[Nginx - Reverse Proxy + SSL]
        
        subgraph "Application Containers"
            NextApp[Next.js App - Port 3000]
            FastAPI[Python FastAPI - Port 8000]
            Worker[Report Worker - Background]
        end
        
        subgraph "Data Containers"
            PG[PostgreSQL 16 + pgvector]
            Redis[Redis 7]
            MinIO[MinIO - S3 Compatible]
        end
    end

    subgraph "External Services"
        Cerebras_API[Cerebras API]
        Groq_API[Groq API]
        Gemini_API[Gemini API]
        Sumopod_API[Sumopod Endpoint]
    end

    Internet[Internet] --> Nginx
    Nginx --> NextApp
    NextApp --> FastAPI
    NextApp --> PG
    NextApp --> Redis
    NextApp --> MinIO
    FastAPI --> MinIO
    Worker --> PG
    Worker --> Redis
    
    NextApp --> Cerebras_API
    NextApp --> Groq_API
    NextApp --> Gemini_API
    NextApp --> Sumopod_API
```

### Alternative: Vercel + Railway

```mermaid
graph TB
    subgraph "Vercel"
        NextApp[Next.js App - Serverless]
        EdgeFunc[Edge Functions - Streaming]
    end
    
    subgraph "Railway"
        FastAPI[Python FastAPI]
        PG[PostgreSQL + pgvector]
        Redis[Redis]
        Worker[Background Worker]
    end
    
    subgraph "Cloudflare R2"
        Storage[File Storage]
    end

    Internet --> NextApp
    NextApp --> EdgeFunc
    NextApp --> FastAPI
    NextApp --> PG
    NextApp --> Redis
    FastAPI --> Storage
    Worker --> PG
    Worker --> Redis
```

---

## Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        A[Rate Limiting - per user, per IP]
        B[Authentication - JWT + Session]
        C[Authorization - Role-based]
        D[Input Validation - Zod schemas]
        E[File Validation - type, size, content]
        F[SQL Injection Prevention - Prisma ORM]
        G[XSS Prevention - sanitize markdown]
        H[CORS Configuration]
        I[Encryption - TLS 1.3 + AES-256 at rest]
    end

    Request[Incoming Request] --> A
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> Response[Safe Response]
```
