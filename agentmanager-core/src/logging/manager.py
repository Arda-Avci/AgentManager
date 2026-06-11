from __future__ import annotations

from src.features import FeatureFlag, features
from src.logging.models import ActionLog, ChainEntry, ThoughtLog
from src.ws_manager import WebSocketManager


class LogManager:
    def __init__(self, ws_manager: WebSocketManager | None = None):
        self._ws = ws_manager
        self._thoughts: dict[str, list[ThoughtLog]] = {}
        self._actions: dict[str, list[ActionLog]] = {}

    def _chain_key(self, agent_id: str, task_id: str) -> str:
        return f"{agent_id}:{task_id}"

    async def log_thought(self, agent_id: str, task_id: str, thought: ThoughtLog) -> None:
        if not features.is_enabled(FeatureFlag.COT_LOGGING):
            return
        key = self._chain_key(agent_id, task_id)
        self._thoughts.setdefault(key, []).append(thought)
        if self._ws:
            await self._ws.broadcast(
                agent_id,
                "cot:thought",
                {
                    "task_id": task_id,
                    "thought_type": thought.thought_type,
                    "content": thought.content,
                    "timestamp": thought.timestamp.isoformat(),
                },
            )

    async def log_action(self, agent_id: str, task_id: str, action_log: ActionLog) -> None:
        if not features.is_enabled(FeatureFlag.COT_LOGGING):
            return
        key = self._chain_key(agent_id, task_id)
        self._actions.setdefault(key, []).append(action_log)
        if self._ws:
            await self._ws.broadcast(
                agent_id,
                "cot:action",
                {
                    "task_id": task_id,
                    "action_name": action_log.action_name,
                    "params": action_log.params,
                    "result": action_log.result,
                    "timestamp": action_log.timestamp.isoformat(),
                },
            )

    def get_chain(self, agent_id: str, task_id: str) -> list[ChainEntry]:
        key = self._chain_key(agent_id, task_id)
        thoughts = self._thoughts.get(key, [])
        actions = self._actions.get(key, [])
        merged: list[ChainEntry] = []
        for t in thoughts:
            merged.append(ChainEntry(type="thought", thought=t))
        for a in actions:
            merged.append(ChainEntry(type="action", action=a))
        merged.sort(key=lambda e: (e.thought.timestamp if e.thought else e.action.timestamp) if (e.thought or e.action) else _zero())
        return merged

    async def stream_chain(self, agent_id: str, task_id: str) -> None:
        if not self._ws:
            return
        key = self._chain_key(agent_id, task_id)
        for thought in self._thoughts.get(key, []):
            await self._ws.broadcast(
                agent_id,
                "cot:thought",
                {
                    "task_id": task_id,
                    "thought_type": thought.thought_type,
                    "content": thought.content,
                    "timestamp": thought.timestamp.isoformat(),
                },
            )
        for action in self._actions.get(key, []):
            await self._ws.broadcast(
                agent_id,
                "cot:action",
                {
                    "task_id": task_id,
                    "action_name": action.action_name,
                    "params": action.params,
                    "result": action.result,
                    "timestamp": action.timestamp.isoformat(),
                },
            )


def _zero():
    from datetime import datetime, timezone
    return datetime(1970, 1, 1, tzinfo=timezone.utc)
