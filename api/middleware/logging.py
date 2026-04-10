"""Request logging middleware with timing."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip and request.client:
            client_ip = request.client.host

        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "[%s] %s %s %s -> 500 (%.1fms)",
                request_id, client_ip, request.method, request.url.path, elapsed,
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id

        log_fn = logger.info if response.status_code < 400 else logger.warning
        if response.status_code >= 500:
            log_fn = logger.error

        log_fn(
            "[%s] %s %s %s -> %d (%.1fms)",
            request_id, client_ip, request.method, request.url.path,
            response.status_code, elapsed,
        )

        return response
