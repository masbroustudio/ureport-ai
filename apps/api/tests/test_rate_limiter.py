import time

import pytest

from app.middleware.rate_limit import GENERAL_LIMIT, REPORT_LIMIT, RateLimitMiddleware


def _find_rate_limiter():
    """Find the RateLimitMiddleware instance in the app's middleware stack."""
    from app.main import app

    stack = app.middleware_stack
    while stack is not None:
        if isinstance(stack, RateLimitMiddleware):
            return stack
        stack = getattr(stack, "app", None)
    return None


# The test client uses ASGITransport which sets client host to 127.0.0.1
CLIENT_IP_KEY = "ip:127.0.0.1"


@pytest.fixture(autouse=True)
async def reset_rate_limiter(client):
    """Reset rate limiter state between tests.

    Depends on client fixture to ensure middleware stack is built.
    """
    # Make a request to ensure middleware stack is initialized
    await client.get("/healthz")

    rate_limiter = _find_rate_limiter()
    if rate_limiter:
        rate_limiter._requests.clear()
    yield
    if rate_limiter:
        rate_limiter._requests.clear()


async def test_normal_request_passes(client):
    """Test that normal requests pass through without rate limiting."""
    response = await client.get("/healthz")
    assert response.status_code == 200


async def test_exceeding_general_limit_returns_429(client):
    """Test that exceeding 60 requests/min returns 429 with Retry-After."""
    rate_limiter = _find_rate_limiter()
    assert rate_limiter is not None

    # Pre-fill the bucket with timestamps to simulate reaching the limit
    now = time.time()
    bucket_key = f"{CLIENT_IP_KEY}:general"
    rate_limiter._requests[bucket_key] = [now - i * 0.5 for i in range(GENERAL_LIMIT)]

    # The next request should be rate limited
    response = await client.get("/healthz")
    assert response.status_code == 429
    assert "retry-after" in response.headers
    body = response.json()
    assert "Rate limit exceeded" in body["detail"]


async def test_report_endpoint_stricter_limit(client):
    """Test that POST /api/v1/reports has a stricter 10/hour limit."""
    rate_limiter = _find_rate_limiter()
    assert rate_limiter is not None

    # Pre-fill the report bucket
    now = time.time()
    bucket_key = f"{CLIENT_IP_KEY}:report"
    rate_limiter._requests[bucket_key] = [now - i * 60 for i in range(REPORT_LIMIT)]

    # The next report request should be rate limited
    response = await client.post("/api/v1/reports/")
    assert response.status_code == 429
    assert "retry-after" in response.headers


async def test_different_users_independent_limits(client):
    """Test that different users have independent rate limits."""
    rate_limiter = _find_rate_limiter()
    assert rate_limiter is not None

    now = time.time()

    # Fill limits for a different user key but NOT for this test client's key
    other_user_key = "user:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee:general"
    rate_limiter._requests[other_user_key] = [now - i * 0.5 for i in range(GENERAL_LIMIT)]

    # The test client (ip:127.0.0.1) should NOT be rate limited
    response = await client.get("/healthz")
    assert response.status_code == 200

    # Now fill the test client's bucket
    bucket_key = f"{CLIENT_IP_KEY}:general"
    rate_limiter._requests[bucket_key] = [now - i * 0.5 for i in range(GENERAL_LIMIT)]

    # Now it should be rate limited
    response = await client.get("/healthz")
    assert response.status_code == 429
