from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.commands.handler import CommandHandler, CommandResult
from src.commands.parser import get_help_text, parse_command


class TestParser:
    def test_parse_add(self):
        cmd = parse_command("/add foo.py")
        assert cmd == {"name": "add", "args": "foo.py"}

    def test_parse_drop(self):
        cmd = parse_command("/drop bar.py")
        assert cmd == {"name": "drop", "args": "bar.py"}

    def test_parse_undo(self):
        cmd = parse_command("/undo")
        assert cmd == {"name": "undo", "args": ""}

    def test_parse_diff(self):
        cmd = parse_command("/diff")
        assert cmd == {"name": "diff", "args": ""}

    def test_parse_run(self):
        cmd = parse_command("/run pytest")
        assert cmd == {"name": "run", "args": "pytest"}

    def test_parse_help(self):
        cmd = parse_command("/help")
        assert cmd == {"name": "help", "args": ""}

    def test_parse_plain_text_ignored(self):
        assert parse_command("merhaba nasilsin") is None

    def test_parse_unknown_command(self):
        assert parse_command("/xyz") is None

    def test_parse_slash_only(self):
        assert parse_command("/") is None

    def test_parse_case_insensitive(self):
        cmd = parse_command("/ADD file.txt")
        assert cmd is not None
        assert cmd["name"] == "add"

    def test_get_help_text(self):
        text = get_help_text()
        assert "/add" in text
        assert "/drop" in text
        assert "/undo" in text
        assert "/diff" in text
        assert "/run" in text
        assert "/help" in text


class TestHandler:
    @pytest.mark.asyncio
    async def test_handle_help(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "help", "args": ""})
        assert "/add" in result.response

    @pytest.mark.asyncio
    async def test_handle_unknown(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "unknown", "args": ""})
        assert "Bilinmeyen" in result.response

    @pytest.mark.asyncio
    async def test_handle_add_no_args(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "add", "args": ""})
        assert "Kullanim" in result.response

    @pytest.mark.asyncio
    async def test_handle_add_file_not_found(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "add", "args": "nonexistent_file_xyz.txt"})
        assert "bulunamadi" in result.response

    @pytest.mark.asyncio
    async def test_handle_add_success(self, tmp_path: Path):
        test_file = tmp_path / "test_add.txt"
        test_file.write_text("hello world", encoding="utf-8")

        mock_session = AsyncMock()
        mock_session.context = {}

        sm = AsyncMock()
        sm.get_or_create = AsyncMock(return_value=mock_session)

        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "add", "args": str(test_file)})
        assert "eklendi" in result.response

    @pytest.mark.asyncio
    async def test_handle_undo_empty(self):
        sm = AsyncMock()
        mock_session = AsyncMock()
        mock_session.context = {}
        sm.get_or_create = AsyncMock(return_value=mock_session)

        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "undo", "args": ""})
        assert "islem yok" in result.response

    @pytest.mark.asyncio
    async def test_handle_run_not_allowed(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")
        result = await handler.handle({"name": "run", "args": "rm -rf /"})
        assert "allowlist" in result.response

    @pytest.mark.asyncio
    async def test_handle_run_allowed(self):
        sm = AsyncMock()
        handler = CommandHandler(sm, "test-chat")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "hello from echo"
            mock_run.return_value.returncode = 0
            result = await handler.handle({"name": "run", "args": "echo test"})
            assert "hello" in result.response or "bos" in result.response
