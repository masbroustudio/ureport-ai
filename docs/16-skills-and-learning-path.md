# 16 - Skills & Learning Path

## Overview

Dokumen ini berisi daftar semua skills dan pengetahuan yang dibutuhkan untuk membangun uReport AI v2. Setiap skill dikategorikan berdasarkan:
- **Difficulty Level:** Beginner / Intermediate / Advanced
- **Priority:** Must-Have / Important / Nice-to-Have
- **Time to Learn:** Estimasi waktu untuk menguasai dasar

---

## 1. Frontend Development

### 1.1 React 19 (Hooks, RSC, Suspense)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 2-4 minggu |

**Yang perlu dikuasai:**
- JSX syntax dan component structure
- useState, useEffect, useRef, useCallback, useMemo hooks
- React Server Components (RSC) - paradigma baru
- Suspense boundaries untuk async data fetching
- useTransition dan useDeferredValue
- Custom hooks pattern
- Error boundaries
- Context API
- React.memo, lazy loading, code splitting
- use() hook baru di React 19
- Actions dan useActionState
- Concurrent rendering patterns

**Learning Resources:**
- [React Official Docs](https://react.dev/) - Dokumentasi resmi
- [React 19 Blog](https://react.dev/blog/2024/12/05/react-19) - Fitur baru
- [Full React Course](https://www.youtube.com/watch?v=bMknfKXIFA8) - freeCodeCamp
- [React Patterns](https://reactpatterns.com/) - Common patterns
- [useHooks](https://usehooks.com/) - Collection of hooks

---

### 1.2 Next.js 15 App Router

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Must-Have |
| **Time to Learn** | 3-4 minggu |

**Yang perlu dikuasai:**
- File-based routing (pages, layouts, loading, error, not-found)
- Server Components vs Client Components (kapan pakai masing-masing)
- Data fetching patterns (server-side, parallel, sequential)
- Route Handlers (GET, POST, PUT, DELETE)
- Middleware (authentication, redirects, headers)
- Dynamic routes dan route groups
- Server Actions (form handling tanpa API endpoint)
- Streaming dan Progressive Rendering
- Parallel Routes dan Intercepting Routes
- Image optimization (next/image)
- Font optimization (next/font)
- Environment variables (NEXT_PUBLIC_ prefix)
- Caching dan revalidation strategies
- Partial Prerendering (PPR) - fitur baru Next.js 15

**Learning Resources:**
- [Next.js Learn Course](https://nextjs.org/learn) - Interactive course resmi
- [Next.js Docs - App Router](https://nextjs.org/docs/app) - Reference lengkap
- [Lee Robinson YouTube](https://www.youtube.com/@leerob) - Next.js core team
- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples) - Code examples
- [Vercel Templates](https://vercel.com/templates/next.js) - Starter templates

---

### 1.3 TypeScript (Strict Mode, Generics, Utility Types)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Basic types (string, number, boolean, array, object)
- Interfaces dan type aliases (kapan pakai masing-masing)
- Generic types (fungsi, class, constraint)
- Union types dan intersection types
- Type narrowing dan type guards (is, in, typeof, instanceof)
- Utility types (Partial, Omit, Pick, Record, Required, Readonly)
- Conditional types dan mapped types
- Template literal types
- Enums vs const objects
- Type inference dan satisfies operator
- Module types dan declaration files (.d.ts)
- Async types (Promise<T>, Awaited<T>)
- Strict mode configuration (strict: true di tsconfig)
- Discriminated unions pattern

**Learning Resources:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) - Official handbook
- [TypeScript Exercises](https://typescript-exercises.github.io/) - Practice interaktif
- [Type Challenges](https://github.com/type-challenges/type-challenges) - Advanced practice
- [Total TypeScript](https://www.totaltypescript.com/) - Matt Pocock tutorials
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/) - Free book

---

### 1.4 TailwindCSS + shadcn/ui

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Beginner-Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- CSS fundamentals (box model, flexbox, grid)
- Tailwind utility classes (spacing, colors, typography, layout)
- Responsive design (breakpoints: sm, md, lg, xl, 2xl)
- Dark mode (class strategy)
- Tailwind configuration (theme extend, custom colors, plugins)
- CSS animations (transition, transform, keyframes)
- shadcn/ui component installation dan customization
- Radix UI primitives (accessibility, keyboard navigation)
- Component variants menggunakan class-variance-authority (cva)
- cn() utility untuk conditional classes
- Form handling: React Hook Form + Zod + shadcn Form component

**Learning Resources:**
- [Tailwind CSS Docs](https://tailwindcss.com/docs) - Official docs
- [shadcn/ui Documentation](https://ui.shadcn.com/docs) - Component library
- [Radix UI Primitives](https://www.radix-ui.com/primitives) - Underlying primitives
- [Tailwind Labs YouTube](https://www.youtube.com/@TailwindLabs) - Video tutorials
- [Flexbox Froggy](https://flexboxfroggy.com/) - Game belajar flexbox
- [Grid Garden](https://cssgridgarden.com/) - Game belajar CSS grid

---

### 1.5 Plotly.js (react-plotly.js)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Important |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Plotly.js basic concepts (traces, layout, config)
- react-plotly.js wrapper component
- Chart types: bar, line, scatter, pie, heatmap, box plot
- Subplots dan multiple axes
- Custom styling (colors, fonts, margins)
- Responsive containers dan auto-resize
- Interactive features (hover, click events, zoom, pan)
- Exporting charts (PNG, SVG, PDF)
- Animation dan transitions
- Plotly Express vs Graph Objects pattern

**Learning Resources:**
- [Plotly.js Documentation](https://plotly.com/javascript/) - Official JS docs
- [react-plotly.js](https://github.com/plotly/react-plotly.js) - React wrapper
- [Plotly Examples](https://plotly.com/javascript/basic-charts/) - Chart gallery
- [Plotly Python](https://plotly.com/python/) - Python reference (konsep sama)

---

### 1.6 Vercel AI SDK (useChat, useCompletion)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- useChat hook (streaming chat interface)
- useCompletion hook (text completion)
- Custom transport dan API routes
- Streaming protocols (text, data, tool calls)
- Tool calling dan function execution
- Message history management
- Error handling dan retry logic
- Rate limiting considerations
- Multi-modal support (text + images)
- Custom providers integration

**Learning Resources:**
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) - Official documentation
- [AI SDK Examples](https://github.com/vercel/ai/tree/main/examples) - Code examples
- [AI SDK Providers](https://sdk.vercel.ai/providers) - Provider integrations
- [Next.js AI Chatbot Template](https://github.com/vercel/ai-chatbot) - Full example

---

### 1.7 Zustand + TanStack Query (State Management)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Important |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Zustand: store creation, selectors, middleware
- Zustand: persist middleware (localStorage)
- Zustand: devtools integration
- Zustand: slices pattern untuk large stores
- TanStack Query: useQuery, useMutation, useInfiniteQuery
- TanStack Query: query keys dan cache invalidation
- TanStack Query: optimistic updates
- TanStack Query: prefetching dan dehydration (SSR)
- TanStack Query: retry dan error handling
- Kapan pakai Zustand vs TanStack Query vs Server State

**Learning Resources:**
- [Zustand Documentation](https://docs.pmnd.rs/zustand) - Official docs
- [TanStack Query Docs](https://tanstack.com/query/latest) - Official docs
- [TkDodo Blog](https://tkdodo.eu/blog/practical-react-query) - Practical React Query
- [Zustand GitHub](https://github.com/pmndrs/zustand) - Examples dan recipes

---

## 2. Backend Development

### 2.1 Python 3.12 (async/await, Type Hints, Dataclasses)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 3-4 minggu |

**Yang perlu dikuasai:**
- Python syntax fundamentals (list, dict, tuple, set)
- async/await dan asyncio event loop
- Type hints (typing module, Generic, Protocol, TypeVar)
- Dataclasses dan attrs
- Context managers (async with)
- Generators dan async generators
- Decorators (function dan class decorators)
- Exception handling patterns
- Virtual environments (venv, uv)
- Python 3.12 features (improved error messages, type parameter syntax)
- Pattern matching (match/case - Python 3.10+)
- Protocols dan structural subtyping

**Learning Resources:**
- [Python Official Docs](https://docs.python.org/3.12/) - Reference lengkap
- [Real Python](https://realpython.com/) - Tutorial berkualitas tinggi
- [Python Type Hints](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) - Mypy cheat sheet
- [asyncio Docs](https://docs.python.org/3/library/asyncio.html) - Async programming
- [Python Patterns](https://python-patterns.guide/) - Design patterns di Python

---

### 2.2 FastAPI (Dependency Injection, Middleware, Async Routes)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Path operations (GET, POST, PUT, DELETE, PATCH)
- Request/Response models dengan Pydantic
- Dependency Injection system (Depends)
- Middleware (CORS, auth, logging, timing)
- Background tasks
- WebSocket support
- File upload/download
- Error handling (HTTPException, custom exception handlers)
- Authentication (OAuth2, JWT, API keys)
- OpenAPI documentation (auto-generated)
- Lifespan events (startup/shutdown)
- Router organization dan API versioning
- Async database sessions sebagai dependency
- Testing dengan TestClient / httpx.AsyncClient

**Learning Resources:**
- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Sangat lengkap dan interaktif
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) - Step-by-step tutorial
- [FastAPI Full Stack Template](https://github.com/tiangolo/full-stack-fastapi-template) - Production template
- [TestDriven.io FastAPI](https://testdriven.io/blog/topics/fastapi/) - Advanced tutorials

---

### 2.3 Pydantic v2 (Validators, Serialization, Settings)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- BaseModel creation dan field types
- Field validators (@field_validator, @model_validator)
- Custom serialization (model_dump, model_dump_json)
- Computed fields (@computed_field)
- Generic models
- Discriminated unions
- BaseSettings untuk environment variables
- JSON Schema generation
- Strict vs lax mode
- Custom types dan annotated validators
- Migration dari Pydantic v1 ke v2

**Learning Resources:**
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/) - Official documentation
- [Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/) - v1 to v2
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Env management

---

### 2.4 SQLAlchemy 2.0 (Async Sessions, Mapped Classes)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Declarative mapping dengan mapped_column()
- Relationship definitions (one-to-many, many-to-many)
- Async session management (AsyncSession, async_sessionmaker)
- Query patterns (select, where, join, subquery)
- Eager vs lazy loading (selectinload, joinedload)
- Transaction management
- Connection pooling
- Events dan hooks
- Hybrid properties
- Type annotations integration
- Unit of Work pattern
- Bulk operations

**Learning Resources:**
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/) - Official docs
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) - Unified tutorial
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async guide
- [Alembic + SQLAlchemy](https://alembic.sqlalchemy.org/) - Migrations

---

### 2.5 Alembic (Migrations, Autogenerate, Branching)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1 minggu |

**Yang perlu dikuasai:**
- Migration creation (revision --autogenerate)
- Upgrade dan downgrade operations
- Migration branching dan merging
- Data migrations (bukan hanya schema)
- Batch operations untuk SQLite compatibility
- Environment configuration (env.py)
- Offline mode (generate SQL tanpa DB connection)
- Migration testing strategies
- Handling enum changes
- Custom migration operations

**Learning Resources:**
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) - Official tutorial
- [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html) - Common recipes
- [Real Python - Alembic](https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/) - Practical guide

---

### 2.6 Celery 5 (Tasks, Retry, Chains, Canvas)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Important |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Task definition dan registration
- Broker configuration (Redis)
- Result backends
- Retry mechanisms (autoretry_for, max_retries, countdown)
- Task chains, groups, dan chords
- Canvas (workflow primitives)
- Periodic tasks (Celery Beat)
- Task routing dan queues
- Error handling dan dead letter queues
- Monitoring dengan Flower
- Task serialization (JSON, pickle)
- Rate limiting
- Task priority
- Integration dengan FastAPI

**Learning Resources:**
- [Celery Documentation](https://docs.celeryq.dev/en/stable/) - Official docs
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices) - Best practices
- [Flower Monitoring](https://flower.readthedocs.io/) - Task monitoring
- [Real Python - Celery](https://realpython.com/asynchronous-tasks-with-django-and-celery/) - Practical guide

---

## 3. AI/LLM

### 3.1 LiteLLM (Unified API, Provider Routing, Fallback, Caching)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Unified completion API (litellm.completion)
- Provider configuration (Groq, Cerebras, Gemini, custom)
- Router setup (fallback, load balancing, retry)
- Streaming responses
- Cost tracking dan budget management
- Caching strategies (in-memory, Redis)
- Model aliases dan mapping
- Error handling per provider
- Rate limit handling
- Custom API base configuration (untuk Sumopod)
- Logging dan observability

**Learning Resources:**
- [LiteLLM Documentation](https://docs.litellm.ai/) - Official docs
- [LiteLLM GitHub](https://github.com/BerriAI/litellm) - Source code dan examples
- [LiteLLM Proxy](https://docs.litellm.ai/docs/simple_proxy) - Proxy server setup
- [Provider List](https://docs.litellm.ai/docs/providers) - Supported providers

---

### 3.2 LangGraph (State Machines, Nodes, Edges, Conditional Routing)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Advanced |
| **Priority** | Must-Have |
| **Time to Learn** | 3-4 minggu |

**Yang perlu dikuasai:**
- Graph definition (StateGraph)
- Node functions (sync dan async)
- Edge types (normal, conditional)
- State management (TypedDict, Annotated)
- Checkpointing dan persistence
- Human-in-the-loop patterns
- Branching dan parallel execution
- Error handling dan retry di nodes
- Subgraphs dan composition
- Streaming events dari graph
- Tool calling integration
- Memory dan conversation history
- Debugging dan visualization

**Learning Resources:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Official docs
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/) - Step-by-step
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples) - Code examples
- [LangChain Academy](https://academy.langchain.com/) - Free courses termasuk LangGraph

---

### 3.3 LlamaIndex (Readers, Index Types, Retrievers, Synthesizers)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Document loaders/readers (PDF, DOCX, CSV, web)
- Index types (VectorStoreIndex, SummaryIndex, KeywordTableIndex)
- Node parsing dan text splitting strategies
- Retriever types (vector, keyword, hybrid)
- Response synthesizers (refine, compact, tree_summarize)
- Query engines dan chat engines
- Metadata filtering
- Custom retrievers
- Embedding models integration
- Evaluation (faithfulness, relevancy)
- Callbacks dan observability

**Learning Resources:**
- [LlamaIndex Docs](https://docs.llamaindex.ai/) - Official documentation
- [LlamaIndex Tutorials](https://docs.llamaindex.ai/en/stable/understanding/) - Getting started
- [LlamaIndex GitHub](https://github.com/run-llama/llama_index) - Source dan examples
- [RAG Evaluation](https://docs.llamaindex.ai/en/stable/optimizing/evaluation/) - Eval guide

---

### 3.4 Qdrant (Collections, Points, Search, Payload Filtering)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Collection management (create, update, delete)
- Point operations (upsert, search, scroll, delete)
- Vector search (cosine, dot product, euclidean)
- Payload filtering (match, range, geo, nested)
- Hybrid search (sparse + dense vectors)
- Batch operations
- Snapshots dan backups
- Quantization (scalar, product, binary)
- Multi-tenancy patterns
- Recommendation API
- Python client library (qdrant-client)

**Learning Resources:**
- [Qdrant Documentation](https://qdrant.tech/documentation/) - Official docs
- [Qdrant Tutorials](https://qdrant.tech/documentation/tutorials/) - Step-by-step
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client) - Python SDK
- [Qdrant Examples](https://github.com/qdrant/examples) - Use case examples

---

### 3.5 Embeddings - bge-m3 (sentence-transformers, Multilingual)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Important |
| **Time to Learn** | 1 minggu |

**Yang perlu dikuasai:**
- Embedding concepts (dense vs sparse vs multi-vector)
- sentence-transformers library
- BGE-M3 model (multilingual, multi-functionality)
- Tokenization dan max sequence length
- Batch encoding untuk efisiensi
- Dimensionality dan storage considerations
- Normalization dan similarity metrics
- Fine-tuning considerations
- Inference optimization (ONNX, quantization)
- Bahasa Indonesia embedding quality

**Learning Resources:**
- [sentence-transformers Docs](https://www.sbert.net/) - Official docs
- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216) - Research paper
- [HuggingFace BGE-M3](https://huggingface.co/BAAI/bge-m3) - Model card
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - Embedding benchmarks

---

## 4. Data Engineering

### 4.1 pandas (DataFrame ops, GroupBy, Pivot, Merge)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- DataFrame creation dan manipulation
- Indexing dan selection (loc, iloc, boolean indexing)
- GroupBy operations (agg, transform, filter)
- Pivot tables dan crosstab
- Merge, join, dan concat
- Missing data handling (fillna, dropna, interpolate)
- String operations (str accessor)
- DateTime operations (dt accessor)
- Apply, map, dan vectorized operations
- Memory optimization (dtypes, categorical)
- Reading/writing files (CSV, Excel, JSON, Parquet)
- Method chaining patterns

**Learning Resources:**
- [pandas Documentation](https://pandas.pydata.org/docs/) - Official docs
- [pandas User Guide](https://pandas.pydata.org/docs/user_guide/) - Comprehensive guide
- [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) - Quick start
- [Kaggle pandas Course](https://www.kaggle.com/learn/pandas) - Free interactive course
- [Modern Pandas](https://tomaugspurger.net/posts/modern-1-intro/) - Advanced patterns

---

### 4.2 Plotly (Express, Graph Objects, Subplots)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Plotly Express (high-level API untuk quick charts)
- Graph Objects (low-level API untuk full control)
- Chart types: bar, line, scatter, pie, histogram, box, heatmap, treemap
- Subplots dan multiple axes (make_subplots)
- Layout customization (title, axes, legend, annotations)
- Color scales dan theming
- Statistical charts (violin, strip, ECDF)
- Export ke HTML, PNG, SVG, PDF
- Plotly tables
- Animation frames
- Integration dengan pandas DataFrame

**Learning Resources:**
- [Plotly Python Docs](https://plotly.com/python/) - Official Python docs
- [Plotly Express](https://plotly.com/python/plotly-express/) - High-level API
- [Plotly Graph Objects](https://plotly.com/python/graph-objects/) - Low-level API
- [Plotly Community Forum](https://community.plotly.com/) - Community support

---

### 4.3 E2B / nsjail (Sandbox Code Execution)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Advanced |
| **Priority** | Important |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Sandboxing concepts (isolation, resource limits)
- E2B SDK (cloud sandboxes untuk code execution)
- nsjail configuration (Linux namespaces, cgroups)
- Security considerations (file system access, network, syscalls)
- Timeout management
- Resource limits (CPU, memory, disk)
- Input/output handling
- Error capture dan reporting
- Multi-language support (Python, R)
- Integration dengan LLM-generated code
- Stateful vs stateless execution

**Learning Resources:**
- [E2B Documentation](https://e2b.dev/docs) - Cloud sandbox docs
- [E2B Code Interpreter](https://e2b.dev/docs/code-interpreting) - Code execution SDK
- [nsjail GitHub](https://github.com/google/nsjail) - Google's sandboxing tool
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html) - Kernel docs

---

## 5. Report Generation

### 5.1 Jinja2 (Templates, Filters, Macros, Inheritance)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Beginner-Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1 minggu |

**Yang perlu dikuasai:**
- Template syntax (variables, expressions, statements)
- Control structures (for, if, elif, else)
- Template inheritance (extends, block)
- Macros (reusable template functions)
- Filters (built-in dan custom filters)
- Include dan import
- Whitespace control
- Auto-escaping (HTML safety)
- Environment configuration
- Custom extensions
- Async rendering support
- Template loading strategies

**Learning Resources:**
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Official docs
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/en/3.1.x/templates/) - Template syntax
- [Real Python - Jinja](https://realpython.com/primer-on-jinja-templating/) - Practical tutorial
- [Jinja2 Tips & Tricks](https://jinja.palletsprojects.com/en/3.1.x/tricks/) - Advanced patterns

---

### 5.2 WeasyPrint (CSS Paged Media, @page, Print Layout)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- WeasyPrint API (HTML to PDF conversion)
- CSS Paged Media specification (@page rule)
- Page size dan margins
- Headers dan footers (running elements, @top-center, @bottom-right)
- Page breaks (break-before, break-after, break-inside)
- Table of Contents generation (target-counter, bookmark)
- Multi-column layouts
- Image handling dan sizing
- Font embedding (@font-face)
- CSS counters untuk page numbering
- Named pages untuk different sections
- Footnotes
- Performance optimization (large documents)
- Integration dengan Jinja2 templates

**Learning Resources:**
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/stable/) - Official docs
- [CSS Paged Media Spec](https://www.w3.org/TR/css-page-3/) - W3C specification
- [WeasyPrint Samples](https://github.com/nickhudkins/paged-media-examples) - Example PDFs
- [Print CSS Rocks](https://print-css.rocks/) - CSS print resources

---

### 5.3 HTML/CSS untuk PDF (Page-break, Headers/Footers, ToC)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Semantic HTML untuk dokumen terstruktur
- Print-specific CSS properties
- Page break control (avoid, always, auto)
- Orphans dan widows control
- CSS counters untuk numbering
- Flexbox/Grid untuk layout di paged media
- Image sizing dan aspect ratio preservation
- Table pagination (thead repeat)
- Cross-references
- Bookmark hierarchy
- Color management (CMYK considerations)
- Accessible PDF output

**Learning Resources:**
- [MDN CSS Paged Media](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_paged_media) - MDN reference
- [A List Apart - Print Styles](https://alistapart.com/article/building-books-with-css3/) - Article
- [Paged.js](https://pagedjs.org/) - Alternative polyfill (untuk referensi)

---

## 6. DevOps

### 6.1 Docker + Docker Compose (Multi-service, Volumes, Networks)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Must-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- Dockerfile best practices (multi-stage builds, layer caching)
- Docker Compose untuk multi-service orchestration
- Volume management (named volumes, bind mounts)
- Network configuration (bridge, host, custom networks)
- Environment variables dan .env files
- Health checks
- Resource limits (memory, CPU)
- Docker build arguments (ARG, ENV)
- Image optimization (alpine, slim, distroless)
- Docker registry (push, pull, tag)
- Docker debugging (logs, exec, inspect)
- Compose profiles untuk development vs production

**Learning Resources:**
- [Docker Documentation](https://docs.docker.com/) - Official docs
- [Docker Compose Docs](https://docs.docker.com/compose/) - Compose reference
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) - Optimization
- [Docker Curriculum](https://docker-curriculum.com/) - Beginner-friendly tutorial

---

### 6.2 Nginx (Reverse Proxy, SSL, Rate Limiting)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Important |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Server blocks dan virtual hosts
- Reverse proxy configuration (proxy_pass)
- SSL/TLS termination (Let's Encrypt, certbot)
- Rate limiting (limit_req_zone, limit_conn_zone)
- Static file serving
- Gzip compression
- WebSocket proxy
- Load balancing (upstream)
- Caching (proxy_cache)
- Security headers (X-Frame-Options, CSP, HSTS)
- Access logs dan error logs
- Health check endpoints

**Learning Resources:**
- [Nginx Documentation](https://nginx.org/en/docs/) - Official docs
- [Nginx Admin Guide](https://docs.nginx.com/nginx/admin-guide/) - Administration
- [DigitalOcean Nginx Tutorials](https://www.digitalocean.com/community/tags/nginx) - Practical guides
- [Mozilla SSL Config Generator](https://ssl-config.mozilla.org/) - SSL best practices

---

### 6.3 GitHub Actions (CI/CD Pipelines)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate |
| **Priority** | Important |
| **Time to Learn** | 1-2 minggu |

**Yang perlu dikuasai:**
- Workflow YAML syntax
- Triggers (push, pull_request, schedule, workflow_dispatch)
- Jobs dan steps
- Actions marketplace
- Secrets dan environment variables
- Matrix builds
- Caching dependencies (actions/cache)
- Artifacts upload/download
- Docker builds dalam CI
- Deployment workflows
- Branch protection rules integration
- Reusable workflows
- Composite actions

**Learning Resources:**
- [GitHub Actions Docs](https://docs.github.com/en/actions) - Official documentation
- [Actions Marketplace](https://github.com/marketplace?type=actions) - Pre-built actions
- [GitHub Actions Examples](https://github.com/actions/starter-workflows) - Starter workflows
- [Act](https://github.com/nektos/act) - Run actions locally

---

### 6.4 OpenTelemetry (Tracing, Metrics, Instrumentation)

| Aspek | Detail |
|-------|--------|
| **Difficulty** | Intermediate-Advanced |
| **Priority** | Nice-to-Have |
| **Time to Learn** | 2-3 minggu |

**Yang perlu dikuasai:**
- OpenTelemetry concepts (traces, spans, metrics, logs)
- Python SDK (opentelemetry-python)
- Auto-instrumentation (FastAPI, SQLAlchemy, httpx)
- Manual instrumentation (custom spans)
- Context propagation
- Exporters (OTLP, Jaeger, Prometheus)
- Collector configuration
- Sampling strategies
- Custom metrics (counters, histograms, gauges)
- Distributed tracing across services
- Dashboard creation (Grafana)
- Alerting rules

**Learning Resources:**
- [OpenTelemetry Docs](https://opentelemetry.io/docs/) - Official documentation
- [OTel Python](https://opentelemetry.io/docs/languages/python/) - Python SDK
- [Jaeger Documentation](https://www.jaegertracing.io/docs/) - Tracing backend
- [Grafana Tutorials](https://grafana.com/tutorials/) - Dashboard creation

---

## Recommended Learning Order

Berikut urutan belajar yang disarankan untuk developer baru yang bergabung di project uReport AI v2:

### Phase 1: Foundation (Minggu 1-4)

Fokus pada dasar yang dibutuhkan semua fitur:

1. **Python 3.12** - Dasar async/await, type hints
2. **TypeScript** - Strict mode, generics, utility types
3. **React 19** - Hooks, RSC, Suspense
4. **FastAPI** - Routes, dependency injection, Pydantic
5. **Docker + Docker Compose** - Setup development environment

### Phase 2: Core Stack (Minggu 5-8)

Teknologi inti yang dipakai sehari-hari:

6. **Next.js 15 App Router** - Routing, server actions, streaming
7. **SQLAlchemy 2.0 + Alembic** - Database layer
8. **TailwindCSS + shadcn/ui** - UI development
9. **Zustand + TanStack Query** - State management
10. **Pydantic v2** - Validation dan serialization

### Phase 3: AI/LLM (Minggu 9-12)

Kemampuan AI yang jadi core product:

11. **LiteLLM** - Multi-provider LLM access
12. **LangGraph** - Agent orchestration
13. **Vercel AI SDK** - Frontend streaming chat
14. **LlamaIndex** - RAG pipeline
15. **Qdrant + Embeddings** - Vector search

### Phase 4: Data & Reports (Minggu 13-16)

Fitur analisis data dan report generation:

16. **pandas** - Data manipulation
17. **Plotly / react-plotly.js** - Visualization
18. **Jinja2 + WeasyPrint** - PDF report generation
19. **E2B / nsjail** - Sandbox execution
20. **Celery** - Background job processing

### Phase 5: Production (Minggu 17-20)

Persiapan production dan operational excellence:

21. **Nginx** - Reverse proxy dan SSL
22. **GitHub Actions** - CI/CD pipelines
23. **OpenTelemetry** - Observability
24. **Security best practices** - Auth, CORS, rate limiting

---

## Tips Belajar

1. **Jangan belajar semuanya sekaligus.** Fokus pada satu phase sebelum lanjut ke phase berikutnya.
2. **Langsung praktek.** Setiap teknologi, buat mini-project kecil untuk memahami konsep.
3. **Baca official docs dulu.** Dokumentasi resmi biasanya paling akurat dan up-to-date.
4. **Pair programming.** Belajar bersama tim member yang sudah lebih berpengalaman.
5. **Kontribusi ke project.** Cara terbaik belajar adalah langsung mengerjakan task di project ini.
6. **Catat yang dipelajari.** Buat personal notes untuk referensi cepat di kemudian hari.

---

## Skill Matrix Summary

| Kategori | Skill | Difficulty | Priority | Time |
|----------|-------|-----------|----------|------|
| Frontend | React 19 | Intermediate | Must-Have | 2-4w |
| Frontend | Next.js 15 | Intermediate-Advanced | Must-Have | 3-4w |
| Frontend | TypeScript | Intermediate | Must-Have | 2-3w |
| Frontend | TailwindCSS + shadcn/ui | Beginner-Intermediate | Must-Have | 1-2w |
| Frontend | Plotly.js | Intermediate | Important | 1-2w |
| Frontend | Vercel AI SDK | Intermediate | Must-Have | 1-2w |
| Frontend | Zustand + TanStack Query | Intermediate | Important | 1-2w |
| Backend | Python 3.12 | Intermediate | Must-Have | 3-4w |
| Backend | FastAPI | Intermediate | Must-Have | 2-3w |
| Backend | Pydantic v2 | Intermediate | Must-Have | 1-2w |
| Backend | SQLAlchemy 2.0 | Intermediate-Advanced | Must-Have | 2-3w |
| Backend | Alembic | Intermediate | Must-Have | 1w |
| Backend | Celery 5 | Intermediate-Advanced | Important | 2-3w |
| AI/LLM | LiteLLM | Intermediate | Must-Have | 1-2w |
| AI/LLM | LangGraph | Advanced | Must-Have | 3-4w |
| AI/LLM | LlamaIndex | Intermediate-Advanced | Must-Have | 2-3w |
| AI/LLM | Qdrant | Intermediate | Must-Have | 1-2w |
| AI/LLM | Embeddings bge-m3 | Intermediate | Important | 1w |
| Data | pandas | Intermediate | Must-Have | 2-3w |
| Data | Plotly | Intermediate | Must-Have | 1-2w |
| Data | E2B / nsjail | Advanced | Important | 2-3w |
| Report | Jinja2 | Beginner-Intermediate | Must-Have | 1w |
| Report | WeasyPrint | Intermediate-Advanced | Must-Have | 2-3w |
| Report | HTML/CSS PDF | Intermediate | Must-Have | 1-2w |
| DevOps | Docker + Compose | Intermediate | Must-Have | 2-3w |
| DevOps | Nginx | Intermediate | Important | 1-2w |
| DevOps | GitHub Actions | Intermediate | Important | 1-2w |
| DevOps | OpenTelemetry | Intermediate-Advanced | Nice-to-Have | 2-3w |

---

> **Total estimated time:** 20-24 minggu (5-6 bulan) untuk menguasai semua skill dari nol.
> Namun dengan fokus pada Must-Have skills, developer bisa produktif dalam 8-10 minggu.
