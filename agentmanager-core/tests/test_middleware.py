from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.auth.service import AuthService
from src.database.models import ApiKeyModel
from src.main import app


@pytest.mark.asyncio
async def test_middleware_public_paths_bypass_auth(client: AsyncClient):
    app.state.auth_enabled = True

    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200

    resp = await client.get("/docs")
    assert resp.status_code == 200

    app.state.auth_enabled = False


@pytest.mark.asyncio
async def test_middleware_missing_key_returns_401(client: AsyncClient):
    app.state.auth_enabled = True

    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Missing X-API-Key header"

    app.state.auth_enabled = False


@pytest.mark.asyncio
async def test_middleware_valid_key_passes(client: AsyncClient):
    mock_record = ApiKeyModel(
        id="test-id",
        key_hash="test-hash",
        name="mock-key",
        is_active=True,
        allowed_agent_ids=[],
    )

    app.state.auth_enabled = True

    with patch.object(AuthService, "validate_api_key", return_value=mock_record):
        resp = await client.get(
            "/api/v1/agents", headers={"X-API-Key": "valid-key-test"}
        )
        assert resp.status_code == 200

    app.state.auth_enabled = False


@pytest.mark.asyncio
async def test_middleware_invalid_key_returns_401(client: AsyncClient):
    app.state.auth_enabled = True

    with patch.object(AuthService, "validate_api_key", return_value=None):
        resp = await client.get(
            "/api/v1/agents", headers={"X-API-Key": "invalid-key-xxx"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid API key"

    app.state.auth_enabled = False


@pytest.mark.asyncio
async def test_auth_endpoints_accessible_without_key(client: AsyncClient):
    app.state.auth_enabled = True

    resp = await client.post(
        "/api/v1/auth/api-key", json={"name": "public-create-test"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "key" in data

    app.state.auth_enabled = False


@pytest.mark.asyncio
async def test_device_pairing_endpoint(client: AsyncClient):
    app.state.auth_enabled = True

    resp = await client.post(
        "/api/v1/auth/device-pair", json={"name": "test-device"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["device_name"] == "test-device"

    token = data["token"]
    confirm = await client.post(
        "/api/v1/auth/device-confirm",
        json={"token": token},
    )
    assert confirm.status_code == 200
    assert confirm.json()["is_active"] is True

    app.state.auth_enabled = False
