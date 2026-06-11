from __future__ import annotations

import time
from collections import defaultdict
from typing import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from src.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int | None = None):
        super().__init__(app)
        self._rate_limit = rate_limit or settings.rate_limit_per_minute
        self._buckets: dict[str, tuple[float, int]] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable]
    ):
        if request.url.path in ("/docs", "/openapi.json", "/api/v1/health", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = 60.0

        last_reset, count = self._buckets.get(client_ip, (0.0, 0))
        if now - last_reset > window:
            last_reset = now
            count = 0

        count += 1
        self._buckets[client_ip] = (last_reset, count)

        if count > self._rate_limit:
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after_seconds": int(window - (now - last_reset)),
                },
            )

        return await call_next(request)
