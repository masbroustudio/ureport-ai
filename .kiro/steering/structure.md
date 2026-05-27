---
inclusion: always
---

# Project Structure — uReport AI

## Layout Monorepo (target)

```
ureport-ai/
├── apps/
│   ├── web/                      # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/              # App Router pages
│   │   │   ├── components/
│   │   │   │   ├── ui/           # shadcn primitives
│   │   │   │   ├── chat/
│   │   │   │   ├── files/
│   │   │   │   ├── reports/
│   │   │   │   └── knowledge/
│   │   │   ├── lib/              # utils, api client, ai sdk
│   │   │   ├── hooks/
│   │   │   ├── stores/           # Zustand
│   │   │   └── styles/
│   │   ├── public/
│   │   ├── package.json
│   │   └── next.config.mjs
│   └── api/                      # FastAPI backend
│       ├── app/
│       │   ├── main.py
│       │   ├── settings.py
│       │   ├── deps.py
│       │   ├── router/           # endpoints (auth, conversations, files, kb, reports)
│       │   ├── service/          # business logic
│       │   ├── model/            # SQLAlchemy models
│       │   ├── schema/           # Pydantic schemas
│       │   ├── agent/            # LangGraph agent + skills
│       │   │   ├── graph.py
│       │   │   ├── skills/
│       │   │   ├── prompts/      # versioned prompt md
│       │   │   └── memory.py
│       │   ├── llm/              # LiteLLM wrapper, registry
│       │   ├── rag/              # ingest, retrieve, rerank
│       │   ├── data/             # auto-profile, sandbox runner
│       │   ├── report/           # planner, writer, render
│       │   │   └── templates/    # Jinja2 + CSS per template
│       │   ├── storage/          # S3 client, file ops
│       │   └── workers/          # Celery tasks
│       ├── alembic/              # DB migrations
│       ├── tests/
│       ├── pyproject.toml
│       └── Dockerfile
├── packages/
│   ├── shared-types/             # OpenAPI → TS types auto-gen
│   └── prompts/                  # Prompt library cross-FE/BE (md)
├── infra/
│   ├── docker/
│   │   ├── compose.dev.yml
│   │   └── compose.prod.yml
│   ├── nginx/
│   └── grafana/                  # dashboards json
├── scripts/                      # seed db, migrate, util
├── docs/                         # dokumentasi (17 file + decisions/)
│   ├── 01-vision-and-scope.md
│   ├── 02-tech-stack.md
│   ├── 03-architecture.md
│   ├── 04-features-and-user-flows.md
│   ├── 05-llm-providers.md
│   ├── 06-rag-and-knowledge.md
│   ├── 07-data-analysis-engine.md
│   ├── 08-report-generation.md
│   ├── 09-database-schema.md
│   ├── 10-api-design.md
│   ├── 11-frontend-design.md
│   ├── 12-agent-skills-and-memory.md
│   ├── 13-roadmap-and-milestones.md
│   ├── 14-deployment-and-ops.md
│   ├── 15-security-and-compliance.md
│   ├── 16-skills-and-learning-path.md
│   ├── 17-development-guide.md
│   └── decisions/
│       └── ADR-001-to-006.md
├── .kiro/
│   ├── steering/
│   └── specs/
├── .github/
│   └── workflows/
├── .env.example
├── Makefile
├── MASTERPLAN.md
└── README.md
```

## Aturan Penambahan Folder/File

1. **Module BE baru** → tambah di `apps/api/app/<domain>/` dengan pola `{router, service, model, schema}`.
2. **Komponen FE baru** → group by domain di `apps/web/src/components/<domain>/`.
3. **Skill agent baru** → tambah file di `apps/api/app/agent/skills/<skill_name>.py` + register di `skills/__init__.py`.
4. **Prompt baru** → markdown di `apps/api/app/agent/prompts/<id>.v<n>.md` (front-matter untuk metadata).
5. **Template laporan baru** → folder di `apps/api/app/report/templates/<id>/` dengan `meta.yaml`, `layout.html.j2`, `styles.css`.
6. **Migration DB** → `alembic revision -m "..."`.
7. **Halaman frontend baru** → group dalam route `(app)/`, `(auth)/`, atau `(marketing)/`.

## Aturan Penamaan File

- React komponen: `PascalCase.tsx` (`MessageBubble.tsx`)
- Hook: `useFooBar.ts`
- Util: `camelCase.ts`
- Python module: `snake_case.py`
- SQL migration: angka + nama (`20260601_add_reports_table.py`)

## Hindari

- **Tidak boleh** menaruh logic LLM/agent di Next.js — semua via FastAPI.
- **Tidak boleh** akses DB langsung dari Next.js — selalu via API endpoint.
- **Tidak boleh** simpan secret di repo.
- **Tidak boleh** bypass sandbox untuk eksekusi kode user.

## Workflow Branch & PR

- Branch: `feature/<scope>`, `fix/<scope>`, `chore/<scope>`, `docs/<scope>`
- 1 PR fokus 1 hal, deskripsi pakai template (apa, kenapa, cara test)
- Minimal 1 reviewer
- Squash merge ke `main`
