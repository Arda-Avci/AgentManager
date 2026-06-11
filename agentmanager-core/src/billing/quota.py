from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import QuotaModel


class QuotaManager:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def set_quota(
        self,
        agent_id: str,
        monthly_token_limit: int = 0,
        monthly_cost_limit: float = 0.0,
    ) -> QuotaModel:
        stmt = select(QuotaModel).where(QuotaModel.agent_id == agent_id)
        result = await self._session.execute(stmt)
        quota = result.scalar_one_or_none()
        if quota:
            quota.monthly_token_limit = monthly_token_limit
            quota.monthly_cost_limit = monthly_cost_limit
        else:
            quota = QuotaModel(
                agent_id=agent_id,
                monthly_token_limit=monthly_token_limit,
                monthly_cost_limit=monthly_cost_limit,
                reset_date=datetime.now(timezone.utc),
            )
            self._session.add(quota)
        await self._session.flush()
        return quota

    async def check_quota(self, agent_id: str) -> dict:
        stmt = select(QuotaModel).where(QuotaModel.agent_id == agent_id)
        result = await self._session.execute(stmt)
        quota = result.scalar_one_or_none()
        if not quota:
            return {"exceeded": False, "reason": "no quota set"}

        token_exceeded = (
            quota.monthly_token_limit > 0
            and quota.current_tokens >= quota.monthly_token_limit
        )
        cost_exceeded = (
            quota.monthly_cost_limit > 0
            and quota.current_cost >= quota.monthly_cost_limit
        )

        if token_exceeded and cost_exceeded:
            return {"exceeded": True, "reason": "token and cost limit exceeded"}
        if token_exceeded:
            return {"exceeded": True, "reason": "token limit exceeded"}
        if cost_exceeded:
            return {"exceeded": True, "reason": "cost limit exceeded"}

        return {"exceeded": False, "reason": "within limits"}

    async def get_remaining(self, agent_id: str) -> dict:
        stmt = select(QuotaModel).where(QuotaModel.agent_id == agent_id)
        result = await self._session.execute(stmt)
        quota = result.scalar_one_or_none()
        if not quota:
            return {
                "remaining_tokens": -1,
                "remaining_cost": -1.0,
                "message": "no quota set",
            }

        rem_tokens = (
            max(0, quota.monthly_token_limit - quota.current_tokens)
            if quota.monthly_token_limit > 0
            else -1
        )
        rem_cost = (
            max(0.0, quota.monthly_cost_limit - quota.current_cost)
            if quota.monthly_cost_limit > 0
            else -1.0
        )
        return {
            "remaining_tokens": rem_tokens,
            "remaining_cost": rem_cost,
            "current_tokens": quota.current_tokens,
            "current_cost": quota.current_cost,
        }
