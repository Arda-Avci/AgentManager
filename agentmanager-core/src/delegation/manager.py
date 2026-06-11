from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DelegationModel


class DelegationManager:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def delegate(
        self, from_agent_id: str, to_agent_id: str, task_goal: str
    ) -> DelegationModel:
        delegation = DelegationModel(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            task_goal=task_goal,
            status="pending",
        )
        self._session.add(delegation)
        await self._session.flush()
        return delegation

    async def get_delegations(self, agent_id: str) -> list[DelegationModel]:
        result = await self._session.execute(
            select(DelegationModel)
            .where(DelegationModel.to_agent_id == agent_id)
            .order_by(DelegationModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def complete_delegation(
        self, delegation_id: str, result: str
    ) -> DelegationModel | None:
        delegation = await self._session.get(DelegationModel, delegation_id)
        if not delegation:
            return None
        delegation.status = "completed"
        delegation.result = result
        await self._session.flush()
        return delegation

    async def get_chain(self, agent_id: str) -> list[DelegationModel]:
        result = await self._session.execute(
            select(DelegationModel)
            .where(
                (DelegationModel.from_agent_id == agent_id)
                | (DelegationModel.to_agent_id == agent_id)
            )
            .order_by(DelegationModel.created_at.asc())
        )
        return list(result.scalars().all())
