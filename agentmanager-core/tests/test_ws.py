from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


def _find_ws_routes():
    from src.main import app
    from fastapi.routing import APIWebSocketRoute

    return [
        r.path for r in app.routes if isinstance(r, APIWebSocketRoute)
    ]


@pytest.mark.asyncio
async def test_ws_logs_route_registered(client, db_session: AsyncSession):
    routes = _find_ws_routes()
    assert "/api/v1/ws/logs/{agent_id}" in routes
