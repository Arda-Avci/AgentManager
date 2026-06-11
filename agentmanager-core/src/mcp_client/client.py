from __future__ import annotations

import json
from typing import Any

import httpx


class MCPClient:
    def __init__(self, server_url: str = "", timeout: float = 30.0):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._connected = False
        self._capabilities: dict[str, Any] = {}

    async def connect(self, server_url: str | None = None) -> dict[str, Any]:
        if server_url:
            self.server_url = server_url.rstrip("/")
        if not self.server_url:
            raise ValueError("server_url is required")

        self._client = httpx.AsyncClient(timeout=self.timeout)
        resp = await self._client.get(f"{self.server_url}/mcp/health")
        resp.raise_for_status()
        health = resp.json()

        cap_resp = await self._client.get(f"{self.server_url}/mcp/capabilities")
        if cap_resp.status_code == 200:
            self._capabilities = cap_resp.json()

        self._connected = True
        return {"status": "connected", "capabilities": self._capabilities}

    async def list_tools(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = await self._client.get(f"{self.server_url}/mcp/tools")
        resp.raise_for_status()
        return resp.json().get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        self._ensure_connected()
        resp = await self._client.post(
            f"{self.server_url}/mcp/tools/{name}/call",
            json={"arguments": arguments or {}},
        )
        if resp.status_code == 400:
            error_body = resp.json()
            raise ValueError(error_body.get("error", "Bad request"))
        resp.raise_for_status()
        return resp.json().get("result")

    async def stream_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        self._ensure_connected()
        async with self._client.stream(
            "POST",
            f"{self.server_url}/mcp/tools/{name}/stream",
            json={"arguments": arguments or {}},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    yield json.loads(line[6:])

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        self._capabilities = {}

    def _ensure_connected(self) -> None:
        if not self._connected or not self._client:
            raise RuntimeError("MCPClient is not connected. Call connect() first.")
