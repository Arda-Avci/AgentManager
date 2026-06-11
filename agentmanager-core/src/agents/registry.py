from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AgentModel

if TYPE_CHECKING:
    from src.agents.base import BaseAgent


class AgentRegistry:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._cache: dict[str, BaseAgent] = {}

    async def list_agents(self) -> list[AgentModel]:
        result = await self._session.execute(
            select(AgentModel).where(AgentModel.is_active == True)
        )
        return list(result.scalars().all())

    async def get_agent(self, agent_id: str) -> AgentModel | None:
        return await self._session.get(AgentModel, agent_id)

    async def get_agent_by_name(self, name: str) -> AgentModel | None:
        result = await self._session.execute(
            select(AgentModel).where(AgentModel.name == name)
        )
        return result.scalar_one_or_none()

    async def create_agent(self, **kwargs) -> AgentModel:
        agent = AgentModel(**kwargs)
        self._session.add(agent)
        await self._session.flush()
        return agent

    async def update_agent(self, agent_id: str, **kwargs) -> AgentModel | None:
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        for key, value in kwargs.items():
            setattr(agent, key, value)
        await self._session.flush()
        return agent

    async def delete_agent(self, agent_id: str) -> bool:
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        agent.is_active = False
        await self._session.flush()
        return True
