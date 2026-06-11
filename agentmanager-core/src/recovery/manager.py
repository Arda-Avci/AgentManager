from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class RecoveryManager:
    def __init__(self, max_restarts: int = 3):
        self._max_restarts = max_restarts
        self._agents: dict[str, dict[str, Any]] = {}

    def register_agent(self, agent_id: str) -> None:
        if agent_id not in self._agents:
            self._agents[agent_id] = {
                "restart_count": 0,
                "last_error": None,
                "last_crash": None,
                "uptime_start": datetime.now(timezone.utc),
                "status": "healthy",
            }

    def on_crash(self, agent_id: str, error: Exception | str) -> dict[str, Any]:
        entry = self._agents.get(agent_id)
        if not entry:
            self.register_agent(agent_id)
            entry = self._agents[agent_id]

        entry["restart_count"] += 1
        entry["last_error"] = str(error)
        entry["last_crash"] = datetime.now(timezone.utc)

        if entry["restart_count"] > self._max_restarts:
            entry["status"] = "dead"
            return {"restarted": False, "status": "dead", "message": "max restarts exceeded"}
        entry["status"] = "recovering"
        entry["uptime_start"] = datetime.now(timezone.utc)
        return {"restarted": True, "status": "recovering", "restart_count": entry["restart_count"]}

    def get_status(self, agent_id: str) -> dict[str, Any]:
        entry = self._agents.get(agent_id)
        if not entry:
            return {"status": "unknown", "message": "agent not registered"}
        uptime = None
        if entry["status"] in ("healthy", "recovering"):
            uptime = (datetime.now(timezone.utc) - entry["uptime_start"]).total_seconds()
        return {
            "status": entry["status"],
            "restart_count": entry["restart_count"],
            "last_error": entry["last_error"],
            "last_crash": entry["last_crash"],
            "uptime_seconds": uptime,
        }
