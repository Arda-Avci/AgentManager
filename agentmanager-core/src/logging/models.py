from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow():
    return datetime.now(timezone.utc)


class ThoughtLog(BaseModel):
    agent_id: str
    task_id: str
    thought_type: str = "reasoning"
    content: str = ""
    timestamp: datetime = Field(default_factory=_utcnow)


class ActionLog(BaseModel):
    agent_id: str
    task_id: str
    action_name: str
    params: dict[str, Any] = Field(default_factory=dict)
    result: str = ""
    timestamp: datetime = Field(default_factory=_utcnow)


class ChainEntry(BaseModel):
    type: str = "thought"
    thought: ThoughtLog | None = None
    action: ActionLog | None = None
