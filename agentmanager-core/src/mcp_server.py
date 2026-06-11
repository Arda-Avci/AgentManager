from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.registry import AgentRegistry
from src.database.engine import async_session
from src.database.models import TaskModel
from src.router import LLMRouter

_router: LLMRouter | None = None
mcp_server = FastMCP("AgentManager MCP")


def setup_mcp(router: LLMRouter) -> None:
    global _router
    _router = router


# ── Internal helpers (testable with injected session) ──────────────


async def _list_agents(session: AsyncSession) -> list[dict[str, Any]]:
    registry = AgentRegistry(session)
    agents = await registry.list_agents()
    return [
        {
            "id": a.id,
            "name": a.name,
            "role": a.role,
            "status": a.status,
            "provider": a.provider,
            "model": a.model,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in agents
    ]


async def _get_agent_detail(
    session: AsyncSession, agent_id: str
) -> dict[str, Any] | None:
    registry = AgentRegistry(session)
    agent = await registry.get_agent(agent_id)
    if not agent:
        return None
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "status": agent.status,
        "provider": agent.provider,
        "model": agent.model,
        "system_prompt": agent.system_prompt,
        "is_active": agent.is_active,
        "config": agent.config,
        "fallback_providers": agent.fallback_providers,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
    }


async def _create_agent(
    session: AsyncSession,
    name: str,
    role: str = "assistant",
    provider: str = "openai",
    model: str = "gpt-4o",
    system_prompt: str = "",
) -> dict[str, Any]:
    registry = AgentRegistry(session)
    existing = await registry.get_agent_by_name(name)
    if existing:
        return {"error": f"Agent '{name}' already exists"}
    agent = await registry.create_agent(
        name=name,
        role=role,
        provider=provider,
        model=model,
        system_prompt=system_prompt,
    )
    await session.flush()
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "status": agent.status,
        "provider": agent.provider,
        "model": agent.model,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
    }


async def _assign_task(
    session: AsyncSession, agent_id: str, goal: str
) -> dict[str, Any]:
    registry = AgentRegistry(session)
    agent = await registry.get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    task = TaskModel(agent_id=agent_id, goal=goal)
    session.add(task)
    await session.flush()
    return {
        "id": task.id,
        "agent_id": task.agent_id,
        "goal": task.goal,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


async def _pause_agent(session: AsyncSession, agent_id: str) -> dict[str, Any]:
    registry = AgentRegistry(session)
    agent = await registry.update_agent(agent_id, status="paused")
    if not agent:
        return {"error": "Agent not found"}
    await session.flush()
    return {"id": agent.id, "name": agent.name, "status": agent.status}


async def _resume_agent(session: AsyncSession, agent_id: str) -> dict[str, Any]:
    registry = AgentRegistry(session)
    agent = await registry.update_agent(agent_id, status="idle")
    if not agent:
        return {"error": "Agent not found"}
    await session.flush()
    return {"id": agent.id, "name": agent.name, "status": agent.status}


async def _chat_with_agent(
    session: AsyncSession, agent_id: str, message: str
) -> dict[str, Any]:
    if _router is None:
        return {"error": "LLM Router not initialized"}
    registry = AgentRegistry(session)
    agent = await registry.get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    messages = [
        {
            "role": "system",
            "content": agent.system_prompt or "You are a helpful assistant.",
        },
        {"role": "user", "content": message},
    ]
    try:
        result, used = await _router.route(
            messages,
            primary_provider=agent.provider,
            primary_model=agent.model,
            fallback_chain=agent.fallback_providers,
        )
        return {"response": result, "used_model": used}
    except Exception as e:
        return {"error": str(e)}


# ── FastMCP tool wrappers ─────────────────────────────────────────


@mcp_server.tool()
async def list_agents() -> list[dict[str, Any]]:
    async with async_session() as session:
        return await _list_agents(session)


@mcp_server.tool()
async def get_agent_detail(agent_id: str) -> dict[str, Any] | None:
    async with async_session() as session:
        return await _get_agent_detail(session, agent_id)


@mcp_server.tool()
async def create_agent(
    name: str,
    role: str = "assistant",
    provider: str = "openai",
    model: str = "gpt-4o",
    system_prompt: str = "",
) -> dict[str, Any]:
    async with async_session() as session:
        result = await _create_agent(session, name, role, provider, model, system_prompt)
        await session.commit()
        return result


@mcp_server.tool()
async def assign_task(agent_id: str, goal: str) -> dict[str, Any]:
    async with async_session() as session:
        result = await _assign_task(session, agent_id, goal)
        await session.commit()
        return result


@mcp_server.tool()
async def pause_agent(agent_id: str) -> dict[str, Any]:
    async with async_session() as session:
        result = await _pause_agent(session, agent_id)
        await session.commit()
        return result


@mcp_server.tool()
async def resume_agent(agent_id: str) -> dict[str, Any]:
    async with async_session() as session:
        result = await _resume_agent(session, agent_id)
        await session.commit()
        return result


@mcp_server.tool()
async def chat_with_agent(agent_id: str, message: str) -> dict[str, Any]:
    async with async_session() as session:
        return await _chat_with_agent(session, agent_id, message)
