from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import SessionManager


@pytest.mark.asyncio
async def test_create_session(db_session: AsyncSession):
    sm = SessionManager(db_session)
    session = await sm.get_or_create("chat_123", "telegram")
    assert session.chat_id == "chat_123"
    assert session.platform == "telegram"


@pytest.mark.asyncio
async def test_set_active_agent(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="agent-x")

    sm = SessionManager(db_session)
    session = await sm.set_active_agent("chat_456", agent.id, "telegram")
    assert session.active_agent_id == agent.id

    active = await sm.get_active_agent("chat_456", "telegram")
    assert active == agent.id


@pytest.mark.asyncio
async def test_reuse_session(db_session: AsyncSession):
    sm = SessionManager(db_session)
    s1 = await sm.get_or_create("chat_789", "telegram")
    s2 = await sm.get_or_create("chat_789", "telegram")
    assert s1.id == s2.id


@pytest.mark.asyncio
async def test_update_context(db_session: AsyncSession):
    sm = SessionManager(db_session)
    session = await sm.update_context("chat_ctx", {"key": "value"}, "telegram")
    assert session.context == {"key": "value"}

    s2 = await sm.get_or_create("chat_ctx", "telegram")
    assert s2.context == {"key": "value"}
