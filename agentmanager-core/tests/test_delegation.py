from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delegate_task(client: AsyncClient):
    resp_a = await client.post("/api/v1/agents", json={"name": "agent-a"})
    agent_a = resp_a.json()["id"]
    resp_b = await client.post("/api/v1/agents", json={"name": "agent-b"})
    agent_b = resp_b.json()["id"]

    resp = await client.post(
        f"/api/v1/agents/{agent_a}/delegate",
        json={"to_agent_id": agent_b, "task_goal": "Review my code"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["from_agent_id"] == agent_a
    assert data["to_agent_id"] == agent_b
    assert data["task_goal"] == "Review my code"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_delegations(client: AsyncClient):
    resp_a = await client.post("/api/v1/agents", json={"name": "del-agent-a"})
    agent_a = resp_a.json()["id"]
    resp_b = await client.post("/api/v1/agents", json={"name": "del-agent-b"})
    agent_b = resp_b.json()["id"]

    await client.post(
        f"/api/v1/agents/{agent_a}/delegate",
        json={"to_agent_id": agent_b, "task_goal": "Task 1"},
    )
    await client.post(
        f"/api/v1/agents/{agent_a}/delegate",
        json={"to_agent_id": agent_b, "task_goal": "Task 2"},
    )

    resp = await client.get(f"/api/v1/agents/{agent_b}/delegations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_complete_delegation(client: AsyncClient):
    resp_a = await client.post("/api/v1/agents", json={"name": "compl-agent-a"})
    agent_a = resp_a.json()["id"]
    resp_b = await client.post("/api/v1/agents", json={"name": "compl-agent-b"})
    agent_b = resp_b.json()["id"]

    del_resp = await client.post(
        f"/api/v1/agents/{agent_a}/delegate",
        json={"to_agent_id": agent_b, "task_goal": "Fix bug"},
    )
    del_id = del_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/delegations/{del_id}/complete",
        json={"result": "Bug fixed"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert resp.json()["result"] == "Bug fixed"


@pytest.mark.asyncio
async def test_delegation_chain(client: AsyncClient):
    resp_a = await client.post("/api/v1/agents", json={"name": "chain-agent-a"})
    agent_a = resp_a.json()["id"]
    resp_b = await client.post("/api/v1/agents", json={"name": "chain-agent-b"})
    agent_b = resp_b.json()["id"]
    resp_c = await client.post("/api/v1/agents", json={"name": "chain-agent-c"})
    agent_c = resp_c.json()["id"]

    await client.post(
        f"/api/v1/agents/{agent_a}/delegate",
        json={"to_agent_id": agent_b, "task_goal": "Research topic"},
    )
    await client.post(
        f"/api/v1/agents/{agent_b}/delegate",
        json={"to_agent_id": agent_c, "task_goal": "Write report"},
    )

    resp = await client.get(f"/api/v1/agents/{agent_b}/delegation-chain")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delegate_to_nonexistent_agent(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/nonexistent/delegate",
        json={"to_agent_id": "also-nonexistent", "task_goal": "Test"},
    )
    assert resp.status_code == 404
