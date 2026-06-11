from __future__ import annotations

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.engine import Base, get_session
from src.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_session():
        yield db_session

    app.dependency_overrides[get_session] = _get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mcp_client_connect_no_server():
    from src.mcp_client.client import MCPClient

    client = MCPClient()
    with pytest.raises(ValueError, match="server_url is required"):
        await client.connect()


@pytest.mark.asyncio
async def test_mcp_client_call_without_connect():
    from src.mcp_client.client import MCPClient

    client = MCPClient("http://localhost:9999")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.list_tools()


@pytest.mark.asyncio
async def test_register_local_tool():
    from src.mcp_client.registry import MCPToolRegistry
    from src.tools.web_search import WebSearchTool

    registry = MCPToolRegistry(None)
    tool = WebSearchTool()
    registry.register_local(tool)

    assert registry.get_local("web_search") is tool
    assert len(registry.list_local()) == 1


@pytest.mark.asyncio
async def test_tool_persist_and_retrieve(db_session: AsyncSession):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(db_session)
    tool = await registry.create_tool(
        name="test-tool",
        description="A test tool",
        tool_type="builtin",
    )
    assert tool.name == "test-tool"
    assert tool.is_active is True

    fetched = await registry.get_by_name("test-tool")
    assert fetched is not None
    assert fetched.id == tool.id

    tools = await registry.list_active()
    assert len(tools) >= 1


@pytest.mark.asyncio
async def test_tool_deactivate(db_session: AsyncSession):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(db_session)
    tool = await registry.create_tool(
        name="deactivate-me",
        tool_type="builtin",
    )

    ok = await registry.deactivate(tool.id)
    assert ok is True

    fetched = await registry.get_by_id(tool.id)
    assert fetched.is_active is False


@pytest.mark.asyncio
async def test_tool_delete(db_session: AsyncSession):
    from src.mcp_client.registry import MCPToolRegistry

    registry = MCPToolRegistry(db_session)
    tool = await registry.create_tool(
        name="delete-me",
        tool_type="builtin",
    )

    ok = await registry.delete(tool.id)
    assert ok is True

    fetched = await registry.get_by_id(tool.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_create_tool_via_api(client: AsyncClient):
    resp = await client.post(
        "/api/v1/tools",
        json={"name": "api-tool", "description": "Created via API", "tool_type": "builtin"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "api-tool"
    assert data["is_active"] is True
    assert data["tool_type"] == "builtin"


@pytest.mark.asyncio
async def test_create_duplicate_tool(client: AsyncClient):
    await client.post(
        "/api/v1/tools",
        json={"name": "dup-tool", "tool_type": "builtin"},
    )
    resp = await client.post(
        "/api/v1/tools",
        json={"name": "dup-tool", "tool_type": "builtin"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_tools_via_api(client: AsyncClient):
    await client.post("/api/v1/tools", json={"name": "list-test-1", "tool_type": "builtin"})
    await client.post("/api/v1/tools", json={"name": "list-test-2", "tool_type": "builtin"})

    resp = await client.get("/api/v1/tools")
    assert resp.status_code == 200
    data = resp.json()
    names = [t["name"] for t in data]
    assert "list-test-1" in names
    assert "list-test-2" in names


@pytest.mark.asyncio
async def test_get_tool_by_id(client: AsyncClient):
    create = await client.post("/api/v1/tools", json={"name": "get-test", "tool_type": "builtin"})
    tool_id = create.json()["id"]

    resp = await client.get(f"/api/v1/tools/{tool_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "get-test"


@pytest.mark.asyncio
async def test_get_tool_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/tools/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_tool_via_api(client: AsyncClient):
    create = await client.post("/api/v1/tools", json={"name": "del-test", "tool_type": "builtin"})
    tool_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/tools/{tool_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/tools/{tool_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_call_nonexistent_tool(client: AsyncClient):
    resp = await client.post("/api/v1/tools/bad-id/call", json={"arguments": {}})
    assert resp.status_code == 404
