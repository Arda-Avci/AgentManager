from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    ChatRequest,
    ChatResponse,
    CronCreate,
    CronResponse,
    SessionResponse,
    TaskCreate,
    TaskResponse,
)
from src.database.engine import get_session
from src.database.models import TaskModel
from src.router import LLMRouter
from src.session import SessionManager

router = APIRouter(prefix="/api/v1")


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(session: AsyncSession = Depends(get_session)):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    agents = await registry.list_agents()
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            role=a.role,
            status=a.status,
            provider=a.provider,
            model=a.model,
            is_active=a.is_active,
            created_at=a.created_at,
        )
        for a in agents
    ]


@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    body: AgentCreate, session: AsyncSession = Depends(get_session)
):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    existing = await registry.get_agent_by_name(body.name)
    if existing:
        raise HTTPException(409, f"Agent '{body.name}' already exists")
    agent = await registry.create_agent(**body.model_dump())
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        role=agent.role,
        status=agent.status,
        provider=agent.provider,
        model=agent.model,
        is_active=agent.is_active,
        created_at=agent.created_at,
    )


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str, session: AsyncSession = Depends(get_session)
):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    agent = await registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        role=agent.role,
        status=agent.status,
        provider=agent.provider,
        model=agent.model,
        is_active=agent.is_active,
        created_at=agent.created_at,
    )


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    body: AgentUpdate,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    agent = await registry.update_agent(
        agent_id, **{k: v for k, v in body.model_dump().items() if v is not None}
    )
    if not agent:
        raise HTTPException(404, "Agent not found")
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        role=agent.role,
        status=agent.status,
        provider=agent.provider,
        model=agent.model,
        is_active=agent.is_active,
        created_at=agent.created_at,
    )


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str, session: AsyncSession = Depends(get_session)
):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    if not await registry.delete_agent(agent_id):
        raise HTTPException(404, "Agent not found")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    router_: LLMRouter = Depends(lambda: router_),
    session: AsyncSession = Depends(get_session),
):
    from src.agents.registry import AgentRegistry

    registry = AgentRegistry(session)
    agent = await registry.get_agent(body.agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")

    messages = [
        {"role": "system", "content": agent.system_prompt or "You are a helpful assistant."},
        {"role": "user", "content": body.message},
    ]

    result, used = await router_.route(
        messages,
        primary_provider=agent.provider,
        primary_model=agent.model,
        fallback_chain=agent.fallback_providers,
    )
    return ChatResponse(response=result, used_model=used)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import select

    result = await session.execute(select(TaskModel).order_by(TaskModel.created_at.desc()))
    tasks = result.scalars().all()
    return [
        TaskResponse(
            id=t.id,
            agent_id=t.agent_id,
            goal=t.goal,
            status=t.status,
            result=t.result,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreate, session: AsyncSession = Depends(get_session)
):
    task = TaskModel(agent_id=body.agent_id, goal=body.goal, parent_task_id=body.parent_task_id)
    session.add(task)
    await session.flush()
    return TaskResponse(
        id=task.id,
        agent_id=task.agent_id,
        goal=task.goal,
        status=task.status,
        result=task.result,
        created_at=task.created_at,
    )


@router.get("/session/{chat_id}", response_model=SessionResponse)
async def get_session(
    chat_id: str,
    platform: str = "telegram",
    db_session: AsyncSession = Depends(get_session),
):
    sm = SessionManager(db_session)
    s = await sm.get_or_create(chat_id, platform)
    return SessionResponse(
        id=s.id,
        chat_id=s.chat_id,
        platform=s.platform,
        active_agent_id=s.active_agent_id,
    )


@router.post("/session/{chat_id}/agent/{agent_id}", response_model=SessionResponse)
async def set_active_agent(
    chat_id: str,
    agent_id: str,
    platform: str = "telegram",
    db_session: AsyncSession = Depends(get_session),
):
    sm = SessionManager(db_session)
    s = await sm.set_active_agent(chat_id, agent_id, platform)
    return SessionResponse(
        id=s.id,
        chat_id=s.chat_id,
        platform=s.platform,
        active_agent_id=s.active_agent_id,
    )


@router.post("/cron", response_model=CronResponse, status_code=201)
async def create_cron(
    body: CronCreate, session: AsyncSession = Depends(get_session)
):
    from src.cron import CronRegistry

    cr = CronRegistry(session)
    job = await cr.create_job(**body.model_dump())
    return CronResponse(
        id=job.id,
        agent_id=job.agent_id,
        schedule=job.schedule,
        is_active=job.is_active,
        last_triggered=job.last_triggered,
    )


@router.get("/cron", response_model=list[CronResponse])
async def list_cron(
    plugin: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    from src.cron import CronRegistry

    cr = CronRegistry(session)
    jobs = await cr.list_jobs(plugin)
    return [
        CronResponse(
            id=j.id,
            agent_id=j.agent_id,
            schedule=j.schedule,
            is_active=j.is_active,
            last_triggered=j.last_triggered,
        )
        for j in jobs
    ]


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
