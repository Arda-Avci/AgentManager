from __future__ import annotations

from typing import Any

from src.agents.enums import AgentRole
from src.skills.base import BaseSkill


class CodeReviewSkill(BaseSkill):
    name = "code_review"
    description = "Kod inceleme prosedürü — kalite, güvenlik ve performans açısından kod değerlendirmesi yapar"
    version = "1.0.0"
    agent_role = AgentRole.REVIEWER
    template_prompt = """You are a code reviewer. Analyze code for:
1. Correctness — does the code do what it intends?
2. Security — any vulnerabilities or unsafe patterns?
3. Performance — any obvious inefficiencies?
4. Maintainability — is the code readable and well-structured?
5. Edge cases — are error conditions handled?

Provide a structured review with severity ratings (critical/major/minor/nit)."""
    required_tools = ["git", "file"]

    async def execute(self, context: dict[str, Any]) -> str:
        code = context.get("code", "")
        language = context.get("language", "unknown")
        return f"Reviewing {language} code ({len(code)} chars)..."
