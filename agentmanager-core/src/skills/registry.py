from __future__ import annotations

from src.agents.enums import AgentRole
from src.skills.base import BaseSkill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    def get_for_role(self, role: AgentRole | str) -> list[BaseSkill]:
        if isinstance(role, str):
            role = AgentRole(role)
        return [s for s in self._skills.values() if s.agent_role == role]

    def list_all(self) -> list[BaseSkill]:
        return list(self._skills.values())
