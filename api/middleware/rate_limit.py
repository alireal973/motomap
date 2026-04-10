"""Token-bucket rate limiting middleware."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

DEFAULT_RATE = 60       # requests
DEFAULT_WINDOW = 60     # seconds
AUTH_RATE = 10          # login/register attempts
AUTH_WINDOW = 60

ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/auth/login": (AUTH_RATE, AUTH_WINDOW),
    "/api/auth/register": (AUTH_RATE, AUTH_WINDOW),
    "/api/auth/refresh": (20, 60),
    "/api/weather/current": (30, 60),
    "/api/weather/road-conditions": (30, 60),
    "/api/reports": (30, 60),
}


class _TokenBucket:
    __slots__ = ("rate", "window", "tokens", "last_refill")

    def __init__(self, rate: int, window: int):
        self.rate = rate
        self.window = window
        self.tokens = float(rate)
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.window))
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    @property
    def retry_after(self) -> int:
        return max(1, int((1 - self.tokens) * (self.window / self.rate)))


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_rate: int = DEFAULT_RATE, default_window: int = DEFAULT_WINDOW):
        super().__init__(app)
        self._default_rate = default_rate
        self._default_window = default_window
        self._buckets: dict[str, _TokenBucket] = {}
        self._last_cleanup = time.monotonic()

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_bucket_key(self, ip: str, path: str) -> str:
        for prefix, _ in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return f"{ip}:{prefix}"
        return f"{ip}:default"

    def _get_limits(self, path: str) -> tuple[int, int]:
        for prefix, limits in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return limits
        return self._default_rate, self._default_window

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        ip = self._get_client_ip(request)
        key = self._get_bucket_key(ip, request.url.path)
        rate, window = self._get_limits(request.url.path)

        if key not in self._buckets:
            self._buckets[key] = _TokenBucket(rate, window)

        bucket = self._buckets[key]
        if not bucket.consume():
            logger.warning("Rate limit hit: %s on %s", ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(bucket.retry_after)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))

        if time.monotonic() - self._last_cleanup > 300:
            self._cleanup()

        return response

    def _cleanup(self) -> None:
        now = time.monotonic()
        stale = [k for k, b in self._buckets.items() if now - b.last_refill > b.window * 2]
        for k in stale:
            del self._buckets[k]
        self._last_cleanup = now
