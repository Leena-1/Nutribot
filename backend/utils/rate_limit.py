from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


@dataclass
class _Counter:
    window_start: float
    count: int


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple fixed-window rate limiter.

    - **Default**: in-memory (single-process). Good for development.
    - **Production**: swap to a Redis-backed limiter to enforce across replicas.
    """

    def __init__(self, app, *, requests_per_minute: int):
        super().__init__(app)
        self._rpm = max(1, int(requests_per_minute))
        self._window_s = 60.0
        self._counters: Dict[Tuple[str, str], _Counter] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Allow health/docs without limits
        path = request.url.path
        if path in ("/", "/health", "/docs", "/openapi.json"):
            return await call_next(request)

        ip = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
        key = (ip, path)

        now = time.time()
        c = self._counters.get(key)
        if c is None or (now - c.window_start) >= self._window_s:
            self._counters[key] = _Counter(window_start=now, count=1)
            return await call_next(request)

        if c.count >= self._rpm:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please try again later.",
                    }
                },
                headers={"Retry-After": "60"},
            )

        c.count += 1
        return await call_next(request)

