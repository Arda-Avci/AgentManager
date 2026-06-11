from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_store_set_and_get(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "store-agent"})
    agent_id = create.json()["id"]

    resp = await client.put(
        f"/api/v1/agents/{agent_id}/store/mykey",
        json={"value": "hello world"},
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == "hello world"


@pytest.mark.asyncio
async def test_store_list_keys(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "store-list-agent"})
    agent_id = create.json()["id"]

    await client.put(
        f"/api/v1/agents/{agent_id}/store/key1",
        json={"value": 42},
    )
    await client.put(
        f"/api/v1/agents/{agent_id}/store/key2",
        json={"value": {"nested": True}},
    )

    resp = await client.get(f"/api/v1/agents/{agent_id}/store")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    keys = [e["key"] for e in data]
    assert "key1" in keys
    assert "key2" in keys


@pytest.mark.asyncio
async def test_store_overwrite_value(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "store-overwrite"})
    agent_id = create.json()["id"]

    await client.put(
        f"/api/v1/agents/{agent_id}/store/counter",
        json={"value": 1},
    )
    await client.put(
        f"/api/v1/agents/{agent_id}/store/counter",
        json={"value": 99},
    )

    resp = await client.get(f"/api/v1/agents/{agent_id}/store")
    data = resp.json()
    counter = [e for e in data if e["key"] == "counter"][0]
    assert counter["value"] == 99


@pytest.mark.asyncio
async def test_store_delete_key(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "store-del-agent"})
    agent_id = create.json()["id"]

    await client.put(
        f"/api/v1/agents/{agent_id}/store/temp",
        json={"value": "delete me"},
    )

    resp = await client.delete(f"/api/v1/agents/{agent_id}/store/temp")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/agents/{agent_id}/store")
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_store_delete_nonexistent_key(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "store-nodel"})
    agent_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/agents/{agent_id}/store/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_skill_assignment_via_api(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "skill-assign"})
    agent_id = create.json()["id"]

    resp = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_name": "tester"},
    )
    assert resp.status_code == 201
    assert resp.json()["skill_name"] == "tester"


@pytest.mark.asyncio
async def test_list_skills_api(client: AsyncClient):
    resp = await client.get("/api/v1/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 4
    names = [s["name"] for s in data]
    assert "code_review" in names
    assert "doc_writer" in names
    assert "research" in names
    assert "tester" in names
