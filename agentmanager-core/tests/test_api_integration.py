from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_agent_lifecycle(client: AsyncClient):
    create = await client.post(
        "/api/v1/agents",
        json={
            "name": "lifecycle-agent",
            "role": "tester",
            "provider": "openai",
            "model": "gpt-4o",
        },
    )
    assert create.status_code == 201
    agent_id = create.json()["id"]

    get = await client.get(f"/api/v1/agents/{agent_id}")
    assert get.status_code == 200
    assert get.json()["role"] == "tester"

    update = await client.patch(
        f"/api/v1/agents/{agent_id}", json={"status": "paused"}
    )
    assert update.status_code == 200
    assert update.json()["status"] == "paused"

    delete = await client.delete(f"/api/v1/agents/{agent_id}")
    assert delete.status_code == 204

    get2 = await client.get(f"/api/v1/agents/{agent_id}")
    assert get2.status_code == 200
    assert get2.json()["is_active"] is False


@pytest.mark.asyncio
async def test_task_create_and_query(client: AsyncClient):
    create = await client.post(
        "/api/v1/agents", json={"name": "task-integration-agent"}
    )
    agent_id = create.json()["id"]

    t1 = await client.post(
        "/api/v1/tasks", json={"agent_id": agent_id, "goal": "integration goal 1"}
    )
    assert t1.status_code == 201
    t1_id = t1.json()["id"]

    t2 = await client.post(
        "/api/v1/tasks", json={"agent_id": agent_id, "goal": "integration goal 2"}
    )
    assert t2.status_code == 201

    queue = await client.get(f"/api/v1/tasks/queue/{agent_id}")
    data = queue.json()
    assert len(data) == 2
    ids = [t["id"] for t in data]
    assert t1_id in ids


@pytest.mark.asyncio
async def test_provider_registration_and_validation(client: AsyncClient):
    from src.main import app

    app.state.auth_enabled = False

    types_resp = await client.get("/api/v1/providers/types")
    assert types_resp.status_code == 200
    types = types_resp.json()
    assert isinstance(types, list)
    assert "openai" in types
    assert "mock" in types

    providers_resp = await client.get("/api/v1/providers")
    assert providers_resp.status_code == 200


@pytest.mark.asyncio
async def test_tool_crud_flow(client: AsyncClient):
    t1 = await client.post(
        "/api/v1/tools",
        json={
            "name": "integration-websearch",
            "description": "test web search tool",
            "tool_type": "builtin",
        },
    )
    assert t1.status_code == 201
    tool_id = t1.json()["id"]

    list_resp = await client.get("/api/v1/tools")
    assert list_resp.status_code == 200
    names = [t["name"] for t in list_resp.json()]
    assert "integration-websearch" in names

    get_resp = await client.get(f"/api/v1/tools/{tool_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "integration-websearch"

    delete_resp = await client.delete(f"/api/v1/tools/{tool_id}")
    assert delete_resp.status_code == 204

    get_resp2 = await client.get(f"/api/v1/tools/{tool_id}")
    assert get_resp2.status_code == 404


@pytest.mark.asyncio
async def test_delegation_flow(client: AsyncClient):
    a1 = await client.post("/api/v1/agents", json={"name": "delegator-agent"})
    a2 = await client.post("/api/v1/agents", json={"name": "worker-agent"})
    a1_id = a1.json()["id"]
    a2_id = a2.json()["id"]

    delegate = await client.post(
        f"/api/v1/agents/{a1_id}/delegate",
        json={"to_agent_id": a2_id, "task_goal": "Please process this task"},
    )
    assert delegate.status_code == 201
    delegation_id = delegate.json()["id"]

    chain = await client.get(f"/api/v1/agents/{a1_id}/delegation-chain")
    assert chain.status_code == 200
    assert len(chain.json()) == 1

    complete = await client.post(
        f"/api/v1/delegations/{delegation_id}/complete",
        json={"result": "Task completed successfully"},
    )
    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_cron_integration(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "cron-int-agent"})
    agent_id = create.json()["id"]

    cron = await client.post(
        "/api/v1/cron",
        json={
            "agent_id": agent_id,
            "schedule": "0 9 * * *",
            "task_template": "Daily report",
        },
    )
    assert cron.status_code == 201
    cron_id = cron.json()["id"]

    toggle = await client.patch(f"/api/v1/cron/{cron_id}/toggle")
    assert toggle.status_code == 200
    assert toggle.json()["is_active"] is False

    agent_crons = await client.get(f"/api/v1/cron/agent/{agent_id}")
    assert agent_crons.status_code == 200
    assert len(agent_crons.json()) == 1
