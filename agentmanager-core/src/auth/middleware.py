from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from src.database.engine import async_session
from src.auth.service import AuthService

PUBLIC_PATHS = ("/docs", "/openapi.json", "/health", "/api/v1/health", "/api/v1/auth", "/mcp")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable]
    ):
        auth_enabled = getattr(request.app.state, "auth_enabled", True)
        if not auth_enabled:
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing X-API-Key header"},
            )

        async with async_session() as session:
            svc = AuthService(session)
            key_record = await svc.validate_api_key(api_key)
            if not key_record:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid API key"},
                )

            request.scope["agent_scope"] = {
                "key_id": key_record.id,
                "allowed_agents": key_record.allowed_agent_ids or [],
            }

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
