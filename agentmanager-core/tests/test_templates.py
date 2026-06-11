from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient):
    resp = await client.get("/api/v1/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5
    names = [t["name"] for t in data]
    assert "code-reviewer" in names
    assert "doc-writer" in names
    assert "researcher" in names
    assert "tester" in names
    assert "assistant" in names


@pytest.mark.asyncio
async def test_create_agent_from_template(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/from-template",
        json={"template_name": "code-reviewer", "name": "my-reviewer"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "my-reviewer"
    assert data["role"] == "reviewer"


@pytest.mark.asyncio
async def test_create_agent_from_template_with_custom_provider(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/from-template",
        json={
            "template_name": "researcher",
            "name": "custom-researcher",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-3-5-sonnet"


@pytest.mark.asyncio
async def test_create_agent_from_invalid_template(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/from-template",
        json={"template_name": "nonexistent-template", "name": "no-agent"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_template_agent_has_skills_assigned(client: AsyncClient):
    resp = await client.post(
        "/api/v1/agents/from-template",
        json={"template_name": "code-reviewer", "name": "reviewer-with-skills"},
    )
    agent_id = resp.json()["id"]
    resp_skills = await client.get(f"/api/v1/agents/{agent_id}/skills")
    assert resp_skills.status_code == 200
    skill_names = [s["skill_name"] for s in resp_skills.json()]
    assert "code_review" in skill_names
