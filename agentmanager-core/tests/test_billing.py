from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.quota import QuotaManager
from src.billing.tracker import TokenTracker


@pytest.fixture
def agent_id():
    return "test-agent-1"


class TestTokenTracker:
    async def test_track_usage(self, db_session: AsyncSession, agent_id: str):
        tracker = TokenTracker(db_session)
        entry = await tracker.track_usage(
            agent_id=agent_id,
            provider="openai",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.015,
        )
        assert entry.agent_id == agent_id
        assert entry.prompt_tokens == 100
        assert entry.completion_tokens == 50
        assert entry.cost == 0.015

    async def test_get_usage_daily(self, db_session: AsyncSession, agent_id: str):
        tracker = TokenTracker(db_session)
        await tracker.track_usage(agent_id, "openai", "gpt-4", 10, 5, 0.002)
        records = await tracker.get_usage(agent_id, period="daily")
        assert len(records) >= 1

    async def test_get_total_cost(self, db_session: AsyncSession, agent_id: str):
        tracker = TokenTracker(db_session)
        await tracker.track_usage(agent_id, "openai", "gpt-4", 10, 5, 0.002)
        await tracker.track_usage(agent_id, "anthropic", "claude-3", 20, 10, 0.005)
        total = await tracker.get_total_cost(agent_id)
        assert total == pytest.approx(0.007, rel=1e-3)

    async def test_get_total_tokens(self, db_session: AsyncSession, agent_id: str):
        tracker = TokenTracker(db_session)
        await tracker.track_usage(agent_id, "openai", "gpt-4", 100, 50, 0.01)
        await tracker.track_usage(agent_id, "anthropic", "claude-3", 200, 100, 0.02)
        total = await tracker.get_total_tokens(agent_id)
        assert total == 450

    async def test_multiple_agents(self, db_session: AsyncSession):
        tracker = TokenTracker(db_session)
        await tracker.track_usage("agent-a", "openai", "gpt-4", 10, 5, 0.002)
        await tracker.track_usage("agent-b", "anthropic", "claude-3", 20, 10, 0.005)
        cost_a = await tracker.get_total_cost("agent-a")
        cost_b = await tracker.get_total_cost("agent-b")
        assert cost_a == pytest.approx(0.002, rel=1e-3)
        assert cost_b == pytest.approx(0.005, rel=1e-3)


class TestQuotaManager:
    async def test_set_and_check_quota(self, db_session: AsyncSession, agent_id: str):
        qm = QuotaManager(db_session)
        quota = await qm.set_quota(agent_id, monthly_token_limit=1000, monthly_cost_limit=10.0)
        assert quota.monthly_token_limit == 1000
        assert quota.monthly_cost_limit == 10.0

        check = await qm.check_quota(agent_id)
        assert check["exceeded"] is False

    async def test_quota_exceeded(self, db_session: AsyncSession):
        qm = QuotaManager(db_session)
        await qm.set_quota("agent-over", monthly_token_limit=100, monthly_cost_limit=1.0)
        from sqlalchemy import select
        from src.database.models import QuotaModel

        stmt = select(QuotaModel).where(QuotaModel.agent_id == "agent-over")
        result = await db_session.execute(stmt)
        q = result.scalar_one()
        q.current_tokens = 150
        q.current_cost = 2.0
        await db_session.flush()

        check = await qm.check_quota("agent-over")
        assert check["exceeded"] is True

    async def test_get_remaining_no_quota(self, db_session: AsyncSession, agent_id: str):
        qm = QuotaManager(db_session)
        remaining = await qm.get_remaining(agent_id)
        assert remaining["remaining_tokens"] == -1
        assert remaining["remaining_cost"] == -1.0

    async def test_get_remaining_with_quota(self, db_session: AsyncSession):
        qm = QuotaManager(db_session)
        await qm.set_quota("agent-quota", monthly_token_limit=1000, monthly_cost_limit=10.0)
        remaining = await qm.get_remaining("agent-quota")
        assert remaining["remaining_tokens"] == 1000
        assert remaining["remaining_cost"] == 10.0
