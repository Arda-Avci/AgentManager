from __future__ import annotations

import hashlib
from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, valid_keys: set[str]):
        super().__init__(app)
        self._valid_hashes = {hashlib.sha256(k.encode()).hexdigest() for k in valid_keys}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable]
    ):
        if request.url.path.startswith(("/docs", "/openapi.json", "/health")):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing X-API-Key header"},
            )

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash not in self._valid_hashes:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"},
            )

        return await call_next(request)


class AgentPartitionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        agent_id = request.path_params.get("agent_id")
        if agent_id and request.method in ("POST", "PUT", "PATCH", "DELETE"):
            api_key = request.headers.get("X-API-Key", "")
            scope = request.scope.get("agent_scope")
            if scope and scope.get("allowed_agents") and agent_id not in scope["allowed_agents"]:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"detail": "Agent access denied"},
                )
        return await call_next(request)
