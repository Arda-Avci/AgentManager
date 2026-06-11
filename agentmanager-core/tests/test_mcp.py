from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp_server import (
    _list_agents,
    _create_agent,
    _get_agent_detail,
    _assign_task,
    _pause_agent,
    _resume_agent,
)


@pytest.mark.asyncio
async def test_mcp_list_agents_empty(client: AsyncClient, db_session: AsyncSession):
    agents = await _list_agents(db_session)
    assert agents == []


@pytest.mark.asyncio
async def test_mcp_create_and_list(client: AsyncClient, db_session: AsyncSession):
    result = await _create_agent(db_session, name="mcp-agent", role="helper")
    await db_session.commit()
    assert "id" in result
    assert result["name"] == "mcp-agent"
    assert result["status"] == "idle"

    agents = await _list_agents(db_session)
    names = [a["name"] for a in agents]
    assert "mcp-agent" in names


@pytest.mark.asyncio
async def test_mcp_create_duplicate(client: AsyncClient, db_session: AsyncSession):
    await _create_agent(db_session, name="dup-agent")
    await db_session.commit()
    result = await _create_agent(db_session, name="dup-agent")
    await db_session.commit()
    assert "error" in result


@pytest.mark.asyncio
async def test_mcp_get_agent_detail(client: AsyncClient, db_session: AsyncSession):
    created = await _create_agent(
        db_session, name="detail-agent", role="analyst", provider="anthropic", model="claude-3"
    )
    await db_session.commit()
    detail = await _get_agent_detail(db_session, created["id"])
    assert detail is not None
    assert detail["name"] == "detail-agent"
    assert detail["role"] == "analyst"
    assert detail["provider"] == "anthropic"
    assert detail["model"] == "claude-3"


@pytest.mark.asyncio
async def test_mcp_get_agent_detail_not_found(
    client: AsyncClient, db_session: AsyncSession
):
    detail = await _get_agent_detail(db_session, "nonexistent")
    assert detail is None


@pytest.mark.asyncio
async def test_mcp_assign_task(client: AsyncClient, db_session: AsyncSession):
    created = await _create_agent(db_session, name="task-agent")
    await db_session.commit()
    task = await _assign_task(db_session, created["id"], "Test goal")
    await db_session.commit()
    assert task["agent_id"] == created["id"]
    assert task["goal"] == "Test goal"
    assert task["status"] == "pending"


@pytest.mark.asyncio
async def test_mcp_assign_task_agent_not_found(
    client: AsyncClient, db_session: AsyncSession
):
    result = await _assign_task(db_session, "bad-id", "goal")
    await db_session.commit()
    assert result["error"] == "Agent not found"


@pytest.mark.asyncio
async def test_mcp_pause_resume_agent(client: AsyncClient, db_session: AsyncSession):
    created = await _create_agent(db_session, name="pause-agent")
    await db_session.commit()

    paused = await _pause_agent(db_session, created["id"])
    await db_session.commit()
    assert paused["status"] == "paused"

    detail = await _get_agent_detail(db_session, created["id"])
    assert detail["status"] == "paused"

    resumed = await _resume_agent(db_session, created["id"])
    await db_session.commit()
    assert resumed["status"] == "idle"


@pytest.mark.asyncio
async def test_mcp_pause_agent_not_found(client: AsyncClient, db_session: AsyncSession):
    result = await _pause_agent(db_session, "bad-id")
    await db_session.commit()
    assert result["error"] == "Agent not found"


@pytest.mark.asyncio
async def test_mcp_resume_agent_not_found(client: AsyncClient, db_session: AsyncSession):
    result = await _resume_agent(db_session, "bad-id")
    await db_session.commit()
    assert result["error"] == "Agent not found"
