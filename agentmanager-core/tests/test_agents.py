from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents",
        json={"name": "test-agent", "role": "assistant", "provider": "openai", "model": "gpt-4o"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-agent"
    assert data["status"] == "idle"


@pytest.mark.asyncio
async def test_create_duplicate_agent(client: AsyncClient):
    await client.post(
        "/api/v1/agents",
        json={"name": "dup-agent"},
    )
    resp = await client.post(
        "/api/v1/agents",
        json={"name": "dup-agent"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    await client.post("/api/v1/agents", json={"name": "agent-a"})
    await client.post("/api/v1/agents", json={"name": "agent-b"})
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient):
    create_resp = await client.post("/api/v1/agents", json={"name": "get-me"})
    agent_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/agents/{agent_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "get-me"


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/agents/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    create_resp = await client.post("/api/v1/agents", json={"name": "delete-me"})
    agent_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/agents/{agent_id}")
    assert resp.status_code == 204
    list_resp = await client.get("/api/v1/agents")
    names = [a["name"] for a in list_resp.json()]
    assert "delete-me" not in names


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
