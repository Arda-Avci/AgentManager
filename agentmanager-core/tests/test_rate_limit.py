from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request
from starlette.responses import JSONResponse

from src.api.middleware import RateLimitMiddleware


class TestRateLimitMiddleware:
    @pytest.fixture
    def middleware(self):
        app = Mock()
        return RateLimitMiddleware(app, rate_limit=5)

    @pytest.mark.asyncio
    async def test_allows_requests_under_limit(self, middleware):
        request = Mock(spec=Request)
        request.url.path = "/api/v1/agents"
        request.client.host = "127.0.0.1"
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))

        for _ in range(3):
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_blocks_requests_over_limit(self, middleware):
        request = Mock(spec=Request)
        request.url.path = "/api/v1/agents"
        request.client.host = "10.0.0.1"
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))

        for _ in range(5):
            await middleware.dispatch(request, call_next)

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_skip_public_paths(self, middleware):
        request = Mock(spec=Request)
        request.url.path = "/api/v1/health"
        request.client.host = "10.0.0.2"
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))

        for _ in range(100):
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_different_ips_independent(self, middleware):
        call_next = AsyncMock(return_value=JSONResponse({"ok": True}))

        for ip in ["10.0.0.1", "10.0.0.2", "10.0.0.3"]:
            request = Mock(spec=Request)
            request.url.path = "/api/v1/agents"
            request.client.host = ip
            for _ in range(5):
                resp = await middleware.dispatch(request, call_next)
                assert resp.status_code == 200

            request2 = Mock(spec=Request)
            request2.url.path = "/api/v1/agents"
            request2.client.host = ip
            resp = await middleware.dispatch(request2, call_next)
            assert resp.status_code == 429
