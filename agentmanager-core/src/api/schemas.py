from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    role: str = "assistant"
    system_prompt: str = ""
    provider: str = "openai"
    model: str = "gpt-4o"
    fallback_providers: list[dict] = []
    config: dict = {}


class AgentUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    system_prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    fallback_providers: list[dict] | None = None
    config: dict | None = None
    status: str | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    status: str
    provider: str
    model: str
    is_active: bool
    created_at: datetime


class TaskCreate(BaseModel):
    agent_id: str
    goal: str
    parent_task_id: str | None = None


class TaskResponse(BaseModel):
    id: str
    agent_id: str
    goal: str
    status: str
    result: str | None
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    chat_id: str
    platform: str
    active_agent_id: str | None


class CronCreate(BaseModel):
    agent_id: str
    schedule: str
    task_template: str
    plugin: str = "core"


class CronResponse(BaseModel):
    id: str
    agent_id: str
    schedule: str
    is_active: bool
    last_triggered: datetime | None


class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    tool_type: str = "builtin"
    mcp_server_url: str | None = None
    agent_id: str | None = None
    config: dict = {}


class ToolResponse(BaseModel):
    id: str
    name: str
    description: str
    tool_type: str
    mcp_server_url: str | None
    agent_id: str | None
    is_active: bool
    config: dict
    created_at: datetime


class ToolCallRequest(BaseModel):
    arguments: dict = {}


class ChatRequest(BaseModel):
    agent_id: str
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    used_model: str


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    allowed_agent_ids: list[str] = []


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    device_name: str | None = None
    is_active: bool
    created_at: datetime


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str


class DevicePairRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class DevicePairResponse(BaseModel):
    token: str
    device_name: str


class DeviceConfirmRequest(BaseModel):
    token: str


class DeviceConfirmResponse(BaseModel):
    id: str
    name: str
    api_key: str
    is_active: bool


class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    provider_type: str = Field(..., min_length=1, max_length=32)
    api_key: str | None = None
    base_url: str | None = None
    config: dict = Field(default_factory=dict)


class ProviderUpdate(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    config: dict | None = None
    is_enabled: bool | None = None


class ProviderResponse(BaseModel):
    name: str
    provider_type: str
    is_enabled: bool
    created_at: datetime


class ProviderValidateResponse(BaseModel):
    name: str
    valid: bool
    error: str | None = None
