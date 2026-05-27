# 09 — Data Model & API Design

## 9.1 ERD (Entity Relationship Diagram)

```
┌──────────┐ 1   N ┌────────────────┐ 1   N ┌──────────┐
│  users   │───────│  conversations │───────│ messages │
└────┬─────┘       └───────┬────────┘       └────┬─────┘
     │ 1                   │ 1                   │
     │ N                   │ N                   │ N
┌────▼──────┐         ┌────▼─────┐          ┌────▼──────┐
│workspaces │         │  files   │          │ tool_calls│
└────┬──────┘         └──────────┘          └───────────┘
     │ 1
     │ N
┌────▼──────────┐
│ knowledge_    │
│ documents     │
└────┬──────────┘
     │ 1
     │ N
┌────▼──────────┐         ┌─────────────┐
│ kb_chunks     │         │   reports   │───── chapters / sections
└───────────────┘         └─────────────┘

┌────────────┐
│ usage_logs │  (LLM calls, cost tracking)
└────────────┘
```

---

## 9.2 PostgreSQL Schema (sketsa SQL)

```sql
-- Users
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       CITEXT UNIQUE NOT NULL,
  name        TEXT,
  avatar_url  TEXT,
  password_hash TEXT,                 -- nullable kalau OAuth-only
  oauth_provider TEXT,                -- 'google' | null
  oauth_id    TEXT,
  monthly_budget_usd NUMERIC(8,2) DEFAULT 2.00,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Workspace (V1: 1 user = 1 workspace; V2: multi-user)
CREATE TABLE workspaces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  default_provider TEXT,
  default_model TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Conversations (chat threads)
CREATE TABLE conversations (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES users(id),
  title        TEXT,
  pinned       BOOLEAN DEFAULT false,
  archived     BOOLEAN DEFAULT false,
  model        TEXT,                  -- override default
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON conversations(workspace_id, updated_at DESC);

-- Messages
CREATE TABLE messages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role            TEXT NOT NULL,     -- 'user' | 'assistant' | 'system' | 'tool'
  content         TEXT,              -- markdown
  content_json    JSONB,             -- structured (tool calls, attachments)
  parent_id       UUID,              -- threading / branch
  status          TEXT,              -- 'streaming' | 'done' | 'error'
  model           TEXT,
  tokens_in       INT,
  tokens_out      INT,
  created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON messages(conversation_id, created_at);

-- Tool calls (audit per message)
CREATE TABLE tool_calls (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id   UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  tool_name    TEXT NOT NULL,        -- 'run_python' | 'search_kb' | ...
  args_json    JSONB,
  output_json  JSONB,
  duration_ms  INT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- Files (uploaded data files)
CREATE TABLE files (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES users(id),
  name         TEXT NOT NULL,
  mime         TEXT,
  size_bytes   BIGINT,
  s3_key       TEXT NOT NULL,
  kind         TEXT,                  -- 'data' | 'document' | 'image'
  profile_json JSONB,                 -- auto-profile result
  status       TEXT DEFAULT 'ready',  -- 'uploading' | 'ready' | 'failed'
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- Knowledge documents (untuk RAG, beda dari files data)
CREATE TABLE knowledge_documents (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name         TEXT,
  source_file_id UUID REFERENCES files(id),
  title        TEXT,
  authors      TEXT,
  year         INT,
  tags         TEXT[],
  language     TEXT,
  status       TEXT,                  -- 'processing' | 'ready' | 'failed'
  chunk_count  INT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- (Vektor disimpan di Qdrant; tabel ini hanya metadata referensi)
CREATE TABLE kb_chunks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id  UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
  chunk_index  INT,
  text         TEXT,
  page         INT,
  section      TEXT,
  qdrant_id    TEXT,                  -- id vektor di Qdrant
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- Reports (PDF generation jobs & artifact)
CREATE TABLE reports (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id),
  conversation_id UUID REFERENCES conversations(id),
  title           TEXT,
  template_id     TEXT,
  outline_json    JSONB,
  markdown        TEXT,
  pdf_s3_key      TEXT,
  status          TEXT,    -- 'created' | 'planning' | 'writing' | 'rendering' | 'done' | 'failed'
  progress_pct    INT DEFAULT 0,
  error_message   TEXT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Usage / cost tracking
CREATE TABLE usage_logs (
  id           BIGSERIAL PRIMARY KEY,
  user_id      UUID NOT NULL,
  workspace_id UUID,
  provider     TEXT,
  model        TEXT,
  tokens_in    INT,
  tokens_out   INT,
  cost_usd     NUMERIC(10,6),
  task_type    TEXT,        -- 'chat' | 'data_analysis' | 'report_writer' | ...
  conversation_id UUID,
  created_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON usage_logs(user_id, created_at);

-- Memory (long-term per user, lihat docs/11)
CREATE TABLE user_memories (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind        TEXT,         -- 'fact' | 'preference' | 'goal'
  content     TEXT,
  confidence  NUMERIC(3,2),
  source_msg_id UUID,
  created_at  TIMESTAMPTZ DEFAULT now()
);
```

---

## 9.3 API Endpoints (REST)

Base path: `/api/v1`. Semua endpoint butuh JWT (kecuali auth).

### Auth
| Method | Path | Deskripsi |
|---|---|---|
| POST | `/auth/signup` | Email + password sign up |
| POST | `/auth/signin` | Sign in → JWT |
| GET  | `/auth/oauth/google` | Redirect OAuth |
| GET  | `/auth/oauth/google/callback` | OAuth callback |
| POST | `/auth/signout` | Invalidate session |
| GET  | `/auth/me` | Current user |

### Conversations
| Method | Path | Deskripsi |
|---|---|---|
| GET    | `/conversations` | List with pagination & search |
| POST   | `/conversations` | Buat baru |
| GET    | `/conversations/{id}` | Detail |
| PATCH  | `/conversations/{id}` | Rename, pin, archive |
| DELETE | `/conversations/{id}` | Hapus |
| GET    | `/conversations/{id}/messages` | List messages |
| POST   | `/conversations/{id}/messages` | **Send message (SSE streaming)** |
| POST   | `/conversations/{id}/messages/{mid}/regenerate` | Regenerate |

### Files
| Method | Path | Deskripsi |
|---|---|---|
| POST   | `/files` (multipart) | Upload, return `file_id` |
| GET    | `/files` | List files |
| GET    | `/files/{id}` | Metadata + profile |
| GET    | `/files/{id}/preview?sheet=&n=20` | Sample rows |
| DELETE | `/files/{id}` | Hapus (cascade) |

### Knowledge Base
| Method | Path | Deskripsi |
|---|---|---|
| POST   | `/kb/documents` | Upload + ingest async |
| GET    | `/kb/documents` | List, filter tag |
| GET    | `/kb/documents/{id}` | Detail + status |
| DELETE | `/kb/documents/{id}` | Hapus & remove vektor |
| POST   | `/kb/search` | `{query, top_k, filters}` → chunks |

### Reports
| Method | Path | Deskripsi |
|---|---|---|
| POST   | `/reports` | Buat report (sync planning) |
| GET    | `/reports` | List |
| GET    | `/reports/{id}` | Detail (status + outline) |
| PUT    | `/reports/{id}/outline` | Edit outline |
| POST   | `/reports/{id}/start` | Mulai writing async |
| GET    | `/reports/{id}/sse` | Stream progress |
| POST   | `/reports/{id}/regenerate-section` | Ulang section |
| GET    | `/reports/{id}/pdf` | Pre-signed URL |
| DELETE | `/reports/{id}` | Hapus |

### Tools (internal, dipakai agent)
Tidak diekspos publik; di-call internal lewat orchestrator.

### Models
| Method | Path | Deskripsi |
|---|---|---|
| GET    | `/models` | List provider+model tersedia (sesuai .env) |

### Usage
| Method | Path | Deskripsi |
|---|---|---|
| GET    | `/usage/me` | Konsumsi token & cost user (this month) |

---

## 9.4 Format Stream Event (SSE) — `/messages` & `/reports/sse`

```
event: token        data: {"text": "Halo"}
event: tool_start   data: {"id":"tc_1","tool":"run_python","args":{...}}
event: tool_chunk   data: {"id":"tc_1","stdout":"..."}
event: tool_end     data: {"id":"tc_1","output":{...}}
event: chart        data: {"id":"chart_abc","spec":{...}}
event: table        data: {"id":"tbl_xyz","columns":[...],"rows":[...]}
event: citation     data: {"id":"cit_1","doc":"X.pdf","page":12}
event: done         data: {"message_id":"...","usage":{"in":120,"out":340}}
event: error        data: {"code":"...","message":"..."}
```

---

## 9.5 Authentication & Authorization

- **JWT** signed dengan `JWT_SECRET`, expiry 7 hari
- Refresh token (V1) — `httpOnly` cookie
- Middleware `get_current_user(token)` di FastAPI (dependency injection)
- RBAC sederhana V1 (semua user = "user"); V2 tambah "admin", "viewer"

---

## 9.6 Rate Limiting

- Pakai middleware berbasis Redis (token bucket)
- Default: 60 req/menit per user, 600 req/jam
- Endpoint generate report: 10 / hari (per user)
- Upload: 50 file / hari

---

## 9.7 Pagination Pattern

Cursor-based:
```
GET /conversations?limit=20&cursor=eyJp...
→ { items: [...], next_cursor: "eyJ..."} 
```

---

## 9.8 OpenAPI / Type Generation

- FastAPI auto-generate `/openapi.json`
- Run `openapi-typescript` saat CI → `packages/shared-types/src/api.d.ts`
- Frontend import types langsung — fully type-safe end-to-end.
