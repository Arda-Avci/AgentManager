from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AgentStoreModel


class AgentStore:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def set(self, agent_id: str, key: str, value: object) -> AgentStoreModel:
        result = await self._session.execute(
            select(AgentStoreModel).where(
                AgentStoreModel.agent_id == agent_id,
                AgentStoreModel.key == key,
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.value = value
        else:
            entry = AgentStoreModel(agent_id=agent_id, key=key, value=value)
            self._session.add(entry)
        await self._session.flush()
        return entry

    async def get(self, agent_id: str, key: str) -> object | None:
        result = await self._session.execute(
            select(AgentStoreModel).where(
                AgentStoreModel.agent_id == agent_id,
                AgentStoreModel.key == key,
            )
        )
        entry = result.scalar_one_or_none()
        return entry.value if entry else None

    async def delete(self, agent_id: str, key: str) -> bool:
        result = await self._session.execute(
            delete(AgentStoreModel).where(
                AgentStoreModel.agent_id == agent_id,
                AgentStoreModel.key == key,
            )
        )
        await self._session.flush()
        return result.rowcount > 0

    async def list_keys(self, agent_id: str) -> list[str]:
        result = await self._session.execute(
            select(AgentStoreModel.key).where(
                AgentStoreModel.agent_id == agent_id
            ).order_by(AgentStoreModel.created_at)
        )
        return [row[0] for row in result.all()]
