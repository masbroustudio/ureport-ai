from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.router import auth, conversations, files, knowledge, reports
from app.settings import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


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
