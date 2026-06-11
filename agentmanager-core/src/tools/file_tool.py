from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.tools.base import BaseTool


class FileReadParams(BaseModel):
    path: str = Field(..., min_length=1, description="File path to read")
    encoding: str = Field("utf-8", description="File encoding")


class FileWriteParams(BaseModel):
    path: str = Field(..., min_length=1, description="File path to write")
    content: str = Field(..., description="Content to write")
    encoding: str = Field("utf-8", description="File encoding")


class FileDeleteParams(BaseModel):
    path: str = Field(..., min_length=1, description="File path to delete")


class FileListParams(BaseModel):
    path: str = Field(".", description="Directory to list")
    pattern: str = Field("*", description="Glob pattern")


class FileTool(BaseTool):
    name = "file"
    description = "Read, write, delete, and list files on the filesystem"

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.base_path = Path(self.config.get("base_path", "."))

    async def execute(self, params: BaseModel) -> Any:
        if isinstance(params, FileReadParams):
            return self._read(params)
        elif isinstance(params, FileWriteParams):
            return self._write(params)
        elif isinstance(params, FileDeleteParams):
            return self._delete(params)
        elif isinstance(params, FileListParams):
            return self._list(params)
        raise ValueError(f"Unknown params type: {type(params).__name__}")

    def _resolve(self, path: str) -> Path:
        p = self.base_path / path
        return p.resolve()

    def _read(self, params: FileReadParams) -> str:
        p = self._resolve(params.path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        return p.read_text(encoding=params.encoding)

    def _write(self, params: FileWriteParams) -> dict:
        p = self._resolve(params.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(params.content, encoding=params.encoding)
        return {"path": str(p), "size": len(params.content)}

    def _delete(self, params: FileDeleteParams) -> dict:
        p = self._resolve(params.path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        p.unlink()
        return {"path": str(p), "deleted": True}

    def _list(self, params: FileListParams) -> list[dict]:
        p = self._resolve(params.path)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {p}")
        entries = []
        for child in p.glob(params.pattern):
            entries.append({"name": child.name, "is_dir": child.is_dir(), "path": str(child)})
        return sorted(entries, key=lambda x: (not x["is_dir"], x["name"]))
