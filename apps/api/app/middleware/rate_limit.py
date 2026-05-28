import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.settings import settings
from app.service.auth import decode_access_token

# Rate limit configuration
GENERAL_LIMIT = 60  # requests per minute
GENERAL_WINDOW = 60  # seconds
REPORT_LIMIT = 10  # requests per hour
REPORT_WINDOW = 3600  # seconds
CLEANUP_INTERVAL = 300  # cleanup every 5 minutes


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup: float = time.time()

    def _get_user_key(self, request: Request) -> str:
        """Extract user identifier from JWT token or fall back to client IP."""
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = decode_access_token(
                    token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
                )
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except (ValueError, Exception):
                pass

        # Fall back to client IP
        client = request.client
        ip = client.host if client else "unknown"
        return f"ip:{ip}"

    def _is_report_endpoint(self, request: Request) -> bool:
        """Check if request is a report generation endpoint (POST to /api/v1/reports)."""
        return request.method == "POST" and request.url.path.startswith("/api/v1/reports")

    def _cleanup_expired(self):
        """Remove entries older than 1 hour to prevent memory leaks."""
        now = time.time()
        if now - self._last_cleanup < CLEANUP_INTERVAL:
            return

        self._last_cleanup = now
        cutoff = now - 3600  # 1 hour
        keys_to_delete = []
        for key, timestamps in self._requests.items():
            self._requests[key] = [t for t in timestamps if t > cutoff]
            if not self._requests[key]:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self._requests[key]

    def _check_rate_limit(self, key: str, request: Request) -> tuple[bool, int]:
        """Check if request exceeds rate limit. Returns (allowed, retry_after_seconds)."""
        now = time.time()

        if self._is_report_endpoint(request):
            limit = REPORT_LIMIT
            window = REPORT_WINDOW
            bucket_key = f"{key}:report"
        else:
            limit = GENERAL_LIMIT
            window = GENERAL_WINDOW
            bucket_key = f"{key}:general"

        # Filter timestamps within the window
        timestamps = self._requests[bucket_key]
        timestamps = [t for t in timestamps if t > now - window]
        self._requests[bucket_key] = timestamps

        if len(timestamps) >= limit:
            # Calculate retry-after based on oldest request in window
            oldest = min(timestamps)
            retry_after = int(oldest + window - now) + 1
            return False, max(retry_after, 1)

        # Record this request
        timestamps.append(now)
        return True, 0

    async def dispatch(self, request: Request, call_next):
        self._cleanup_expired()

        user_key = self._get_user_key(request)
        allowed, retry_after = self._check_rate_limit(user_key, request)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response
