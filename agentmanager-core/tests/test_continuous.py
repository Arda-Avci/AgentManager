from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.agents.continuous import ContinuousMode
from src.database.engine import Base
from src.features import FeatureFlag, features
from src.router import LLMRouter

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture(autouse=True)
def _enable_continuous():
    features.set_enabled(FeatureFlag.CONTINUOUS_MODE, True)
    yield
    features.set_enabled(FeatureFlag.CONTINUOUS_MODE, False)


@pytest.fixture
def router():
    from src.providers.mock_provider import MockProvider

    r = LLMRouter()
    r.register_provider(
        "mock",
        MockProvider({"mock": {"response": '{"achieved": true, "reason": "done", "next_action": null}'}}),
    )
    return r


@pytest.mark.asyncio
async def test_continuous_start_completes(db_session, router):
    cm = ContinuousMode(db_session, router)
    result = await cm.start("agent-1", "Test loop", max_iterations=2)
    assert result["status"] == "completed"
    assert result["agent_id"] == "agent-1"
    assert result["goal"] == "Test loop"
    assert result["results_count"] >= 1


@pytest.mark.asyncio
async def test_continuous_feature_flag_disabled(db_session, router):
    features.set_enabled(FeatureFlag.CONTINUOUS_MODE, False)
    cm = ContinuousMode(db_session, router)
    result = await cm.start("agent-2", "Should not run", max_iterations=2)
    assert "error" in result


@pytest.mark.asyncio
async def test_continuous_stop_no_loop(db_session, router):
    cm = ContinuousMode(db_session, router)
    result = await cm.stop("agent-3")
    assert "error" in result


@pytest.mark.asyncio
async def test_continuous_stop_after_start(db_session, router):
    cm = ContinuousMode(db_session, router)
    await cm.start("agent-3b", "Test stop", max_iterations=5)
    result = await cm.stop("agent-3b")
    assert result["status"] in ("stopped", "completed")


@pytest.mark.asyncio
async def test_continuous_get_status_inactive(db_session, router):
    cm = ContinuousMode(db_session, router)
    status = cm.get_status("nonexistent")
    assert status["status"] == "inactive"


@pytest.mark.asyncio
async def test_continuous_get_status_after_start(db_session, router):
    cm = ContinuousMode(db_session, router)
    await cm.start("agent-5", "Status check", max_iterations=3)
    status = cm.get_status("agent-5")
    assert status["agent_id"] == "agent-5"
    assert status["goal"] == "Status check"
    assert status["status"] in ("completed", "active")
