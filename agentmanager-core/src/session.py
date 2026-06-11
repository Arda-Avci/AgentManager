from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import SessionModel


class SessionManager:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_create(self, chat_id: str, platform: str = "telegram") -> SessionModel:
        result = await self._session.execute(
            select(SessionModel).where(
                SessionModel.chat_id == chat_id,
                SessionModel.platform == platform,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            session = SessionModel(chat_id=chat_id, platform=platform)
            self._session.add(session)
            await self._session.flush()
        return session

    async def set_active_agent(
        self, chat_id: str, agent_id: str, platform: str = "telegram"
    ) -> SessionModel:
        session = await self.get_or_create(chat_id, platform)
        session.active_agent_id = agent_id
        await self._session.flush()
        return session

    async def get_active_agent(
        self, chat_id: str, platform: str = "telegram"
    ) -> str | None:
        session = await self.get_or_create(chat_id, platform)
        return session.active_agent_id

    async def update_context(
        self, chat_id: str, context: dict, platform: str = "telegram"
    ) -> SessionModel:
        session = await self.get_or_create(chat_id, platform)
        session.context = context
        await self._session.flush()
        return session
