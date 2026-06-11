from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.tools.base import BaseTool


IGNORED_DIRS = {
    "__pycache__", ".git", ".svn", ".hg", "node_modules",
    "venv", ".venv", ".env", "dist", "build", ".egg-info",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".opencode", ".claude", "__pycache__",
}

SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt"}


class RepoMapParams(BaseModel):
    path: str = Field(".", description="Repo path to scan")
    depth: int = Field(3, ge=1, le=10, description="Tree depth")
    include_signatures: bool = Field(False, description="Include function signatures")


class RepoMapTool(BaseTool):
    name = "repo_map"
    description = "Generate a repository map with file structure and code signatures"
    parameters = RepoMapParams

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    async def execute(self, params: BaseModel) -> Any:
        p = params if isinstance(params, RepoMapParams) else RepoMapParams(**params.model_dump())
        mapper = RepoMap()
        return {
            "map": mapper.generate_map(p.path, p.depth),
            "context": mapper.get_repo_context(p.path),
        }


class RepoMap:
    def scan(self, path: str) -> list[dict]:
        root = Path(path).resolve()
        if not root.is_dir():
            return []
        return self._scan_dir(root, root)

    def _scan_dir(self, dir_path: Path, root: Path) -> list[dict]:
        entries: list[dict] = []
        try:
            items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return entries

        for item in items:
            if item.name.startswith(".") or item.name in IGNORED_DIRS:
                continue
            if item.is_dir():
                children = self._scan_dir(item, root)
                if children or not item.name.startswith("_"):
                    entries.append({
                        "name": item.name,
                        "type": "dir",
                        "path": str(item.relative_to(root)),
                        "children": children,
                    })
            elif item.suffix in SOURCE_EXTENSIONS:
                sigs = self.parse_source(str(item))
                entries.append({
                    "name": item.name,
                    "type": "file",
                    "path": str(item.relative_to(root)),
                    "symbols": self._summarize_symbols(sigs),
                })
        return entries

    def _summarize_symbols(self, symbols: list[dict]) -> list[str]:
        return [
            f"{s['kind']} {s['name']}{'(' + ', '.join(s['params']) + ')' if s['kind'] == 'function' else ''}"
            for s in symbols
        ]

    def generate_map(self, path: str, depth: int = 3) -> str:
        root = Path(path).resolve()
        if not root.is_dir():
            return f"Error: '{path}' is not a directory"

        tree = self.scan(path)
        return self._format_tree(tree, depth=depth)

    def _format_tree(self, entries: list[dict], depth: int, prefix: str = "") -> str:
        if depth <= 0 or not entries:
            return ""

        lines: list[str] = []
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            extension = "" if entry["type"] == "dir" else ""

            label = entry["name"]

            if entry["type"] == "file" and entry.get("symbols"):
                sigs = "; ".join(entry["symbols"][:5])
                if len(entry["symbols"]) > 5:
                    sigs += f" ... (+{len(entry['symbols']) - 5})"
                label += f"  ({sigs})"
            elif entry["type"] == "file" and entry["name"].endswith(".py"):
                label += "  (module)"

            lines.append(f"{prefix}{connector}{label}")

            if entry["type"] == "dir" and entry.get("children"):
                sub_prefix = prefix + ("    " if is_last else "│   ")
                sub = self._format_tree(entry["children"], depth - 1, sub_prefix)
                if sub:
                    lines.append(sub)

        return "\n".join(lines)

    def parse_source(self, file_path: str) -> list[dict]:
        path = Path(file_path)
        if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
            return []

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []

        if path.suffix == ".py":
            return self._parse_python(source)
        return self._parse_generic(source)

    def _parse_python(self, source: str) -> list[dict]:
        symbols: list[dict] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return self._parse_generic(source)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in ast.iter_child_nodes(node):
                    if isinstance(item, ast.FunctionDef):
                        params = [arg.arg for arg in item.args.args if arg.arg != "self"]
                        methods.append({
                            "kind": "method",
                            "name": item.name,
                            "params": params,
                            "lineno": item.lineno,
                        })
                symbols.append({
                    "kind": "class",
                    "name": node.name,
                    "params": [],
                    "lineno": node.lineno,
                    "methods": methods,
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = [arg.arg for arg in node.args.args]
                symbols.append({
                    "kind": "function",
                    "name": node.name,
                    "params": params,
                    "lineno": node.lineno,
                })
        return symbols

    def _parse_generic(self, source: str) -> list[dict]:
        symbols: list[dict] = []
        patterns = [
            (r"(?:class|interface|trait|struct)\s+(\w+)", "class"),
            (r"(?:def|fn|function|func|async\s+def)\s+(\w+)\s*\(", "function"),
        ]
        for pattern, kind in patterns:
            for m in re.finditer(pattern, source, re.MULTILINE):
                symbols.append({
                    "kind": kind,
                    "name": m.group(1),
                    "params": [],
                    "lineno": source[:m.start()].count("\n") + 1,
                })
        return symbols

    def get_signature(self, file_path: str, function_name: str) -> dict | None:
        symbols = self.parse_source(file_path)
        for sym in symbols:
            if sym["name"] == function_name:
                return sym
            if sym["kind"] == "class" and sym.get("methods"):
                for m in sym["methods"]:
                    if m["name"] == function_name:
                        return m
        return None

    def find_references(self, symbol: str, path: str | None = None) -> list[dict]:
        import subprocess

        search_path = path or "."
        try:
            result = subprocess.run(
                ["rg", "--no-heading", "--line-number", symbol, search_path],
                capture_output=True,
                text=True,
                timeout=15,
            )
            refs: list[dict] = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":", 2)
                if len(parts) >= 2:
                    refs.append({
                        "file": parts[0],
                        "line": int(parts[1]),
                        "content": parts[2] if len(parts) > 2 else "",
                    })
            return refs
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def get_repo_context(self, path: str) -> dict:
        tree = self.scan(path)
        important_files = self._find_important_files(tree, path)
        signatures: dict[str, list[dict]] = {}
        for fp in important_files:
            sigs = self.parse_source(fp)
            if sigs:
                signatures[fp] = sigs
        return {
            "structure": self.generate_map(path, depth=2),
            "file_count": self._count_files(tree),
            "important_files": {fp: [s["name"] for s in sigs] for fp, sigs in signatures.items()},
            "signatures": signatures,
        }

    def _find_important_files(self, entries: list[dict], base_path: str, max_files: int = 15) -> list[str]:
        files: list[str] = []
        priority_keywords = ["main", "app", "index", "routes", "models", "schemas", "config", "settings", "base", "registry", "manager", "service"]

        def walk(entries: list[dict], current: str):
            for e in entries:
                full = str(Path(current) / e["name"]) if current else e["path"]
                if e["type"] == "file":
                    score = 0
                    for kw in priority_keywords:
                        if kw in e["name"].lower():
                            score += 1
                    if e.get("symbols"):
                        score += min(len(e["symbols"]), 3)
                    files.append((full, score))
                elif e["type"] == "dir" and e.get("children"):
                    walk(e["children"], full)

        walk(entries, "")
        files.sort(key=lambda x: -x[1])
        return [f[0] for f in files[:max_files]]

    def _count_files(self, entries: list[dict]) -> int:
        count = 0
        for e in entries:
            if e["type"] == "file":
                count += 1
            elif e["type"] == "dir" and e.get("children"):
                count += self._count_files(e["children"])
        return count
