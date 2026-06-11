from __future__ import annotations

from typing import Any

from src.agents.enums import AgentRole
from src.skills.base import BaseSkill


class TesterSkill(BaseSkill):
    name = "tester"
    description = "Test senaryosu üretme — birim test, entegrasyon testi ve uçtan uca test senaryoları yazar"
    version = "1.0.0"
    agent_role = AgentRole.TESTER
    template_prompt = """You are a QA engineer. When writing tests:
1. Test the happy path first
2. Then test edge cases and error conditions
3. Use descriptive test names that explain the scenario
4. Follow Arrange-Act-Assert pattern
5. Keep tests independent and deterministic"""
    required_tools = ["file"]

    async def execute(self, context: dict[str, Any]) -> str:
        code = context.get("code", "")
        framework = context.get("framework", "pytest")
        return f"Generating {framework} tests for {len(code)} chars of code..."
