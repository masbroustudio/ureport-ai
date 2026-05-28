from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.middleware._metrics_state import get_requests_total, get_uptime_seconds

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Return basic metrics in Prometheus exposition format."""
    requests_total = get_requests_total()
    uptime_seconds = get_uptime_seconds()

    lines = [
        "# HELP requests_total Total number of HTTP requests processed.",
        "# TYPE requests_total counter",
        f"requests_total {requests_total}",
        "",
        "# HELP uptime_seconds Time since the application started in seconds.",
        "# TYPE uptime_seconds gauge",
        f"uptime_seconds {uptime_seconds:.2f}",
        "",
    ]
    return "\n".join(lines)
