from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.keys import hash_key, verify_key
from src.auth.service import AuthService


@pytest.mark.asyncio
async def test_generate_and_verify_key():
    from src.auth.keys import generate_api_key

    key = generate_api_key()
    assert key.startswith("am_")
    assert len(key) > 20

    hashed = hash_key(key)
    assert verify_key(key, hashed) is True
    assert verify_key("wrong", hashed) is False


@pytest.mark.asyncio
async def test_create_api_key(db_session: AsyncSession):
    svc = AuthService(db_session)
    raw_key, model = await svc.create_api_key("test-key")
    assert raw_key.startswith("am_")
    assert model.name == "test-key"
    assert model.is_active is True

    # Verify it can be validated
    found = await svc.validate_api_key(raw_key)
    assert found is not None
    assert found.id == model.id


@pytest.mark.asyncio
async def test_validate_invalid_key(db_session: AsyncSession):
    svc = AuthService(db_session)
    found = await svc.validate_api_key("invalid-key")
    assert found is None


@pytest.mark.asyncio
async def test_list_keys(db_session: AsyncSession):
    svc = AuthService(db_session)
    await svc.create_api_key("key-a")
    await svc.create_api_key("key-b")

    keys = await svc.list_keys()
    assert len(keys) == 2


@pytest.mark.asyncio
async def test_delete_key(db_session: AsyncSession):
    svc = AuthService(db_session)
    raw_key, model = await svc.create_api_key("delete-me")

    assert await svc.delete_key(model.id) is True
    assert await svc.delete_key("nonexistent") is False

    keys = await svc.list_keys()
    assert len(keys) == 0


@pytest.mark.asyncio
async def test_device_pairing_flow(db_session: AsyncSession):
    svc = AuthService(db_session)
    token, model = await svc.create_device_pairing("device-1")
    assert model.is_active is False
    assert model.device_name == "device-1"

    confirmed = await svc.confirm_device_pairing(token)
    assert confirmed is not None
    assert confirmed.is_active is True

    # Re-confirm should fail
    assert await svc.confirm_device_pairing(token) is None


@pytest.mark.asyncio
async def test_device_pairing_invalid_token(db_session: AsyncSession):
    svc = AuthService(db_session)
    assert await svc.confirm_device_pairing("invalid-token") is None


@pytest.mark.asyncio
async def test_create_api_key_with_allowed_agents(db_session: AsyncSession):
    svc = AuthService(db_session)
    _, model = await svc.create_api_key("scoped-key", allowed_agent_ids=["a1", "a2"])
    assert model.allowed_agent_ids == ["a1", "a2"]


@pytest.mark.asyncio
async def test_api_key_endpoints(client: AsyncClient):
    # Create key via API
    resp = await client.post("/api/v1/auth/api-key", json={"name": "api-test"})
    assert resp.status_code == 201
    data = resp.json()
    assert "key" in data
    assert data["name"] == "api-test"
    assert data["is_active"] is True
    key = data["key"]

    # List keys
    resp = await client.get("/api/v1/auth/keys", headers={"X-API-Key": key})
    assert resp.status_code == 200
    keys = resp.json()
    assert len(keys) >= 1

    # Delete key
    resp = await client.delete(
        f"/api/v1/auth/keys/{data['id']}", headers={"X-API-Key": key}
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_auth_middleware_blocks_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_auth_middleware_bypasses_public_paths(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200

    resp = await client.get("/docs")
    assert resp.status_code == 200

    # Auth routes should also be public
    resp = await client.post("/api/v1/auth/api-key", json={"name": "public-test"})
    assert resp.status_code == 201
