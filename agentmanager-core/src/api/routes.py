from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    ChatRequest,
    ChatResponse,
    CronCreate,
    CronResponse,
    DeviceConfirmRequest,
    DeviceConfirmResponse,
    DevicePairRequest,
    DevicePairResponse,
    ProviderCreate,
    ProviderResponse,
    ProviderValidateResponse,
    SessionResponse,
    TaskCreate,
    TaskResponse,
    ToolCallRequest,
    ToolCreate,
    ToolResponse,
)
from src.database.engine import get_session
from src.database.models import ProviderModel, TaskModel
from src.providers.registry import ProviderRegistry
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
async def get_session_route(
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


@router.post("/providers", response_model=ProviderResponse, status_code=201)
async def create_provider(
    body: ProviderCreate,
    session: AsyncSession = Depends(get_session),
    router_: LLMRouter = Depends(lambda: router_),
):
    existing = await session.get(ProviderModel, body.name)
    if existing:
        raise HTTPException(409, f"Provider '{body.name}' already exists")

    config = body.model_dump(exclude={"name", "provider_type"}, exclude_none=True)

    provider_db = ProviderModel(
        name=body.name,
        provider_type=body.provider_type,
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
        config=config.get("config", {}),
    )
    session.add(provider_db)
    await session.flush()

    from src.main import provider_registry

    try:
        instance = provider_registry.create(body.provider_type, body.name, config)
        router_.register_provider(body.name, instance)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return ProviderResponse(
        name=provider_db.name,
        provider_type=provider_db.provider_type,
        is_enabled=provider_db.is_enabled,
        created_at=provider_db.created_at,
    )


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import select

    result = await session.execute(select(ProviderModel).order_by(ProviderModel.created_at.desc()))
    providers = result.scalars().all()
    return [
        ProviderResponse(
            name=p.name,
            provider_type=p.provider_type,
            is_enabled=p.is_enabled,
            created_at=p.created_at,
        )
        for p in providers
    ]


@router.get("/providers/{name}", response_model=ProviderResponse)
async def get_provider(
    name: str, session: AsyncSession = Depends(get_session)
):
    provider_db = await session.get(ProviderModel, name)
    if not provider_db:
        raise HTTPException(404, "Provider not found")
    return ProviderResponse(
        name=provider_db.name,
        provider_type=provider_db.provider_type,
        is_enabled=provider_db.is_enabled,
        created_at=provider_db.created_at,
    )


@router.get("/providers/{name}/validate", response_model=ProviderValidateResponse)
async def validate_provider(
    name: str,
    router_: LLMRouter = Depends(lambda: router_),
):
    provider = router_.get_provider(name)
    if not provider:
        raise HTTPException(404, f"Provider '{name}' not registered")
    try:
        valid = await provider.validate()
        return ProviderValidateResponse(name=name, valid=valid, error=None)
    except Exception as e:
        return ProviderValidateResponse(name=name, valid=False, error=str(e))


@router.get("/providers/types", response_model=list[str])
async def list_provider_types():
    return ProviderRegistry.known_types()


# ── Auth ──────────────────────────────────────────────────────────────
@router.post("/auth/api-key", response_model=ApiKeyCreatedResponse, status_code=201)
async def create_api_key(
    body: ApiKeyCreate, session: AsyncSession = Depends(get_session)
):
    from src.auth.service import AuthService

    svc = AuthService(session)
    raw_key, model = await svc.create_api_key(body.name, body.allowed_agent_ids)
    return ApiKeyCreatedResponse(
        id=model.id,
        name=model.name,
        is_active=model.is_active,
        created_at=model.created_at,
        key=raw_key,
    )


@router.post("/auth/device-pair", response_model=DevicePairResponse, status_code=201)
async def device_pair(
    body: DevicePairRequest, session: AsyncSession = Depends(get_session)
):
    from src.auth.service import AuthService

    svc = AuthService(session)
    token, model = await svc.create_device_pairing(body.name)
    return DevicePairResponse(token=token, device_name=model.device_name or model.name)


@router.post("/auth/device-confirm", response_model=DeviceConfirmResponse)
async def device_confirm(
    body: DeviceConfirmRequest, session: AsyncSession = Depends(get_session)
):
    from src.auth.service import AuthService

    svc = AuthService(session)
    model = await svc.confirm_device_pairing(body.token)
    if not model:
        raise HTTPException(400, "Invalid or expired pairing token")
    return DeviceConfirmResponse(
        id=model.id,
        name=model.name,
        api_key=body.token,
        is_active=model.is_active,
    )


@router.get("/auth/keys", response_model=list[ApiKeyResponse])
async def list_api_keys(session: AsyncSession = Depends(get_session)):
    from src.auth.service import AuthService

    svc = AuthService(session)
    keys = await svc.list_keys()
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            device_name=k.device_name,
            is_active=k.is_active,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.delete("/auth/keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str, session: AsyncSession = Depends(get_session)
):
    from src.auth.service import AuthService

    svc = AuthService(session)
    if not await svc.delete_key(key_id):
        raise HTTPException(404, "API key not found")

# ── Cron Extras ───────────────────────────────────────────────────────
@router.patch("/cron/{job_id}/toggle", response_model=CronResponse)
async def toggle_cron(job_id: str, session: AsyncSession = Depends(get_session)):
    from src.cron import CronRegistry

    cr = CronRegistry(session)
    job = await cr.get_job(job_id)
    if not job:
        raise HTTPException(404, "Cron job not found")
    if job.is_active:
        job = await cr.deactivate_job(job_id)
    else:
        job = await cr.activate_job(job_id)
    return CronResponse(
        id=job.id,
        agent_id=job.agent_id,
        schedule=job.schedule,
        is_active=job.is_active,
        last_triggered=job.last_triggered,
    )


@router.delete("/cron/{job_id}", status_code=204)
async def delete_cron(job_id: str, session: AsyncSession = Depends(get_session)):
    from src.cron import CronRegistry

    cr = CronRegistry(session)
    if not await cr.delete_job(job_id):
        raise HTTPException(404, "Cron job not found")


@router.get("/cron/agent/{agent_id}", response_model=list[CronResponse])
async def list_cron_by_agent(
    agent_id: str, session: AsyncSession = Depends(get_session)
):
    from src.cron import CronRegistry

    cr = CronRegistry(session)
    jobs = await cr.get_jobs_by_agent(agent_id)
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


@router.get("/tools", response_model=list[ToolResponse])
async def list_tools(session: AsyncSession = Depends(get_session)):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(session)
    tools = await registry.list_active()
    return [
        ToolResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            tool_type=t.tool_type,
            mcp_server_url=t.mcp_server_url,
            agent_id=t.agent_id,
            is_active=t.is_active,
            config=t.config,
            created_at=t.created_at,
        )
        for t in tools
    ]


@router.post("/tools", response_model=ToolResponse, status_code=201)
async def create_tool(
    body: ToolCreate, session: AsyncSession = Depends(get_session)
):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(session)
    existing = await registry.get_by_name(body.name)
    if existing:
        raise HTTPException(409, f"Tool '{body.name}' already exists")
    tool = await registry.create_tool(
        name=body.name,
        description=body.description,
        tool_type=body.tool_type,
        mcp_server_url=body.mcp_server_url,
        agent_id=body.agent_id,
        is_active=True,
        config=body.config,
    )
    return ToolResponse(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type,
        mcp_server_url=tool.mcp_server_url,
        agent_id=tool.agent_id,
        is_active=tool.is_active,
        config=tool.config,
        created_at=tool.created_at,
    )


@router.get("/tools/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str, session: AsyncSession = Depends(get_session)
):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(session)
    tool = await registry.get_by_id(tool_id)
    if not tool:
        raise HTTPException(404, "Tool not found")
    return ToolResponse(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type,
        mcp_server_url=tool.mcp_server_url,
        agent_id=tool.agent_id,
        is_active=tool.is_active,
        config=tool.config,
        created_at=tool.created_at,
    )


@router.post("/tools/{tool_id}/call")
async def call_tool(
    tool_id: str,
    body: ToolCallRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(session)
    tool = await registry.get_by_id(tool_id)
    if not tool:
        raise HTTPException(404, "Tool not found")
    if not tool.is_active:
        raise HTTPException(400, "Tool is not active")

    local = registry.get_local(tool.name)
    if local:
        try:
            params = local.parameters(**body.arguments)
        except Exception as e:
            raise HTTPException(400, f"Invalid arguments: {e}")
        result = await local.execute(params)
        return {"result": result}

    if tool.mcp_server_url:
        from src.mcp_client.client import MCPClient

        client = MCPClient(tool.mcp_server_url)
        try:
            await client.connect()
            result = await client.call_tool(tool.name, body.arguments)
            return {"result": result}
        finally:
            await client.disconnect()

    raise HTTPException(400, f"No handler for tool '{tool.name}'")


@router.delete("/tools/{tool_id}", status_code=204)
async def delete_tool(
    tool_id: str, session: AsyncSession = Depends(get_session)
):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(session)
    if not await registry.delete(tool_id):
        raise HTTPException(404, "Tool not found")


@router.websocket("/ws/logs/{agent_id}")
async def ws_logs(websocket: WebSocket, agent_id: str):
    from src.main import app as _app

    mgr = _app.state.ws_manager
    await mgr.connect(agent_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        mgr.disconnect(agent_id, websocket)


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
