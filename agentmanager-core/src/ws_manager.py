from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, agent_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(agent_id, set()).add(ws)

    def disconnect(self, agent_id: str, ws: WebSocket) -> None:
        self._connections.get(agent_id, set()).discard(ws)

    async def broadcast(self, agent_id: str, event: str, data: dict[str, Any]) -> None:
        message = json.dumps({"event": event, "data": data})
        for ws in self._connections.get(agent_id, set()).copy():
            try:
                await ws.send_text(message)
            except Exception:
                self._connections[agent_id].discard(ws)

    async def broadcast_all(self, event: str, data: dict[str, Any]) -> None:
        for agent_id in list(self._connections.keys()):
            await self.broadcast(agent_id, event, data)


ws_manager = WebSocketManager()
