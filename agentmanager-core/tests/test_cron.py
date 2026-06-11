from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cron import CronRegistry


@pytest.mark.asyncio
async def test_create_job(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="cron-agent")

    cr = CronRegistry(db_session)
    job = await cr.create_job(
        agent_id=agent.id,
        schedule="0 9 * * *",
        task_template="Run daily standup",
        plugin="telegram",
    )
    assert job.schedule == "0 9 * * *"
    assert job.plugin == "telegram"
    assert job.is_active is True


@pytest.mark.asyncio
async def test_list_jobs(db_session: AsyncSession):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="list-cron-agent")

    cr = CronRegistry(db_session)
    await cr.create_job(agent_id=agent.id, schedule="0 9 * * *", task_template="Morning")
    await cr.create_job(agent_id=agent.id, schedule="0 18 * * *", task_template="Evening")

    jobs = await cr.list_jobs()
    assert len(jobs) == 2

    telegram_jobs = await cr.list_jobs(plugin="telegram")
    assert len(telegram_jobs) == 0


@pytest.mark.asyncio
async def test_heartbeat_check(db_session: AsyncSession):
    from datetime import datetime, timedelta, timezone

    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(db_session)
    agent = await registry.create_agent(name="hb-agent")

    cr = CronRegistry(db_session)
    job = await cr.create_job(agent_id=agent.id, schedule="0 9 * * *", task_template="HB test")
    job.last_triggered = datetime.now(timezone.utc) - timedelta(hours=2)

    dangling = await cr.heartbeat_check(max_gap_minutes=60)
    assert len(dangling) == 1
    assert dangling[0].id == job.id
