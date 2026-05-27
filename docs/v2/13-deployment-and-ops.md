# 13 — Deployment & Operations

## 13.1 Lingkungan

| Env | Tujuan | URL contoh |
|---|---|---|
| `local` | Dev di laptop | `http://localhost:3000` |
| `staging` | Pre-prod testing | `https://staging.ureport.ai` |
| `production` | Live user | `https://app.ureport.ai` |

---

## 13.2 Local Development

`docker-compose.dev.yml` mengangkat:
- `postgres:16`
- `redis:7-alpine`
- `qdrant/qdrant:latest`
- `minio/minio:latest` (S3 compatible) + `minio/mc` (init bucket)
- `mailhog` (capture email dev)

Backend & Frontend dijalankan native (faster reload):
```bash
make dev-up        # docker compose up -d
make api-dev       # uvicorn app.main:app --reload
make web-dev       # pnpm dev di apps/web
```

`.env.example` lengkap dicommit. Developer copy ke `.env` & isi key.

---

## 13.3 Staging & Production Pilihan Hosting

### Pilihan A — All-in-1 VPS (Hemat, MVP)
Cocok untuk traffic awal & cost minim.

- VPS 4 vCPU / 8 GB RAM (Hetzner CPX31, Contabo, DigitalOcean) — ~$15/bln
- Docker Compose → service: api, worker, postgres, redis, qdrant, minio, nginx
- Nginx reverse proxy + Let's Encrypt SSL (Caddy alternatif lebih simpel)
- Frontend di Vercel free tier
- Cloudflare R2 untuk file storage (alternatif MinIO)

### Pilihan B — Hybrid (Production-grade)
- Frontend: Vercel
- API + Worker: Railway / Fly.io / Render (~$20–40/bln)
- Postgres: Neon / Supabase managed (free tier ada)
- Redis: Upstash (free tier)
- Qdrant: Qdrant Cloud (free 1GB) atau self-host
- Storage: Cloudflare R2 (cheap, no egress fee)

### Pilihan C — Kubernetes (V2, scale)
- DigitalOcean / GKE / EKS managed cluster
- Helm chart per service
- HPA otomatis scale berdasarkan CPU & queue length
- ArgoCD untuk GitOps

> **Rekomendasi MVP**: Pilihan B (Vercel + Fly.io/Railway + Neon + Upstash + R2).

---

## 13.4 Containerization

### `apps/api/Dockerfile` (multi-stage)
```dockerfile
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangocairo-1.0-0 libpangoft2-1.0-0 \   # WeasyPrint deps
    build-essential curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `apps/web/Dockerfile`
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
RUN pnpm build

FROM node:20-alpine AS run
WORKDIR /app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 13.5 CI/CD (GitHub Actions)

`.github/workflows/ci.yml`:
- Lint (ruff, eslint, prettier)
- Typecheck (mypy, tsc)
- Test (pytest, vitest)
- Build images
- Push ke GHCR
- Deploy staging on push to `main` (auto)
- Deploy prod on tag `v*` (manual approval)

`.github/workflows/cd.yml`:
- SSH deploy ke VPS (rsync + docker compose pull) ATAU
- Trigger deploy via Fly.io / Railway CLI

---

## 13.6 Database Migrations

- **Alembic** (untuk SQLAlchemy)
- File migration ditrack di `apps/api/alembic/versions/`
- Saat deploy: container start jalankan `alembic upgrade head`
- Backup DB sebelum migrate (auto via cron `pg_dump`)

---

## 13.7 Backup Strategy

| Data | Frekuensi | Retensi | Tool |
|---|---|---|---|
| Postgres | Harian + WAL stream | 30 hari | `pg_basebackup` + WAL-G ke R2 |
| Qdrant snapshots | Harian | 14 hari | Qdrant snapshot API |
| S3 / R2 user files | Versioning enabled | 30 hari | bucket policy |
| Redis | Tidak (cache only) | — | — |

---

## 13.8 Monitoring & Alerting

### Stack
- **Logs**: structured JSON → Loki (atau Vercel Logs + Better Stack)
- **Metrics**: Prometheus (FastAPI middleware `prometheus-fastapi-instrumentator`)
- **Traces**: OpenTelemetry → Tempo / Jaeger
- **Dashboards**: Grafana
- **Frontend errors**: Sentry (free tier)
- **Uptime**: Better Stack / UptimeRobot

### Alerts (PagerDuty / Discord webhook)
- API P95 latency > 2s (5 min)
- Error rate > 1% (5 min)
- Queue length > 100 (Celery report jobs)
- Disk usage > 80%
- LLM cost spike > $10/hour

---

## 13.9 Secrets Management

- Dev: `.env` (gitignored)
- Staging/Prod:
  - GitHub Actions Secrets (untuk CI)
  - Runtime: env var via host (Fly secrets / Railway vars)
  - V2: Doppler / Infisical
- **Tidak pernah commit secret** — pre-commit hook (`detect-secrets`)

---

## 13.10 Estimasi Biaya Bulanan

### Skenario "MVP Hemat" (~100 active user)
| Item | Provider | Biaya |
|---|---|---|
| Frontend | Vercel Hobby | $0 |
| API + Worker | Fly.io machine 1GB | $5–15 |
| Postgres | Neon free → starter | $0–19 |
| Redis | Upstash free | $0 |
| Qdrant | Qdrant Cloud free | $0 |
| Storage | Cloudflare R2 (50GB) | $0.75 |
| Domain | namecheap | $1 |
| LLM | Groq + Gemini Flash mostly | $20–50 |
| E2B sandbox | $20–50 (atau self-host $0) |
| **Total** | | **~$50–135** |

### Skenario "1.000 active user"
| Item | Biaya |
|---|---|
| Infra (Fly + Neon paid + Upstash paid) | $80–150 |
| LLM (Groq + Cerebras + Gemini mix) | $200–500 |
| Sandbox | $100–300 (atau self-host $40) |
| Storage | $5–15 |
| Total | **~$400–950** |

---

## 13.11 Disaster Recovery

- RPO target: 1 jam (Postgres WAL streaming)
- RTO target: 2 jam (re-deploy container + restore DB)
- Drill: setiap kuartal, test restore staging dari backup terbaru.

---

## 13.12 Health Check Endpoints

| Path | Cek |
|---|---|
| `GET /healthz` | Liveness (return 200 selalu) |
| `GET /readyz` | Readiness (cek DB, Redis, Qdrant, S3) |
| `GET /metrics` | Prometheus exposition |

---

## 13.13 Deployment Checklist

Sebelum first prod deploy:
- [ ] DNS + HTTPS
- [ ] Backup pertama berhasil
- [ ] Restore drill sukses
- [ ] Monitoring & alert wired
- [ ] Sentry, log shipping aktif
- [ ] Privacy policy + ToS publish
- [ ] Secret rotation policy ditulis
- [ ] Rate limit aktif & teruji
- [ ] LLM provider key punya budget cap
- [ ] Smoke test end-to-end semua user journey
