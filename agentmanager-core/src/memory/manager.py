from __future__ import annotations

from typing import Awaitable, Callable

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AgentMemoryModel, MessageModel


class MemoryManager:
    def __init__(
        self,
        session: AsyncSession,
        summarize_func: Callable[[str], Awaitable[str]] | None = None,
    ):
        self._session = session
        self._summarize_func = summarize_func

    async def add_message(
        self, agent_id: str, role: str, content: str
    ) -> MessageModel:
        msg = MessageModel(agent_id=agent_id, role=role, content=content)
        self._session.add(msg)
        await self._session.flush()
        return msg

    async def get_context(
        self, agent_id: str, max_messages: int = 20
    ) -> list[MessageModel]:
        result = await self._session.execute(
            select(MessageModel)
            .where(MessageModel.agent_id == agent_id)
            .order_by(MessageModel.created_at.desc())
            .limit(max_messages)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def get_summary(self, agent_id: str) -> str | None:
        result = await self._session.execute(
            select(AgentMemoryModel).where(AgentMemoryModel.agent_id == agent_id)
        )
        memory = result.scalar_one_or_none()
        return memory.summary if memory else None

    async def summarize(self, agent_id: str) -> str | None:
        if not self._summarize_func:
            return None

        messages = await self.get_context(agent_id, max_messages=50)
        existing_summary = await self.get_summary(agent_id)

        lines = [f"Existing summary: {existing_summary or 'None'}"]
        lines.append("")
        lines.append("Recent messages:")
        for m in messages:
            lines.append(f"{m.role}: {m.content}")
        lines.append("")
        lines.append("Provide a concise summary of this conversation so far.")

        summary = await self._summarize_func("\n".join(lines))

        result = await self._session.execute(
            select(AgentMemoryModel).where(AgentMemoryModel.agent_id == agent_id)
        )
        memory = result.scalar_one_or_none()
        if memory:
            memory.summary = summary
        else:
            memory = AgentMemoryModel(agent_id=agent_id, summary=summary)
            self._session.add(memory)
        await self._session.flush()

        # Keep only the most recent 20 messages after summarization
        await self._trim_messages(agent_id, keep=20)

        return summary

    async def _trim_messages(self, agent_id: str, keep: int = 20) -> None:
        subq = (
            select(MessageModel.id)
            .where(MessageModel.agent_id == agent_id)
            .order_by(MessageModel.created_at.desc())
            .limit(keep)
        )
        await self._session.execute(
            delete(MessageModel).where(
                MessageModel.agent_id == agent_id,
                MessageModel.id.notin_(subq),
            )
        )
        await self._session.flush()
