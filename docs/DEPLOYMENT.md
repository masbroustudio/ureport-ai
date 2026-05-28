# Deployment Guide - uReport AI

Panduan lengkap untuk deploy uReport AI ke production environment.

## Prerequisites

- **Docker 24+** & **Docker Compose v2**
- Domain name dengan DNS sudah dikonfigurasi
- SSL certificate (atau gunakan Let's Encrypt/certbot)
- API keys untuk LLM providers (minimal satu dari: Groq, Cerebras, Gemini, Sumopod)
- Minimum **4GB RAM**, **2 CPU cores**
- Disk space: minimal 20GB (untuk database, uploads, dan vector storage)

## Quick Start (Docker Compose)

```bash
# 1. Clone repository
git clone https://github.com/masbroustudio/ureport-ai.git
cd ureport-ai

# 2. Copy environment file
cp .env.example .env

# 3. Edit environment variables (lihat section Environment Variables di bawah)
nano .env

# 4. Build dan start semua services
docker compose -f infra/docker/compose.prod.yml up -d --build

# 5. Jalankan database migration
docker compose -f infra/docker/compose.prod.yml exec api alembic upgrade head

# 6. Verifikasi semua services berjalan
docker compose -f infra/docker/compose.prod.yml ps

# 7. Cek health endpoint
curl http://localhost/healthz
```

Setelah semua services berjalan, akses aplikasi di `http://your-domain.com`.

## Environment Variables

Berikut daftar lengkap environment variables yang digunakan:

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | Yes | `development` | Set ke `production` untuk production |
| `APP_DEBUG` | No | `true` | Set ke `false` di production |
| `APP_NAME` | No | `uReport AI API` | Nama aplikasi |
| `APP_VERSION` | No | `0.1.0` | Versi aplikasi |
| `CORS_ORIGINS` | Yes | `http://localhost:3000` | Comma-separated allowed origins |

### Database & Cache

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai` | PostgreSQL connection string |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection string |
| `DB_PASSWORD` | Yes | - | PostgreSQL password (used in compose) |

### Object Storage (S3/MinIO)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `S3_ENDPOINT` | Yes | `http://localhost:9000` | S3-compatible endpoint URL |
| `S3_ACCESS_KEY` | Yes | `minioadmin` | S3 access key |
| `S3_SECRET_KEY` | Yes | `minioadmin123` | S3 secret key |
| `S3_BUCKET_NAME` | No | `ureport-files` | Bucket name for file uploads |
| `MINIO_ROOT_USER` | Yes | `minioadmin` | MinIO root user (for compose) |
| `MINIO_ROOT_PASSWORD` | Yes | `minioadmin123` | MinIO root password (for compose) |

### Vector Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_URL` | Yes | `http://localhost:6333` | Qdrant vector DB endpoint |

### Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | **Yes** | - | Secret key untuk JWT signing. **WAJIB diubah di production** (min 32 karakter). Generate dengan: `openssl rand -hex 32` |

### LLM Providers

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | No* | `""` | API key untuk Groq |
| `CEREBRAS_API_KEY` | No* | `""` | API key untuk Cerebras |
| `GEMINI_API_KEY` | No* | `""` | API key untuk Google Gemini |
| `SUMOPOD_API_KEY` | No* | `""` | API key untuk Sumopod (custom) |
| `SUMOPOD_BASE_URL` | No | `""` | Base URL untuk Sumopod API |

\* Minimal satu LLM provider key harus diisi agar fitur chat dan report berfungsi.

### Monitoring & Observability

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | `""` | Sentry DSN untuk error tracking. Kosongkan untuk disable. |

### Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FILE_STORAGE_PATH` | No | `./storage/uploads` | Path untuk file uploads lokal |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | URL backend API yang diakses frontend (e.g., `http://api:8000` dalam Docker, atau `https://api.your-domain.com` jika terpisah) |

## Database Setup & Migration

### Initial Setup

Database PostgreSQL otomatis dibuat oleh Docker Compose. Untuk menjalankan migrasi pertama kali:

```bash
# Jalankan semua pending migrations
docker compose -f infra/docker/compose.prod.yml exec api alembic upgrade head
```

### Running Migrations

Setelah update kode yang mengandung migrasi baru:

```bash
# Pull kode terbaru
git pull origin main

# Rebuild API container
docker compose -f infra/docker/compose.prod.yml up -d --build api

# Jalankan migrations
docker compose -f infra/docker/compose.prod.yml exec api alembic upgrade head
```

### Creating New Migrations

Untuk development (bukan di production):

```bash
cd apps/api
uv run alembic revision --autogenerate -m "description of change"
```

### Rollback Migration

```bash
# Rollback satu step
docker compose -f infra/docker/compose.prod.yml exec api alembic downgrade -1

# Rollback ke revision tertentu
docker compose -f infra/docker/compose.prod.yml exec api alembic downgrade <revision_id>
```

## Nginx & SSL Configuration

### Default Configuration

File `infra/docker/nginx.conf` sudah dikonfigurasi untuk:
- Reverse proxy `/api/*` ke backend API (port 8000)
- Reverse proxy `/` ke frontend Next.js (port 3000)
- Rate limiting (30 requests/second per IP)
- SSE support (proxy_buffering off)
- Health check dan metrics endpoints

### Setting Up SSL with Certbot

1. Install certbot di host:

```bash
sudo apt-get install -y certbot
```

2. Obtain certificate (pastikan port 80 accessible):

```bash
# Stop nginx dulu
docker compose -f infra/docker/compose.prod.yml stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Start nginx kembali
docker compose -f infra/docker/compose.prod.yml start nginx
```

3. Update `infra/docker/nginx.conf` - uncomment SSL server block dan update domain:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    # ... location blocks ...
}
```

4. Update `compose.prod.yml` nginx volume - uncomment SSL line:

```yaml
nginx:
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Renewing Certificates

Setup auto-renewal via crontab:

```bash
# Add to crontab (crontab -e)
0 3 * * * certbot renew --quiet && docker compose -f /path/to/infra/docker/compose.prod.yml exec nginx nginx -s reload
```

## Backup Strategy

### PostgreSQL Backup

```bash
# Manual backup
docker compose -f infra/docker/compose.prod.yml exec postgres \
  pg_dump -U ureport ureport_ai | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore dari backup
gunzip -c backup_20250101_120000.sql.gz | \
  docker compose -f infra/docker/compose.prod.yml exec -T postgres \
  psql -U ureport ureport_ai
```

**Automated daily backup** (tambahkan ke crontab):

```bash
0 2 * * * docker compose -f /path/to/compose.prod.yml exec -T postgres pg_dump -U ureport ureport_ai | gzip > /backups/pg_$(date +\%Y\%m\%d).sql.gz
```

### MinIO (Object Storage) Backup

Menggunakan MinIO Client (`mc`):

```bash
# Setup alias
mc alias set ureport http://localhost:9000 minioadmin minioadmin123

# Mirror ke backup location
mc mirror ureport/ureport-files /backups/minio/

# Atau sync ke remote S3
mc mirror ureport/ureport-files s3/backup-bucket/ureport-files/
```

Aktifkan versioning untuk protection terhadap accidental deletes:

```bash
mc versioning enable ureport/ureport-files
```

### Qdrant (Vector DB) Backup

Menggunakan Qdrant Snapshot API:

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/ureport_kb/snapshots

# List snapshots
curl http://localhost:6333/collections/ureport_kb/snapshots

# Download snapshot
curl -o qdrant_snapshot.tar http://localhost:6333/collections/ureport_kb/snapshots/<snapshot_name>
```

### Recommended Backup Schedule

| Resource | Frequency | Retention |
|----------|-----------|-----------|
| PostgreSQL | Daily | 30 days |
| MinIO files | Daily (incremental) | 90 days |
| Qdrant snapshots | Weekly | 4 snapshots |
| Full system | Weekly | 4 copies |

## Monitoring

### Health Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /healthz` | Basic health check - returns 200 if API is running |
| `GET /readyz` | Readiness check - verifies database and service connectivity |
| `GET /metrics` | Prometheus-format metrics (request counts, latency) |

### Prometheus Configuration

Tambahkan scrape target di `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ureport-api'
    scrape_interval: 15s
    metrics_path: /metrics
    static_configs:
      - targets: ['api:8000']
```

### Grafana Dashboard Suggestions

Monitor metrics berikut:
- **Request rate** - total requests per second
- **Error rate** - 4xx dan 5xx responses
- **Response latency** - P50, P95, P99 response times
- **Active connections** - concurrent connections
- **Memory usage** - per-container memory consumption
- **CPU usage** - per-container CPU utilization

### Sentry Error Tracking

Set `SENTRY_DSN` di environment variables untuk mengaktifkan error tracking:

```bash
SENTRY_DSN=https://your-key@sentry.io/your-project-id
```

Sentry akan menangkap:
- Unhandled exceptions
- Slow transactions (performance monitoring)
- Request context (user, URL, headers)

### Log Aggregation

API menggunakan structured JSON logging. Logs dapat di-stream ke ELK/Loki:

```bash
# View real-time logs
docker compose -f infra/docker/compose.prod.yml logs -f api

# Export logs to file
docker compose -f infra/docker/compose.prod.yml logs api > api_logs.json
```

Setiap log entry mencakup:
- Timestamp
- Request ID (X-Request-ID header)
- User ID (jika authenticated)
- HTTP method, path, status code
- Response time

## Scaling Considerations

### Horizontal Scaling (API)

Jalankan multiple API instances di belakang nginx:

```yaml
# Di compose.prod.yml, tambahkan replicas
api:
  deploy:
    replicas: 3
```

Atau gunakan nginx upstream dengan multiple servers:

```nginx
upstream api_backend {
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

### Database Scaling

- **Read replicas**: Gunakan untuk analytics queries dan report generation
- **Connection pooling**: Gunakan PgBouncer di depan PostgreSQL
- **Indexing**: Pastikan semua foreign keys dan commonly-queried columns di-index

### Redis Scaling

- **Cluster mode**: Untuk high availability, gunakan Redis Sentinel atau Redis Cluster
- **Separate instances**: Gunakan Redis instance terpisah untuk cache vs queue

### Qdrant Scaling

- **Distributed mode**: Untuk large vector collections (>1M vectors), gunakan Qdrant distributed mode
- **Sharding**: Konfigurasi sharding berdasarkan user atau collection

### CDN for Static Assets

Serve Next.js static assets via CDN:

```nginx
location /_next/static/ {
    proxy_pass http://web_frontend;
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

Atau gunakan CDN seperti Cloudflare/CloudFront di depan nginx.

## Troubleshooting

### Container Logs

```bash
# Semua services
docker compose -f infra/docker/compose.prod.yml logs -f

# Service tertentu
docker compose -f infra/docker/compose.prod.yml logs -f api
docker compose -f infra/docker/compose.prod.yml logs -f web
docker compose -f infra/docker/compose.prod.yml logs -f postgres
```

### Database Connection Issues

**Symptom**: API gagal start, error "connection refused to postgres"

**Solution**:
```bash
# Cek postgres status
docker compose -f infra/docker/compose.prod.yml ps postgres

# Cek postgres logs
docker compose -f infra/docker/compose.prod.yml logs postgres

# Pastikan health check passed
docker compose -f infra/docker/compose.prod.yml exec postgres pg_isready -U ureport
```

### Memory Issues (WeasyPrint)

**Symptom**: PDF generation fails atau container OOM killed

**Solution**:
- Increase container memory limit (minimal 1GB untuk API service)
- Batasi concurrent PDF generation
- Monitor memory usage: `docker stats`

```yaml
# Di compose.prod.yml
api:
  deploy:
    resources:
      limits:
        memory: 2G
```

### Rate Limiting Adjustments

Default rate limits:
- General API: 60 requests/minute per user
- Report generation: 10 requests/hour per user
- Nginx layer: 30 requests/second per IP

Untuk adjust rate limit aplikasi, modifikasi `apps/api/app/middleware/rate_limit.py`.

Untuk adjust nginx rate limit, update `infra/docker/nginx.conf`:

```nginx
# Increase rate
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/s;
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `JWT_SECRET_KEY must be changed` | Default secret di production | Set `JWT_SECRET_KEY` di `.env` |
| `Connection refused to redis` | Redis belum ready | Tunggu health check atau restart redis |
| `Qdrant connection error` | Qdrant belum start | Cek `docker compose logs qdrant` |
| `S3 bucket not found` | Bucket belum dibuat | Buat bucket via MinIO console (port 9001) |
| `CORS error di browser` | `CORS_ORIGINS` tidak mencakup domain | Update `CORS_ORIGINS` di `.env` |
| `502 Bad Gateway` | Backend belum ready | Cek `docker compose logs api` |

### Resetting Everything

Jika perlu reset dari awal:

```bash
# Stop semua
docker compose -f infra/docker/compose.prod.yml down

# Hapus volumes (WARNING: ini menghapus semua data!)
docker compose -f infra/docker/compose.prod.yml down -v

# Rebuild fresh
docker compose -f infra/docker/compose.prod.yml up -d --build
docker compose -f infra/docker/compose.prod.yml exec api alembic upgrade head
```
