from __future__ import annotations

import pytest
from httpx import AsyncClient

from src.logging.manager import LogManager
from src.logging.models import ActionLog, ChainEntry, ThoughtLog


@pytest.mark.asyncio
async def test_log_thought():
    log = LogManager()
    thought = ThoughtLog(agent_id="agent-1", task_id="task-1", thought_type="reasoning", content="I need to research X")
    await log.log_thought("agent-1", "task-1", thought)
    chain = log.get_chain("agent-1", "task-1")
    assert len(chain) == 1
    assert chain[0].type == "thought"
    assert chain[0].thought.content == "I need to research X"


@pytest.mark.asyncio
async def test_log_action():
    log = LogManager()
    action = ActionLog(agent_id="agent-1", task_id="task-1", action_name="research", params={"q": "AI"}, result="Found results")
    await log.log_action("agent-1", "task-1", action)
    chain = log.get_chain("agent-1", "task-1")
    assert len(chain) == 1
    assert chain[0].type == "action"
    assert chain[0].action.action_name == "research"


@pytest.mark.asyncio
async def test_get_chain_returns_entries_in_order():
    log = LogManager()
    t1 = ThoughtLog(agent_id="a1", task_id="t1", thought_type="reasoning", content="Think 1")
    a1 = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={}, result="Done")
    t2 = ThoughtLog(agent_id="a1", task_id="t1", thought_type="criticism", content="Critique")
    await log.log_thought("a1", "t1", t1)
    await log.log_action("a1", "t1", a1)
    await log.log_thought("a1", "t1", t2)
    chain = log.get_chain("a1", "t1")
    assert len(chain) == 3
    assert chain[0].type == "thought"
    assert chain[1].type == "action"
    assert chain[2].type == "thought"


@pytest.mark.asyncio
async def test_empty_chain():
    log = LogManager()
    chain = log.get_chain("nonexistent", "nonexistent")
    assert chain == []


@pytest.mark.asyncio
async def test_chain_route(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/agents",
        json={"name": "chain-agent", "provider": "openai", "model": "gpt-4o"},
    )
    agent_id = create_resp.json()["id"]

    task_resp = await client.post(
        "/api/v1/tasks",
        json={"agent_id": agent_id, "goal": "Chain test"},
    )
    task_id = task_resp.json()["id"]

    await client.post(f"/api/v1/tasks/execute/{task_id}")

    chain_resp = await client.get(f"/api/v1/tasks/{task_id}/chain")
    assert chain_resp.status_code == 200
    data = chain_resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_thought_fields():
    from datetime import datetime, timezone
    thought = ThoughtLog(agent_id="a1", task_id="t1", thought_type="plan", content="Step 1, Step 2")
    assert thought.agent_id == "a1"
    assert thought.task_id == "t1"
    assert thought.thought_type == "plan"
    assert thought.content == "Step 1, Step 2"
    assert isinstance(thought.timestamp, datetime)


@pytest.mark.asyncio
async def test_action_fields():
    action = ActionLog(agent_id="a1", task_id="t1", action_name="write", params={"file": "test.txt"}, result="Written")
    assert action.action_name == "write"
    assert action.params == {"file": "test.txt"}
    assert action.result == "Written"
