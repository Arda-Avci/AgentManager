from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    AgentCreate,
    AgentFromTemplate,
    AgentResponse,
    AgentSkillResponse,
    AgentUpdate,
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    AssignSkillRequest,
    ChainEntryResponse,
    ChatRequest,
    ChatResponse,
    ContinuousStartRequest,
    ContinuousStatusResponse,
    CronCreate,
    CronResponse,
    DelegateRequest,
    DelegateResponse,
    DeviceConfirmRequest,
    DeviceConfirmResponse,
    DevicePairRequest,
    DevicePairResponse,
    FeatureFlagResponse,
    FeatureFlagUpdate,
    ProviderCreate,
    ProviderResponse,
    ProviderValidateResponse,
    RepoMapRequest,
    RepoMapResponse,
    RepoMapStoreResponse,
    SessionResponse,
    SkillResponse,
    StoreEntryResponse,
    StoreSetRequest,
    TaskCreate,
    TaskExecuteResponse,
    TaskFromTemplateRequest,
    TaskResponse,
    TaskTemplateResponse,
    TemplateResponse,
    ToolCallRequest,
    ToolCreate,
    ToolResponse,
)
from src.database.engine import get_session
from src.database.models import AgentModel, ProviderModel, TaskModel
from src.features import FeatureFlag, features
from src.logging.detector import LoopDetector
from src.logging.manager import LogManager
from src.logging.models import ActionLog, ThoughtLog
from src.providers.registry import ProviderRegistry
from src.router import LLMRouter
from src.commands import CommandHandler, parse_command
from src.session import SessionManager
from src.tasks.executor import TaskExecutor
from src.tasks.queue import TaskPriority, TaskQueue
from src.ws_manager import ws_manager

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
    cmd = parse_command(body.message)
    if cmd:
        from src.commands import CommandHandler

        sm = SessionManager(session)
        result = await CommandHandler(sm, body.agent_id).handle(cmd)
        return ChatResponse(response=result.response, used_model=result.used_model)

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


@router.get("/providers/types", response_model=list[str])
async def list_provider_types():
    return ProviderRegistry.known_types()


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


# ── Task Queue ─────────────────────────────────────────────────────────
@router.post("/tasks/execute/{task_id}", response_model=TaskExecuteResponse)
async def execute_task(
    task_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(TaskModel, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status != "pending":
        raise HTTPException(400, f"Task already {task.status}")

    task.status = "running"
    await session.flush()

    router_: LLMRouter = request.app.state.llm_router
    executor = TaskExecutor(session, router_, ws_manager)
    result = await executor.execute(task_id)
    return TaskExecuteResponse(id=result.id, status=result.status, result=result.result)


@router.get("/tasks/queue/{agent_id}", response_model=list[TaskResponse])
async def list_agent_queue(
    agent_id: str, session: AsyncSession = Depends(get_session)
):
    q = TaskQueue(session)
    tasks = await q.list_pending(agent_id)
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


# ── Task Templates ─────────────────────────────────────────────────────
@router.get("/tasks/templates", response_model=list[TaskTemplateResponse])
async def list_task_templates():
    from src.tasks.templates import TASK_TEMPLATES

    return [
        TaskTemplateResponse(
            name=t["name"],
            description=t["description"],
            default_goal=t["default_goal"],
            suggested_agent_role=t["suggested_agent_role"],
        )
        for t in TASK_TEMPLATES
    ]


@router.post("/tasks/from-template", response_model=TaskResponse, status_code=201)
async def create_task_from_template(
    body: TaskFromTemplateRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.tasks.templates import TASK_TEMPLATES

    template = next((t for t in TASK_TEMPLATES if t["name"] == body.template_name), None)
    if not template:
        raise HTTPException(404, f"Task template '{body.template_name}' not found")

    from src.database.models import AgentModel

    agent = await session.get(AgentModel, body.agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")

    goal = body.custom_goal or template["default_goal"]
    task = TaskModel(agent_id=body.agent_id, goal=goal)
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


@router.get("/tasks/{task_id}/chain", response_model=list[ChainEntryResponse])
async def get_task_chain(task_id: str):
    log_manager = LogManager()
    chain = log_manager.get_chain("", task_id)
    return [
        ChainEntryResponse(
            type=e.type,
            thought_type=e.thought.thought_type if e.thought else None,
            content=e.thought.content if e.thought else e.action.result if e.action else None,
            action_name=e.action.action_name if e.action else None,
            params=e.action.params if e.action else None,
            result=e.action.result if e.action else None,
            timestamp=(e.thought.timestamp if e.thought else e.action.timestamp) if (e.thought or e.action) else None,
        )
        for e in chain
    ]


# ── Feature Flags ──────────────────────────────────────────────────────
@router.get("/features", response_model=FeatureFlagResponse)
async def list_features():
    return FeatureFlagResponse(flags=features.all_flags())


@router.patch("/features/{flag}", response_model=FeatureFlagResponse)
async def update_feature(flag: str, body: FeatureFlagUpdate):
    if flag not in [f.value for f in FeatureFlag]:
        raise HTTPException(404, f"Unknown feature flag '{flag}'")
    features.set_enabled(flag, body.value)
    return FeatureFlagResponse(flags=features.all_flags())


# ── WebSocket COT Chain ────────────────────────────────────────────────
@router.websocket("/ws/chain/{agent_id}/{task_id}")
async def ws_chain(websocket: WebSocket, agent_id: str, task_id: str):
    await ws_manager.connect(agent_id, websocket)
    log_manager = LogManager(ws_manager)
    try:
        await log_manager.stream_chain(agent_id, task_id)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(agent_id, websocket)


# ── Delegation ──────────────────────────────────────────────────────────
@router.post("/agents/{agent_id}/delegate", response_model=DelegateResponse, status_code=201)
async def delegate_task(
    agent_id: str,
    body: DelegateRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.registry import AgentRegistry
    from src.delegation.manager import DelegationManager

    registry = AgentRegistry(session)
    from_agent = await registry.get_agent(agent_id)
    if not from_agent:
        raise HTTPException(404, "From-agent not found")
    to_agent = await registry.get_agent(body.to_agent_id)
    if not to_agent:
        raise HTTPException(404, "To-agent not found")

    dm = DelegationManager(session)
    delegation = await dm.delegate(agent_id, body.to_agent_id, body.task_goal)
    return DelegateResponse(
        id=delegation.id,
        from_agent_id=delegation.from_agent_id,
        to_agent_id=delegation.to_agent_id,
        task_goal=delegation.task_goal,
        status=delegation.status,
        result=delegation.result,
        created_at=delegation.created_at,
    )


@router.get("/agents/{agent_id}/delegations", response_model=list[DelegateResponse])
async def get_agent_delegations(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.delegation.manager import DelegationManager

    dm = DelegationManager(session)
    delegations = await dm.get_delegations(agent_id)
    return [
        DelegateResponse(
            id=d.id,
            from_agent_id=d.from_agent_id,
            to_agent_id=d.to_agent_id,
            task_goal=d.task_goal,
            status=d.status,
            result=d.result,
            created_at=d.created_at,
        )
        for d in delegations
    ]


@router.post("/delegations/{delegation_id}/complete", response_model=DelegateResponse)
async def complete_delegation(
    delegation_id: str,
    body: dict,
    session: AsyncSession = Depends(get_session),
):
    from src.delegation.manager import DelegationManager

    dm = DelegationManager(session)
    result = body.get("result", "")
    delegation = await dm.complete_delegation(delegation_id, result)
    if not delegation:
        raise HTTPException(404, "Delegation not found")
    return DelegateResponse(
        id=delegation.id,
        from_agent_id=delegation.from_agent_id,
        to_agent_id=delegation.to_agent_id,
        task_goal=delegation.task_goal,
        status=delegation.status,
        result=delegation.result,
        created_at=delegation.created_at,
    )


@router.get("/agents/{agent_id}/delegation-chain", response_model=list[DelegateResponse])
async def get_delegation_chain(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.delegation.manager import DelegationManager

    dm = DelegationManager(session)
    chain = await dm.get_chain(agent_id)
    return [
        DelegateResponse(
            id=d.id,
            from_agent_id=d.from_agent_id,
            to_agent_id=d.to_agent_id,
            task_goal=d.task_goal,
            status=d.status,
            result=d.result,
            created_at=d.created_at,
        )
        for d in chain
    ]


# ── Skills ──────────────────────────────────────────────────────────────
_skill_registry: object | None = None


def _get_skill_registry():
    global _skill_registry
    if _skill_registry is None:
        from src.skills.builtin import CodeReviewSkill, DocWriterSkill, ResearchSkill, TesterSkill
        from src.skills.registry import SkillRegistry

        reg = SkillRegistry()
        reg.register(CodeReviewSkill())
        reg.register(DocWriterSkill())
        reg.register(ResearchSkill())
        reg.register(TesterSkill())
        _skill_registry = reg
    return _skill_registry


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills():
    registry = _get_skill_registry()
    return [
        SkillResponse(
            name=s.name,
            description=s.description,
            version=s.version,
            agent_role=s.agent_role.value,
            required_tools=s.required_tools,
        )
        for s in registry.list_all()
    ]


@router.post("/agents/{agent_id}/skills", response_model=AgentSkillResponse, status_code=201)
async def assign_skill_to_agent(
    agent_id: str,
    body: AssignSkillRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.database.models import AgentSkillModel

    agent = await session.get(AgentModel, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")

    entry = AgentSkillModel(agent_id=agent_id, skill_name=body.skill_name)
    session.add(entry)
    await session.flush()
    return AgentSkillResponse(skill_name=entry.skill_name, created_at=entry.created_at)


@router.get("/agents/{agent_id}/skills", response_model=list[AgentSkillResponse])
async def get_agent_skills(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select

    from src.database.models import AgentSkillModel

    result = await session.execute(
        select(AgentSkillModel).where(AgentSkillModel.agent_id == agent_id)
    )
    return [
        AgentSkillResponse(skill_name=r.skill_name, created_at=r.created_at)
        for r in result.scalars().all()
    ]


# ── Templates ───────────────────────────────────────────────────────────
@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates():
    from src.templates import AGENT_TEMPLATES

    return [
        TemplateResponse(
            name=t["name"],
            role=t["role"],
            description=t["description"],
            default_provider=t["default_provider"],
            default_model=t["default_model"],
            suggested_tools=t["suggested_tools"],
            assigned_skills=t["assigned_skills"],
        )
        for t in AGENT_TEMPLATES
    ]


@router.post("/agents/from-template", response_model=AgentResponse, status_code=201)
async def create_agent_from_template(
    body: AgentFromTemplate,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.registry import AgentRegistry
    from src.templates import AGENT_TEMPLATES

    template = next((t for t in AGENT_TEMPLATES if t["name"] == body.template_name), None)
    if not template:
        raise HTTPException(404, f"Template '{body.template_name}' not found")

    agent_name = body.name or f"{template['name']}-{uuid.uuid4().hex[:8]}"

    registry = AgentRegistry(session)
    existing = await registry.get_agent_by_name(agent_name)
    if existing:
        raise HTTPException(409, f"Agent '{agent_name}' already exists")

    agent = await registry.create_agent(
        name=agent_name,
        role=template["role"],
        system_prompt=template["system_prompt"],
        provider=body.provider or template["default_provider"],
        model=body.model or template["default_model"],
    )

    for skill_name in template["assigned_skills"]:
        from src.database.models import AgentSkillModel

        entry = AgentSkillModel(agent_id=agent.id, skill_name=skill_name)
        session.add(entry)
    await session.flush()

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


# ── Agent Store ─────────────────────────────────────────────────────────
@router.get("/agents/{agent_id}/store", response_model=list[StoreEntryResponse])
async def list_agent_store(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.store import AgentStore

    store = AgentStore(session)
    keys = await store.list_keys(agent_id)
    result = []
    for key in keys:
        value = await store.get(agent_id, key)
        result.append(StoreEntryResponse(key=key, value=value))
    return result


@router.put("/agents/{agent_id}/store/{key}", response_model=StoreEntryResponse)
async def set_agent_store(
    agent_id: str,
    key: str,
    body: StoreSetRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.store import AgentStore

    store = AgentStore(session)
    await store.set(agent_id, key, body.value)
    return StoreEntryResponse(key=key, value=body.value)


@router.delete("/agents/{agent_id}/store/{key}", status_code=204)
async def delete_agent_store_key(
    agent_id: str,
    key: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.store import AgentStore

    store = AgentStore(session)
    if not await store.delete(agent_id, key):
        raise HTTPException(404, "Store key not found")


# ── Billing ──────────────────────────────────────────────────────────────
@router.get("/billing/usage/{agent_id}", response_model=list[dict])
async def get_usage(
    agent_id: str,
    period: str = "daily",
    session: AsyncSession = Depends(get_session),
):
    from src.billing.tracker import TokenTracker

    tracker = TokenTracker(session)
    records = await tracker.get_usage(agent_id, period)
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "provider": r.provider,
            "model": r.model,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "cost": r.cost,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@router.get("/billing/usage/{agent_id}/total")
async def get_total_usage(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.billing.tracker import TokenTracker

    tracker = TokenTracker(session)
    total_cost = await tracker.get_total_cost(agent_id)
    total_tokens = await tracker.get_total_tokens(agent_id)
    return {"agent_id": agent_id, "total_cost": total_cost, "total_tokens": total_tokens}


@router.post("/billing/quota/{agent_id}")
async def set_quota(
    agent_id: str,
    body: dict,
    session: AsyncSession = Depends(get_session),
):
    from src.billing.quota import QuotaManager

    qm = QuotaManager(session)
    quota = await qm.set_quota(
        agent_id,
        monthly_token_limit=body.get("monthly_token_limit", 0),
        monthly_cost_limit=body.get("monthly_cost_limit", 0.0),
    )
    return {
        "agent_id": quota.agent_id,
        "monthly_token_limit": quota.monthly_token_limit,
        "monthly_cost_limit": quota.monthly_cost_limit,
    }


@router.get("/billing/quota/{agent_id}")
async def get_quota(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.billing.quota import QuotaManager

    qm = QuotaManager(session)
    check = await qm.check_quota(agent_id)
    remaining = await qm.get_remaining(agent_id)
    return {"check": check, "remaining": remaining}


# ── Recovery ─────────────────────────────────────────────────────────────
_recovery_manager: object | None = None


def _get_recovery():
    global _recovery_manager
    if _recovery_manager is None:
        from src.recovery.manager import RecoveryManager
        _recovery_manager = RecoveryManager()
    return _recovery_manager


@router.post("/recovery/register/{agent_id}")
async def register_agent_recovery(agent_id: str):
    mgr = _get_recovery()
    mgr.register_agent(agent_id)
    return {"status": "registered", "agent_id": agent_id}


@router.post("/recovery/crash/{agent_id}")
async def report_crash(agent_id: str, body: dict):
    mgr = _get_recovery()
    error = body.get("error", "unknown error")
    result = mgr.on_crash(agent_id, error)
    return result


@router.get("/recovery/status/{agent_id}")
async def get_recovery_status(agent_id: str):
    mgr = _get_recovery()
    return mgr.get_status(agent_id)


# ── Monitoring ───────────────────────────────────────────────────────────
@router.get("/monitoring/metrics")
async def get_metrics():
    from src.monitoring.metrics import get_collector
    return get_collector().get_metrics()


# ── Repo Map ────────────────────────────────────────────────────────────
@router.post("/tools/repo-map", response_model=RepoMapResponse)
async def generate_repo_map(body: RepoMapRequest):
    from src.tools.repo_map import RepoMap

    mapper = RepoMap()
    map_text = mapper.generate_map(body.path, body.depth)
    context = None
    if body.include_signatures:
        context = mapper.get_repo_context(body.path)
    return RepoMapResponse(map=map_text, context=context)


@router.get("/tools/repo-map/{agent_id}", response_model=RepoMapStoreResponse)
async def get_agent_repo_map(
    agent_id: str,
    path: str = ".",
    session: AsyncSession = Depends(get_session),
):
    from src.agents.store import AgentStore

    store = AgentStore(session)
    key = f"repo_map:{path}"
    value = await store.get(agent_id, key)
    return RepoMapStoreResponse(agent_id=agent_id, path=path, map=value)


@router.post("/tools/repo-map/{agent_id}", response_model=RepoMapStoreResponse)
async def save_agent_repo_map(
    agent_id: str,
    body: RepoMapRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.store import AgentStore
    from src.tools.repo_map import RepoMap

    mapper = RepoMap()
    map_text = mapper.generate_map(body.path, body.depth)

    store = AgentStore(session)
    key = f"repo_map:{body.path}"
    await store.set(agent_id, key, map_text)
    return RepoMapStoreResponse(agent_id=agent_id, path=body.path, map=map_text)


# ── Continuous Mode ──────────────────────────────────────────────────
_continuous_instances: dict[str, object] = {}


def _get_continuous(session: AsyncSession) -> object:
    key = id(session)
    if key not in _continuous_instances:
        from src.agents.continuous import ContinuousMode
        _continuous_instances[key] = ContinuousMode(session, None, ws_manager)
    return _continuous_instances[key]


@router.post(
    "/agents/{agent_id}/continuous/start",
    response_model=ContinuousStatusResponse,
    status_code=201,
)
async def continuous_start(
    agent_id: str,
    body: ContinuousStartRequest,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.continuous import ContinuousMode

    cm = ContinuousMode(session, None, ws_manager)
    result = await cm.start(agent_id, body.goal, body.max_iterations)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return ContinuousStatusResponse(**result)


@router.post("/agents/{agent_id}/continuous/stop", response_model=ContinuousStatusResponse)
async def continuous_stop(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.continuous import ContinuousMode

    cm = ContinuousMode(session, None, ws_manager)
    result = await cm.stop(agent_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return ContinuousStatusResponse(**result)


@router.get("/agents/{agent_id}/continuous/status", response_model=ContinuousStatusResponse)
async def continuous_status(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.continuous import ContinuousMode

    cm = ContinuousMode(session, None, ws_manager)
    result = cm.get_status(agent_id)
    return ContinuousStatusResponse(**result)


@router.post("/agents/{agent_id}/continuous/pause", response_model=ContinuousStatusResponse)
async def continuous_pause(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.continuous import ContinuousMode

    cm = ContinuousMode(session, None, ws_manager)
    result = await cm.pause(agent_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return ContinuousStatusResponse(**result)


@router.post("/agents/{agent_id}/continuous/resume", response_model=ContinuousStatusResponse)
async def continuous_resume(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    from src.agents.continuous import ContinuousMode

    cm = ContinuousMode(session, None, ws_manager)
    result = await cm.resume(agent_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return ContinuousStatusResponse(**result)


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
