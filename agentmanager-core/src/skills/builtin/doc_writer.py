from __future__ import annotations

from typing import Any

from src.agents.enums import AgentRole
from src.skills.base import BaseSkill


class DocWriterSkill(BaseSkill):
    name = "doc_writer"
    description = "Dokümantasyon yazma — teknik doküman, API referansı ve kullanım kılavuzu oluşturur"
    version = "1.0.0"
    agent_role = AgentRole.WRITER
    template_prompt = """You are a technical writer. When writing documentation:
1. Know your audience — assume the reader's skill level
2. Be precise and unambiguous
3. Include code examples where helpful
4. Structure with clear headings and sections
5. Document edge cases and error scenarios"""
    required_tools = ["file"]

    async def execute(self, context: dict[str, Any]) -> str:
        topic = context.get("topic", "untitled")
        doc_type = context.get("doc_type", "general")
        return f"Writing {doc_type} documentation about '{topic}'..."
