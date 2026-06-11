from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.agents.enums import AgentRole


class BaseSkill(ABC):
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    agent_role: AgentRole = AgentRole.ASSISTANT
    template_prompt: str = ""
    required_tools: list[str] = []

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> str:
        ...

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "agent_role": self.agent_role.value,
            "required_tools": self.required_tools,
        }
