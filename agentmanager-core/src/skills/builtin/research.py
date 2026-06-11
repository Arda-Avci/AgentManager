from __future__ import annotations

from typing import Any

from src.agents.enums import AgentRole
from src.skills.base import BaseSkill


class ResearchSkill(BaseSkill):
    name = "research"
    description = "Araştırma yapma — web'den bilgi toplar, sentezler ve rapor oluşturur"
    version = "1.0.0"
    agent_role = AgentRole.RESEARCHER
    template_prompt = """You are a research assistant. When researching:
1. Start with broad search then narrow down
2. Cross-reference information from multiple sources
3. Distinguish facts from opinions
4. Note uncertainty and conflicting information
5. Provide a structured summary with sources"""
    required_tools = ["web_search"]

    async def execute(self, context: dict[str, Any]) -> str:
        query = context.get("query", "")
        depth = context.get("depth", "basic")
        return f"Researching '{query}' at {depth} depth..."
