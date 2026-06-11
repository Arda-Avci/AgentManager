from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.command_language import CommandLanguage, ParsedCommand


@pytest.fixture
def cl():
    return CommandLanguage()


class TestCommandLanguage:

    def test_parse_create_agent(self, cl: CommandLanguage):
        cmd = cl.parse("create agent code-agent using claude")
        assert cmd.action == "create_agent"
        assert cmd.name == "code-agent"
        assert cmd.provider == "claude"

    def test_parse_create_agent_minimal(self, cl: CommandLanguage):
        cmd = cl.parse("create agent test-agent")
        assert cmd.action == "create_agent"
        assert cmd.name == "test-agent"
        assert cmd.provider == ""

    def test_parse_ask_agent(self, cl: CommandLanguage):
        cmd = cl.parse("ask code-agent to review PR #42")
        assert cmd.action == "ask_agent"
        assert cmd.agent == "code-agent"
        assert "review PR #42" in cmd.task

    def test_parse_schedule(self, cl: CommandLanguage):
        cmd = cl.parse("schedule daily standup at 9am")
        assert cmd.action == "schedule_task"
        assert cmd.task == "daily standup"
        assert cmd.time == "9am"

    def test_parse_list_agents(self, cl: CommandLanguage):
        cmd = cl.parse("list agents")
        assert cmd.action == "list_agents"

    def test_parse_list_agents_alt(self, cl: CommandLanguage):
        cmd = cl.parse("show all bots")
        assert cmd.action == "list_agents"

    def test_parse_pause(self, cl: CommandLanguage):
        cmd = cl.parse("pause code-agent")
        assert cmd.action == "pause_agent"
        assert cmd.name == "code-agent"

    def test_parse_resume(self, cl: CommandLanguage):
        cmd = cl.parse("resume code-agent")
        assert cmd.action == "resume_agent"
        assert cmd.name == "code-agent"

    def test_parse_delete(self, cl: CommandLanguage):
        cmd = cl.parse("delete code-agent")
        assert cmd.action == "delete_agent"
        assert cmd.name == "code-agent"

    def test_parse_help(self, cl: CommandLanguage):
        cmd = cl.parse("help")
        assert cmd.action == "help"

    def test_parse_unrecognized(self, cl: CommandLanguage):
        cmd = cl.parse("some gibberish command here")
        assert cmd.error == "unrecognized"

    def test_parse_assign_task(self, cl: CommandLanguage):
        cmd = cl.parse("assign code-agent to fix login bug")
        assert cmd.action == "assign_task"
        assert cmd.agent == "code-agent"

    def test_format_error(self, cl: CommandLanguage):
        cmd = ParsedCommand(raw="bad command", error="unrecognized")
        result = cl.format(cmd)
        assert "anlaşılamadı" in result
        assert "help" in result

    def test_format_create_agent(self, cl: CommandLanguage):
        cmd = ParsedCommand(action="create_agent", name="test-agent", provider="claude")
        result = cl.format(cmd)
        assert "create_agent" in result
        assert "test-agent" in result
        assert "claude" in result


@pytest.mark.asyncio
async def test_tg_start_handler(client: AsyncClient):
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_tg_agent_list_integration(client: AsyncClient):
    await client.post("/api/v1/agents", json={"name": "tg-test-agent"})
    resp = await client.get("/api/v1/agents")
    names = [a["name"] for a in resp.json()]
    assert "tg-test-agent" in names


@pytest.mark.asyncio
async def test_tg_agent_switch_integration(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "tg-switch-agent"})
    agent_id = create.json()["id"]
    resp = await client.post(f"/api/v1/session/chat_tg_test/agent/{agent_id}")
    assert resp.status_code == 200
    assert resp.json()["active_agent_id"] == agent_id


@pytest.mark.asyncio
async def test_tg_task_integration(client: AsyncClient):
    create = await client.post("/api/v1/agents", json={"name": "tg-task-agent"})
    agent_id = create.json()["id"]
    await client.post("/api/v1/tasks", json={"agent_id": agent_id, "goal": "tg test goal"})
    resp = await client.get("/api/v1/tasks")
    goals = [t["goal"] for t in resp.json()]
    assert "tg test goal" in goals
