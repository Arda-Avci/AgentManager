from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.memory.manager import MemoryManager


@pytest.fixture
def agent_id(db_session: AsyncSession) -> str:
    from src.agents.registry import AgentRegistry

    return "test-memory-agent"


@pytest.mark.asyncio
async def test_add_and_get_messages(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="mem-agent-1")

    mm = MemoryManager(db_session)
    msg = await mm.add_message(agent.id, "user", "Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.agent_id == agent.id

    await mm.add_message(agent.id, "assistant", "Hi there!")
    ctx = await mm.get_context(agent.id)
    assert len(ctx) == 2
    assert ctx[0].content == "Hello"
    assert ctx[1].content == "Hi there!"


@pytest.mark.asyncio
async def test_get_context_max_messages(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="mem-agent-2")

    mm = MemoryManager(db_session)
    for i in range(30):
        await mm.add_message(agent.id, "user", f"msg-{i}")

    ctx = await mm.get_context(agent.id, max_messages=10)
    assert len(ctx) == 10
    assert ctx[0].content == "msg-20"


@pytest.mark.asyncio
async def test_summarize_with_func(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="mem-agent-3")

    mm = MemoryManager(db_session, summarize_func=_fake_summarize)

    for i in range(25):
        await mm.add_message(agent.id, "user", f"msg-{i}")

    summary = await mm.summarize(agent.id)
    assert summary == "FAKE_SUMMARY"

    stored = await mm.get_summary(agent.id)
    assert stored == "FAKE_SUMMARY"

    # After summarization, only 20 messages remain
    ctx = await mm.get_context(agent.id, max_messages=100)
    assert len(ctx) == 20


@pytest.mark.asyncio
async def test_summarize_without_func(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="mem-agent-4")

    mm = MemoryManager(db_session)
    await mm.add_message(agent.id, "user", "hello")

    summary = await mm.summarize(agent.id)
    assert summary is None


@pytest.mark.asyncio
async def test_get_summary_nonexistent(db_session: AsyncSession):
    mm = MemoryManager(db_session)
    assert await mm.get_summary("nonexistent") is None


async def _fake_summarize(text: str) -> str:
    return "FAKE_SUMMARY"
