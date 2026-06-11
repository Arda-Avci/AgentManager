from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.tools.base import BaseTool


class GitDiffParams(BaseModel):
    target: str = Field("HEAD", description="Git ref to diff against")


class GitCommitParams(BaseModel):
    message: str = Field(..., min_length=1, description="Commit message")
    paths: list[str] = Field(default_factory=list, description="Files to stage")


class GitUndoParams(BaseModel):
    soft: bool = Field(True, description="Soft reset (keep changes)")


class GitStatusParams(BaseModel):
    pass


class GitLogParams(BaseModel):
    max_count: int = Field(10, ge=1, le=100, description="Number of commits")


class GitTool(BaseTool):
    name = "git"
    description = "Run git operations: diff, commit, undo, status, log"

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.repo_path = Path(self.config.get("repo_path", "."))

    async def execute(self, params: BaseModel) -> Any:
        action = self.config.get("action", "status")
        if isinstance(params, GitDiffParams):
            return self._diff(params)
        elif isinstance(params, GitCommitParams):
            return self._commit(params)
        elif isinstance(params, GitUndoParams):
            return self._undo(params)
        elif isinstance(params, GitStatusParams):
            return self._status()
        elif isinstance(params, GitLogParams):
            return self._log(params)
        raise ValueError(f"Unknown params type: {type(params).__name__}")

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
        return result.stdout

    def _diff(self, params: GitDiffParams) -> str:
        return self._run("diff", params.target)

    def _commit(self, params: GitCommitParams) -> str:
        if params.paths:
            self._run("add", *params.paths)
        else:
            self._run("add", "-A")
        return self._run("commit", "-m", params.message)

    def _undo(self, params: GitUndoParams) -> str:
        if params.soft:
            return self._run("reset", "--soft", "HEAD~1")
        return self._run("reset", "--hard", "HEAD~1")

    def _status(self) -> str:
        return self._run("status")

    def _log(self, params: GitLogParams) -> str:
        return self._run("log", f"--max-count={params.max_count}", "--oneline")
