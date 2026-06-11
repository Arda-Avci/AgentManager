from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.agents.enums import AgentStatus


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, role: str = "assistant"):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self._status = AgentStatus.IDLE

    @property
    def status(self) -> AgentStatus:
        return self._status

    @status.setter
    def status(self, value: AgentStatus) -> None:
        self._status = value

    @abstractmethod
    async def run(self, task: str, **kwargs: Any) -> str:
        ...

    async def pause(self) -> None:
        self._status = AgentStatus.PAUSED

    async def resume(self) -> None:
        self._status = AgentStatus.RUNNING

    async def stop(self) -> None:
        self._status = AgentStatus.STOPPED
