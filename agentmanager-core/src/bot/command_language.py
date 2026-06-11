from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedCommand:
    action: str = ""
    name: str = ""
    provider: str = ""
    model: str = ""
    agent: str = ""
    task: str = ""
    schedule: str = ""
    time: str = ""
    target: str = ""
    remaining: str = ""
    raw: str = ""
    error: str = ""
    params: dict[str, Any] = field(default_factory=dict)


_PATTERNS: list[tuple[str, str, list[str], dict[str, int]]] = [
    (
        "create_agent",
        r"create\s+(?:agent\s+)?(\S+)(?:\s+using\s+(\S+))?(?:\s+with\s+(\S+))?",
        ["name", "provider", "model"],
        {},
    ),
    (
        "ask_agent",
        r"(?:ask|tell|chat\s+with)\s+(\S+)\s+(?:to\s+|about\s+|:\s*)?(.+)",
        ["agent", "task"],
        {},
    ),
    (
        "schedule_task",
        r"schedule\s+(.+?)\s+(?:at|every)\s+(\S+)",
        ["task", "time"],
        {},
    ),
    (
        "list_agents",
        r"(?:list|show)\s+(?:all\s+)?(?:agents?|bots?)",
        [],
        {"action": "list_agents"},
    ),
    (
        "pause_agent",
        r"pause\s+(?:agent\s+)?(\S+)",
        ["name"],
        {"action": "pause_agent"},
    ),
    (
        "resume_agent",
        r"resume\s+(?:agent\s+)?(\S+)",
        ["name"],
        {"action": "resume_agent"},
    ),
    (
        "delete_agent",
        r"(?:delete|remove)\s+(?:agent\s+)?(\S+)",
        ["name"],
        {"action": "delete_agent"},
    ),
    (
        "agent_status",
        r"(?:status|health)\s+(?:of\s+)?(?:agent\s+)?(\S+)",
        ["name"],
        {"action": "agent_status"},
    ),
    (
        "list_tasks",
        r"(?:list|show)\s+(?:all\s+)?tasks?(?:\s+(?:for|of)\s+(\S+))?",
        ["target"],
        {"action": "list_tasks"},
    ),
    (
        "assign_task",
        r"assign\s+(\S+)\s+(?:to\s+|on\s+)?(.+)",
        ["agent", "task"],
        {"action": "assign_task"},
    ),
    (
        "delegate_task",
        r"delegate\s+(.+?)\s+(?:from\s+)?(\S+)\s+(?:to\s+)(\S+)",
        ["task", "target", "agent"],
        {"action": "delegate_task"},
    ),
    (
        "help",
        r"(?:help|commands?|yardım)",
        [],
        {"action": "help"},
    ),
]


class CommandLanguage:

    def parse(self, text: str) -> ParsedCommand:
        cmd = ParsedCommand(raw=text)
        text_clean = text.strip()

        for action_name, pattern, param_names, extra in _PATTERNS:
            m = re.match(pattern, text_clean, re.IGNORECASE)
            if m:
                cmd.action = extra.get("action", action_name)
                for i, pname in enumerate(param_names):
                    val = m.group(i + 1)
                    if val:
                        lower_val = val.lower()
                        setattr(cmd, pname, val if pname in ("task", "remaining") else lower_val)
                cmd.params = extra
                return cmd

        cmd.error = "unrecognized"
        return cmd

    def format(self, cmd: ParsedCommand) -> str:
        if cmd.error:
            return (
                f"Komut anlaşılamadı: '{cmd.raw}'. "
                "Yardım için 'help' yazın.\n"
                "Örnekler:\n"
                "  • create agent code-agent using claude\n"
                "  • ask code-agent to review PR #42\n"
                "  • schedule daily standup at 9am\n"
                "  • list agents\n"
                "  • pause code-agent\n"
                "  • resume code-agent\n"
                "  • list tasks\n"
                "  • delegate code-review from agent-a to agent-b"
            )

        parts = [f"✅ **{cmd.action}**"]
        if cmd.name:
            parts.append(f"  Ajan: `{cmd.name}`")
        if cmd.agent:
            parts.append(f"  Ajan: `{cmd.agent}`")
        if cmd.provider:
            parts.append(f"  Provider: `{cmd.provider}`")
        if cmd.model:
            parts.append(f"  Model: `{cmd.model}`")
        if cmd.task:
            parts.append(f"  Görev: {cmd.task}")
        if cmd.time:
            parts.append(f"  Zaman: `{cmd.time}`")
        if cmd.target:
            parts.append(f"  Hedef: `{cmd.target}`")
        if cmd.remaining:
            parts.append(f"  İçerik: {cmd.remaining}")
        return "\n".join(parts)
