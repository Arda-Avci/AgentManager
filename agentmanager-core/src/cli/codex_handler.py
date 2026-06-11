from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx

# ── Configuration ─────────────────────────────────────────────────
CORE_URL = os.environ.get("AGENTMANAGER_CORE_URL", "http://127.0.0.1:3010")
API_KEY = os.environ.get("AGENTMANAGER_API_KEY", "")


def _headers() -> dict[str, str]:
    h: dict[str, str] = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


# ── API helpers (name-based, for CLI convenience) ─────────────────


async def _resolve_agent_id(name: str) -> str | None:
    async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
        resp = await c.get("/api/v1/agents")
        if resp.status_code != 200:
            return None
        agents = resp.json()
        for a in agents:
            if a.get("name") == name:
                return a["id"]
    return None


async def _list_agents() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
        resp = await c.get("/api/v1/agents")
        if resp.status_code != 200:
            return []
        return resp.json()


async def _chat_with_agent(agent_id: str, message: str) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
        resp = await c.post("/api/v1/chat", json={"agent_id": agent_id, "message": message})
        if resp.status_code != 200:
            return {"error": f"API error {resp.status_code}: {resp.text}"}
        return resp.json()


async def _assign_task(agent_id: str, goal: str) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
        resp = await c.post("/api/v1/tasks", json={"agent_id": agent_id, "goal": goal})
        if resp.status_code != 201:
            return {"error": f"API error {resp.status_code}: {resp.text}"}
        return resp.json()


# ── Command dispatcher ────────────────────────────────────────────


async def _handle_command(cmd: str, args: list[str]) -> str:
    match cmd:
        case "list":
            agents = await _list_agents()
            if not agents:
                return "No agents found."
            lines = ["Agents:"]
            for a in agents:
                status_icon = "●" if a.get("is_active") else "○"
                lines.append(
                    f"  {status_icon} {a['name']:20} {a.get('role', 'assistant'):12} "
                    f"{a.get('status', 'unknown'):8} {a.get('provider', '?')}/{a.get('model', '?')}"
                )
            return "\n".join(lines)

        case "chat":
            if len(args) < 2:
                return "Usage: /agent chat <name> <message>"
            agent_name = args[0]
            message = " ".join(args[1:])
            agent_id = await _resolve_agent_id(agent_name)
            if not agent_id:
                agents = await _list_agents()
                names = ", ".join(a["name"] for a in agents) if agents else "(none)"
                return f"Agent '{agent_name}' not found. Available: {names}"
            result = await _chat_with_agent(agent_id, message)
            if "error" in result:
                return f"Error: {result['error']}"
            return f"[{agent_name} via {result.get('used_model', '?')}]\n{result.get('response', '')}"

        case "task":
            if len(args) < 2:
                return "Usage: /agent task <name> <goal>"
            agent_name = args[0]
            goal = " ".join(args[1:])
            agent_id = await _resolve_agent_id(agent_name)
            if not agent_id:
                agents = await _list_agents()
                names = ", ".join(a["name"] for a in agents) if agents else "(none)"
                return f"Agent '{agent_name}' not found. Available: {names}"
            result = await _assign_task(agent_id, goal)
            if "error" in result:
                return f"Error: {result['error']}"
            tid = result.get("id", "?")[:8]
            return f"Task created for {agent_name}: [{tid}] {result.get('goal', '')} ({result.get('status', 'pending')})"

        case "status":
            try:
                async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
                    health = await c.get("/api/v1/health")
                    health_data = health.json() if health.status_code == 200 else {"version": "?", "status": "?"}
                agents = await _list_agents()
                active = sum(1 for a in agents if a.get("is_active"))
                return (
                    f" AgentManager Status\n"
                    f"  Core:     v{health_data.get('version', '?')} ({health_data.get('status', '?')})\n"
                    f"  Agents:   {len(agents)} total, {active} active\n"
                    f"  API:      {CORE_URL}"
                )
            except Exception as e:
                return f"Cannot connect to AgentManager Core at {CORE_URL}: {e}"

        case _:
            return (
                "Unknown /agent command. Available:\n"
                "  /agent list                     List all agents\n"
                "  /agent chat <name> <message>    Chat with an agent\n"
                "  /agent task <name> <goal>       Assign a task to an agent\n"
                "  /agent status                   Show connection status"
            )


# ── MCP over stdio mode ───────────────────────────────────────────


async def _handle_mcp_request(request: dict[str, Any]) -> dict[str, Any]:
    req_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agentmanager", "version": "0.1.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "agent_list",
                        "description": "List all agents registered in AgentManager",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "agent_chat",
                        "description": "Send a message to an agent by name",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Agent name"},
                                "message": {"type": "string", "description": "Message to send"},
                            },
                            "required": ["name", "message"],
                        },
                    },
                    {
                        "name": "agent_task",
                        "description": "Assign a task to an agent by name",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Agent name"},
                                "goal": {"type": "string", "description": "Task goal description"},
                            },
                            "required": ["name", "goal"],
                        },
                    },
                    {
                        "name": "agent_status",
                        "description": "Show AgentManager connection status",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        match tool_name:
            case "agent_list":
                agents = await _list_agents()
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(agents, indent=2, default=str)}]}}

            case "agent_chat":
                agent_name = arguments.get("name", "")
                message = arguments.get("message", "")
                if not agent_name or not message:
                    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing required arguments: name, message"}}
                agent_id = await _resolve_agent_id(agent_name)
                if not agent_id:
                    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": f"Agent '{agent_name}' not found"}}
                result = await _chat_with_agent(agent_id, message)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}}

            case "agent_task":
                agent_name = arguments.get("name", "")
                goal = arguments.get("goal", "")
                if not agent_name or not goal:
                    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing required arguments: name, goal"}}
                agent_id = await _resolve_agent_id(agent_name)
                if not agent_id:
                    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": f"Agent '{agent_name}' not found"}}
                result = await _assign_task(agent_id, goal)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}}

            case "agent_status":
                try:
                    async with httpx.AsyncClient(base_url=CORE_URL, headers=_headers()) as c:
                        health = await c.get("/api/v1/health")
                        health_data = health.json() if health.status_code == 200 else {}
                    agents = await _list_agents()
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({
                                        "core_url": CORE_URL,
                                        "version": health_data.get("version"),
                                        "status": health_data.get("status"),
                                        "agent_count": len(agents),
                                    }, indent=2),
                                }
                            ]
                        },
                    }
                except Exception as e:
                    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

            case _:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}

    if method == "notifications/initialized":
        return None

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


# ── Entry points ──────────────────────────────────────────────────


async def mcp_stdio_loop() -> None:
    """Run as MCP-over-stdio server (used by Codex CLI via mcpServers config)."""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = await _handle_mcp_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Invalid JSON: {e}\n")
            sys.stderr.flush()


async def cli_mode() -> None:
    """Run as a single-shot CLI command handler."""
    if len(sys.argv) < 3:
        print("Usage: python -m src.cli.codex_handler <command> [args...]")
        print("Commands: list, chat <name> <message>, task <name> <goal>, status")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]
    result = await _handle_command(cmd, args)
    print(result)


def main() -> None:
    """Detect mode and run accordingly."""
    mode = os.environ.get("AGENTMANAGER_MCP_MODE", "cli")

    if mode == "stdio":
        import asyncio
        asyncio.run(mcp_stdio_loop())
    else:
        import asyncio
        asyncio.run(cli_mode())


if __name__ == "__main__":
    main()
