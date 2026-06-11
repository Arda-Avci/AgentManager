from __future__ import annotations

import subprocess
from pathlib import Path

from src.session import SessionManager


_ALLOWLIST = {
    "python", "python3", "pip", "npm", "npx", "node",
    "git", "ls", "cat", "pwd", "echo", "dir", "type",
    "black", "ruff", "pytest", "vitest", "npx vitest",
}


class CommandResult:
    def __init__(self, response: str, used_model: str = "commands"):
        self.response = response
        self.used_model = used_model


class CommandHandler:
    def __init__(self, session_manager: SessionManager, chat_id: str):
        self._sm = session_manager
        self._chat_id = chat_id

    async def handle(self, cmd: dict) -> CommandResult:
        name = cmd["name"]
        args = cmd["args"]

        handlers = {
            "add": self._add,
            "drop": self._drop,
            "undo": self._undo,
            "diff": self._diff,
            "run": self._run,
            "help": self._help,
        }

        handler = handlers.get(name)
        if not handler:
            return CommandResult(f"Bilinmeyen komut: /{name}")

        return await handler(args)

    async def _add(self, args: str) -> CommandResult:
        if not args:
            return CommandResult("Kullanim: /add <dosya_yolu>")
        path = Path(args)
        if not path.exists():
            return CommandResult(f"Dosya bulunamadi: {args}")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return CommandResult(f"Dosya okunamadi: {e}")

        session = await self._sm.get_or_create(self._chat_id)
        ctx = dict(session.context or {})
        files = list(ctx.get("context_files", []))
        files.append({"path": str(path), "content": content})
        ctx["context_files"] = files
        await self._sm.update_context(self._chat_id, ctx)

        return CommandResult(f"Dosya eklendi: `{path}` ({len(content)} karakter)")

    async def _drop(self, args: str) -> CommandResult:
        if not args:
            return CommandResult("Kullanim: /drop <dosya_yolu>")
        target = Path(args)

        session = await self._sm.get_or_create(self._chat_id)
        ctx = dict(session.context or {})
        files = list(ctx.get("context_files", []))
        before = len(files)
        files = [f for f in files if Path(f["path"]) != target]
        removed = before - len(files)

        if not removed:
            return CommandResult(f"Dosya context'te bulunamadi: `{args}`")

        ctx["context_files"] = files
        await self._sm.update_context(self._chat_id, ctx)
        return CommandResult(f"Dosya context'ten cikarildi: `{args}`")

    async def _undo(self, args: str) -> CommandResult:
        session = await self._sm.get_or_create(self._chat_id)
        ctx = dict(session.context or {})
        files = list(ctx.get("context_files", []))
        if not files:
            return CommandResult("Geri alinacak islem yok.")

        removed = files.pop()
        ctx["context_files"] = files
        await self._sm.update_context(self._chat_id, ctx)
        return CommandResult(f"Son islem geri alindi: `{removed['path']}`")

    async def _diff(self, args: str) -> CommandResult:
        try:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True, text=True, timeout=30,
            )
            output = result.stdout or result.stderr or "(bos)"
            if not result.stdout and result.returncode != 0:
                output = f"Git hatasi: {result.stderr}"
            return CommandResult(output[:2000])
        except FileNotFoundError:
            return CommandResult("Git bulunamadi. PATH'te oldugundan emin olun.")
        except subprocess.TimeoutExpired:
            return CommandResult("Git diff zamani asti.")
        except Exception as e:
            return CommandResult(f"Diff alinamadi: {e}")

    async def _run(self, args: str) -> CommandResult:
        if not args:
            return CommandResult("Kullanim: /run <komut>")
        parts = args.split()
        cmd_name = parts[0].lower()
        if cmd_name not in _ALLOWLIST:
            return CommandResult(
                f"Komut allowlist'te degil: `{cmd_name}`\n"
                f"Izin verilenler: {', '.join(sorted(_ALLOWLIST))}"
            )
        try:
            result = subprocess.run(
                args, shell=True, capture_output=True, text=True, timeout=60,
            )
            output = result.stdout or result.stderr or "(bos cikti)"
            if result.returncode != 0:
                output = f"Kod: {result.returncode}\n{result.stderr[:1000]}"
            return CommandResult(output[:2000])
        except subprocess.TimeoutExpired:
            return CommandResult("Komut zamani asti (60s).")
        except Exception as e:
            return CommandResult(f"Komut calistirilamadi: {e}")

    async def _help(self, args: str) -> CommandResult:
        from src.commands.parser import get_help_text

        return CommandResult(get_help_text())
