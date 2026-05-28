from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.middleware.logging_middleware import LoggingMiddleware, configure_json_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.router import auth, conversations, files, knowledge, reports
from app.router import metrics as metrics_router
from app.settings import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware order: rate_limit (outermost), logging, request_id (innermost)
# Starlette processes them in reverse order of addition, so add innermost last
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Configure structured JSON logging
configure_json_logging()

# Conditionally initialize Sentry
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.APP_ENV,
    )

app.include_router(auth.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(metrics_router.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    checks = {
        "database": "not_configured",
        "redis": "not_configured",
    }

    healthy = all(v == "ok" for v in checks.values())
    status = "ready" if healthy else "unavailable"
    status_code = 200 if healthy else 503

    return JSONResponse(
        content={"status": status, "checks": checks},
        status_code=status_code,
    )
