from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ToolModel
from src.tools.base import BaseTool


@dataclass
class RegisteredTool:
    name: str
    description: str
    tool_type: str
    mcp_server_url: str | None
    agent_id: str | None
    is_active: bool
    config: dict
    instance: BaseTool | None = None
    created_at: datetime | None = None


class MCPToolRegistry:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._local_tools: dict[str, BaseTool] = {}

    def register_local(self, tool: BaseTool) -> None:
        self._local_tools[tool.name] = tool

    def unregister_local(self, name: str) -> None:
        self._local_tools.pop(name, None)

    def get_local(self, name: str) -> BaseTool | None:
        return self._local_tools.get(name)

    def list_local(self) -> list[BaseTool]:
        return list(self._local_tools.values())

    async def create_tool(
        self,
        name: str,
        description: str = "",
        tool_type: str = "builtin",
        mcp_server_url: str | None = None,
        agent_id: str | None = None,
        is_active: bool = True,
        config: dict | None = None,
    ) -> ToolModel:
        model = ToolModel(
            name=name,
            description=description,
            tool_type=tool_type,
            mcp_server_url=mcp_server_url,
            agent_id=agent_id,
            is_active=is_active,
            config=config or {},
        )
        self._session.add(model)
        await self._session.flush()
        return model

    async def get_by_id(self, tool_id: str) -> ToolModel | None:
        return await self._session.get(ToolModel, tool_id)

    async def get_by_name(self, name: str) -> ToolModel | None:
        result = await self._session.execute(
            select(ToolModel).where(ToolModel.name == name)
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> list[ToolModel]:
        result = await self._session.execute(
            select(ToolModel).where(ToolModel.is_active == True)
        )
        return list(result.scalars().all())

    async def list_by_agent(self, agent_id: str) -> list[ToolModel]:
        result = await self._session.execute(
            select(ToolModel).where(ToolModel.agent_id == agent_id, ToolModel.is_active == True)
        )
        return list(result.scalars().all())

    async def assign_to_agent(self, tool_id: str, agent_id: str) -> ToolModel | None:
        tool = await self.get_by_id(tool_id)
        if not tool:
            return None
        tool.agent_id = agent_id
        await self._session.flush()
        return tool

    async def deactivate(self, tool_id: str) -> bool:
        tool = await self.get_by_id(tool_id)
        if not tool:
            return False
        tool.is_active = False
        await self._session.flush()
        return True

    async def delete(self, tool_id: str) -> bool:
        tool = await self.get_by_id(tool_id)
        if not tool:
            return False
        await self._session.delete(tool)
        await self._session.flush()
        return True
