from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import UsageModel


class TokenTracker:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def track_usage(
        self,
        agent_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ) -> UsageModel:
        entry = UsageModel(
            agent_id=agent_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def get_usage(
        self,
        agent_id: str,
        period: str = "daily",
    ) -> list[UsageModel]:
        now = datetime.now(timezone.utc)
        if period == "daily":
            since = now - timedelta(days=1)
        elif period == "monthly":
            since = now - timedelta(days=30)
        elif period == "weekly":
            since = now - timedelta(days=7)
        else:
            since = datetime.min

        stmt = (
            select(UsageModel)
            .where(
                UsageModel.agent_id == agent_id,
                UsageModel.created_at >= since,
            )
            .order_by(UsageModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_total_cost(self, agent_id: str) -> float:
        stmt = select(func.coalesce(func.sum(UsageModel.cost), 0.0)).where(
            UsageModel.agent_id == agent_id
        )
        result = await self._session.execute(stmt)
        return float(result.scalar() or 0.0)

    async def get_total_tokens(self, agent_id: str) -> int:
        stmt = select(
            func.coalesce(func.sum(UsageModel.prompt_tokens + UsageModel.completion_tokens), 0)
        ).where(UsageModel.agent_id == agent_id)
        result = await self._session.execute(stmt)
        return int(result.scalar() or 0)
