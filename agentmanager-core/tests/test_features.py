from __future__ import annotations

import pytest
from httpx import AsyncClient

from src.features import FeatureFlag, FeatureFlagManager


@pytest.fixture
def flag_mgr(tmp_path):
    path = tmp_path / "test_flags.json"
    return FeatureFlagManager(path)


def test_default_flags(flag_mgr: FeatureFlagManager):
    assert flag_mgr.is_enabled(FeatureFlag.MCP_ENABLED) is True
    assert flag_mgr.is_enabled(FeatureFlag.COT_LOGGING) is True
    assert flag_mgr.is_enabled(FeatureFlag.TASK_QUEUE) is True
    assert flag_mgr.is_enabled(FeatureFlag.TELEGRAM_ENABLED) is False


def test_set_enabled(flag_mgr: FeatureFlagManager):
    assert flag_mgr.is_enabled(FeatureFlag.TELEGRAM_ENABLED) is False
    flag_mgr.set_enabled(FeatureFlag.TELEGRAM_ENABLED, True)
    assert flag_mgr.is_enabled(FeatureFlag.TELEGRAM_ENABLED) is True


def test_all_flags(flag_mgr: FeatureFlagManager):
    flags = flag_mgr.all_flags()
    assert isinstance(flags, dict)
    assert len(flags) >= 5
    assert FeatureFlag.MCP_ENABLED in flags or "MCP_ENABLED" in flags


def test_reset_flags(flag_mgr: FeatureFlagManager):
    flag_mgr.set_enabled(FeatureFlag.TELEGRAM_ENABLED, True)
    assert flag_mgr.is_enabled(FeatureFlag.TELEGRAM_ENABLED) is True
    flag_mgr.reset()
    assert flag_mgr.is_enabled(FeatureFlag.TELEGRAM_ENABLED) is False


@pytest.mark.asyncio
async def test_list_features_route(client: AsyncClient):
    resp = await client.get("/api/v1/features")
    assert resp.status_code == 200
    data = resp.json()
    assert "flags" in data
    assert isinstance(data["flags"], dict)
    assert "MCP_ENABLED" in data["flags"]


@pytest.mark.asyncio
async def test_update_feature_route(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/features/TELEGRAM_ENABLED",
        json={"value": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["flags"]["TELEGRAM_ENABLED"] is True


@pytest.mark.asyncio
async def test_update_unknown_feature(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/features/UNKNOWN_FLAG",
        json={"value": True},
    )
    assert resp.status_code == 404
