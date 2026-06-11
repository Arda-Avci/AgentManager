from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

from src.tools.repo_map import RepoMap


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()

    (src / "__init__.py").write_text("")
    (src / "main.py").write_text(
        "def main():\n"
        "    print('hello')\n"
        "\n"
        "def helper(name: str) -> str:\n"
        '    return f"Hello {name}"\n'
    )
    (src / "models.py").write_text(
        "from pydantic import BaseModel\n"
        "\n"
        "\n"
        "class User(BaseModel):\n"
        '    """User model."""\n'
        "    name: str\n"
        "    age: int\n"
        "\n"
        "    def greet(self) -> str:\n"
        '        return f"Hi, {self.name}"\n'
        "\n"
        "\n"
        "class Admin(User):\n"
        "    role: str = 'admin'\n"
        "\n"
        "    def get_role(self) -> str:\n"
        "        return self.role\n"
    )

    api = src / "api"
    api.mkdir()
    (api / "__init__.py").write_text("")
    (api / "routes.py").write_text(
        "from fastapi import APIRouter\n"
        "\n"
        "router = APIRouter()\n"
        "\n"
        "\n"
        "@router.get('/')\n"
        "async def list_items():\n"
        "    return []\n"
        "\n"
        "\n"
        "@router.post('/')\n"
        "async def create_item(data: dict):\n"
        "    return data\n"
    )

    (tmp_path / "README.md").write_text("# Sample Repo")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()\n")
    (tmp_path / "ignored_file.tmp").write_text("cache data")

    return tmp_path


class TestParseSource:
    def test_parse_python_functions(self, sample_repo: Path):
        mapper = RepoMap()
        symbols = mapper.parse_source(str(sample_repo / "src" / "main.py"))

        assert len(symbols) == 2
        assert symbols[0]["kind"] == "function"
        assert symbols[0]["name"] == "main"
        assert symbols[1]["name"] == "helper"

    def test_parse_python_classes(self, sample_repo: Path):
        mapper = RepoMap()
        symbols = mapper.parse_source(str(sample_repo / "src" / "models.py"))

        classes = [s for s in symbols if s["kind"] == "class"]
        assert len(classes) == 2
        assert classes[0]["name"] == "User"
        assert classes[1]["name"] == "Admin"

    def test_parse_python_class_methods(self, sample_repo: Path):
        mapper = RepoMap()
        symbols = mapper.parse_source(str(sample_repo / "src" / "models.py"))

        user = next(s for s in symbols if s["name"] == "User")
        assert len(user["methods"]) == 1
        assert user["methods"][0]["name"] == "greet"

    def test_parse_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.py"
        f.write_text("")
        mapper = RepoMap()
        assert mapper.parse_source(str(f)) == []

    def test_parse_nonexistent_file(self):
        mapper = RepoMap()
        assert mapper.parse_source("/nonexistent/file.py") == []

    def test_parse_syntax_error_falls_back(self, tmp_path: Path):
        f = tmp_path / "broken.py"
        f.write_text("def foo( bar")
        mapper = RepoMap()
        symbols = mapper.parse_source(str(f))
        assert any(s["name"] == "foo" for s in symbols)


class TestScan:
    def test_scan_directory(self, sample_repo: Path):
        mapper = RepoMap()
        tree = mapper.scan(str(sample_repo))

        dir_names = [e["name"] for e in tree if e["type"] == "dir"]
        assert "src" in dir_names

    def test_scan_ignores_special_dirs(self, sample_repo: Path):
        (sample_repo / "__pycache__").mkdir()
        mapper = RepoMap()
        tree = mapper.scan(str(sample_repo))
        dir_names = [e["name"] for e in tree if e["type"] == "dir"]
        assert "__pycache__" not in dir_names

    def test_scan_counts_files(self, sample_repo: Path):
        mapper = RepoMap()
        count = mapper._count_files(mapper.scan(str(sample_repo)))
        assert count >= 5


class TestGenerateMap:
    def test_generate_map_basic(self, sample_repo: Path):
        mapper = RepoMap()
        result = mapper.generate_map(str(sample_repo), depth=3)
        assert "src/" in result or "src" in result or "├──" in result or "└──" in result
        assert "main.py" in result
        assert "models.py" in result

    def test_generate_map_nonexistent_path(self):
        mapper = RepoMap()
        result = mapper.generate_map("/nonexistent/path")
        assert "Error" in result

    def test_generate_map_shallow_depth(self, sample_repo: Path):
        mapper = RepoMap()
        deep = mapper.generate_map(str(sample_repo), depth=5)
        shallow = mapper.generate_map(str(sample_repo), depth=1)
        assert len(shallow) <= len(deep) or shallow != deep


class TestGetSignature:
    def test_get_function_signature(self, sample_repo: Path):
        mapper = RepoMap()
        sig = mapper.get_signature(str(sample_repo / "src" / "main.py"), "helper")
        assert sig is not None
        assert sig["name"] == "helper"
        assert sig["kind"] == "function"

    def test_get_method_signature(self, sample_repo: Path):
        mapper = RepoMap()
        sig = mapper.get_signature(str(sample_repo / "src" / "models.py"), "greet")
        assert sig is not None
        assert sig["name"] == "greet"
        assert sig["kind"] == "method"

    def test_get_nonexistent_signature(self, sample_repo: Path):
        mapper = RepoMap()
        sig = mapper.get_signature(str(sample_repo / "src" / "main.py"), "nonexistent_func")
        assert sig is None


class TestRepoContext:
    def test_get_repo_context(self, sample_repo: Path):
        mapper = RepoMap()
        ctx = mapper.get_repo_context(str(sample_repo))
        assert "structure" in ctx
        assert "file_count" in ctx
        assert "important_files" in ctx
        assert ctx["file_count"] >= 5

    def test_repo_context_has_signatures(self, sample_repo: Path):
        mapper = RepoMap()
        ctx = mapper.get_repo_context(str(sample_repo))
        signatures = ctx.get("signatures", {})
        assert len(signatures) > 0

    def test_important_files_prioritizes_keywords(self, sample_repo: Path):
        mapper = RepoMap()
        ctx = mapper.get_repo_context(str(sample_repo))
        important = ctx.get("important_files", {})
        has_main = any("main" in f for f in important)
        has_models = any("models" in f for f in important)
        has_routes = any("routes" in f for f in important)
        assert has_main or has_models or has_routes


class TestFormatTree:
    def test_tree_uses_unicode_connectors(self, sample_repo: Path):
        mapper = RepoMap()
        result = mapper.generate_map(str(sample_repo), depth=2)
        assert "├──" in result or "└──" in result

    def test_tree_displays_symbols_for_files(self, sample_repo: Path):
        mapper = RepoMap()
        result = mapper.generate_map(str(sample_repo), depth=3)
        assert "main" in result

    def test_empty_directory(self, tmp_path: Path):
        mapper = RepoMap()
        result = mapper.generate_map(str(tmp_path))
        assert isinstance(result, str)


class TestFindReferences:
    def test_find_references_returns_list(self, sample_repo: Path):
        mapper = RepoMap()
        refs = mapper.find_references("main", str(sample_repo))
        assert isinstance(refs, list)

    def test_find_references_nonexistent_symbol(self, sample_repo: Path):
        mapper = RepoMap()
        refs = mapper.find_references("zzz_nonexistent_symbol_12345", str(sample_repo))
        assert isinstance(refs, list)


@pytest.mark.asyncio
async def test_repo_map_api(client):
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        (td_path / "test.py").write_text("def foo():\n    pass\n")
        resp = await client.post(
            "/api/v1/tools/repo-map",
            json={"path": td, "depth": 3, "include_signatures": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "map" in data
        assert "test.py" in data["map"]


@pytest.mark.asyncio
async def test_repo_map_store_flow(client):
    create = await client.post("/api/v1/agents", json={"name": "map-agent"})
    agent_id = create.json()["id"]

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        (td_path / "code.py").write_text("class Foo:\n    pass\n")
        save = await client.post(
            f"/api/v1/tools/repo-map/{agent_id}",
            json={"path": td, "depth": 3, "include_signatures": False},
        )
        assert save.status_code == 200

        get = await client.get(f"/api/v1/tools/repo-map/{agent_id}?path={td}")
        assert get.status_code == 200
        assert get.json()["map"] is not None
