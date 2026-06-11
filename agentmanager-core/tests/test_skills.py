from __future__ import annotations

import pytest

from src.agents.enums import AgentRole
from src.skills.builtin import CodeReviewSkill, DocWriterSkill, ResearchSkill, TesterSkill
from src.skills.registry import SkillRegistry


@pytest.mark.asyncio
async def test_code_review_skill_attributes():
    skill = CodeReviewSkill()
    assert skill.name == "code_review"
    assert skill.agent_role == AgentRole.REVIEWER
    assert "Correctness" in skill.template_prompt
    assert "git" in skill.required_tools


@pytest.mark.asyncio
async def test_doc_writer_skill_attributes():
    skill = DocWriterSkill()
    assert skill.name == "doc_writer"
    assert skill.agent_role == AgentRole.WRITER
    assert "technical writer" in skill.template_prompt.lower()


@pytest.mark.asyncio
async def test_research_skill_attributes():
    skill = ResearchSkill()
    assert skill.name == "research"
    assert skill.agent_role == AgentRole.RESEARCHER
    assert "web_search" in skill.required_tools


@pytest.mark.asyncio
async def test_tester_skill_attributes():
    skill = TesterSkill()
    assert skill.name == "tester"
    assert skill.agent_role == AgentRole.TESTER
    assert "Arrange-Act-Assert" in skill.template_prompt


@pytest.mark.asyncio
async def test_skill_registry_register_and_list():
    registry = SkillRegistry()
    registry.register(CodeReviewSkill())
    registry.register(DocWriterSkill())
    registry.register(ResearchSkill())
    registry.register(TesterSkill())
    all_skills = registry.list_all()
    assert len(all_skills) == 4


@pytest.mark.asyncio
async def test_skill_registry_get_for_role():
    registry = SkillRegistry()
    registry.register(CodeReviewSkill())
    registry.register(DocWriterSkill())
    reviewers = registry.get_for_role(AgentRole.REVIEWER)
    assert len(reviewers) == 1
    assert reviewers[0].name == "code_review"


@pytest.mark.asyncio
async def test_skill_registry_get_by_name():
    registry = SkillRegistry()
    registry.register(CodeReviewSkill())
    skill = registry.get("code_review")
    assert skill is not None
    assert skill.name == "code_review"
    assert registry.get("nonexistent") is None


@pytest.mark.asyncio
async def test_skill_execute():
    skill = CodeReviewSkill()
    result = await skill.execute({"code": "print('hello')", "language": "python"})
    assert "Reviewing" in result
    assert "python" in result


@pytest.mark.asyncio
async def test_skill_to_dict():
    skill = ResearchSkill()
    d = skill.to_dict()
    assert d["name"] == "research"
    assert d["agent_role"] == "researcher"
    assert "web_search" in d["required_tools"]
