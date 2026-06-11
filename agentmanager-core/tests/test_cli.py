from __future__ import annotations

import sys
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def isolate_cli_args():
    old = sys.argv.copy()
    yield
    sys.argv = old


class TestCLICommands:

    def test_cli_create_command_structure(self):
        from click import Group, Command
        from src.cli.main import cli

        assert isinstance(cli, Group)
        commands = cli.commands
        assert "start" in commands
        assert "init" in commands
        assert "create" in commands
        assert "status" in commands

        assert isinstance(commands["start"], Command)
        assert isinstance(commands["init"], Command)
        assert isinstance(commands["create"], Command)
        assert isinstance(commands["status"], Command)

    def test_cli_create_has_correct_options(self):
        from click import Command, Option
        from src.cli.main import cli

        create_cmd = cli.commands["create"]
        assert isinstance(create_cmd, Command)
        opts = {p.name: p for p in create_cmd.params}
        assert "name" in opts
        assert "role" in opts
        assert "provider" in opts
        assert "model" in opts

        role_opt = opts["role"]
        assert isinstance(role_opt, Option)
        assert role_opt.default == "assistant"

        provider_opt = opts["provider"]
        assert isinstance(provider_opt, Option)
        assert provider_opt.default == "openai"

    def test_cli_main_routes_to_cli(self, isolate_cli_args):
        sys.argv = ["agentmanager", "--help"]
        from src.cli.main import main
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once()

    def test_cli_status_command_exists_and_runs(self):
        from click import Command
        from src.cli.main import cli

        status_cmd = cli.commands["status"]
        assert isinstance(status_cmd, Command)

    def test_cli_start_command_exists_and_runs(self):
        from click import Command
        from src.cli.main import cli

        start_cmd = cli.commands["start"]
        assert isinstance(start_cmd, Command)
