from __future__ import annotations

import pytest

from src.providers.base import BaseProvider
from src.router import LLMRouter


class MockProvider(BaseProvider):
    def __init__(self, name: str, fail: bool = False):
        super().__init__(name)
        self.fail = fail
        self.called = False

    async def chat(self, messages: list[dict], **kwargs) -> str:
        self.called = True
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
        return f"{self.name} response"

    async def chat_stream(self, messages: list[dict], **kwargs):
        self.called = True
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
        yield f"{self.name} stream"

    async def validate(self) -> bool:
        return not self.fail


@pytest.mark.asyncio
async def test_route_single_provider():
    router = LLMRouter()
    router.register_provider("mock", MockProvider("mock"))
    result, used = await router.route(
        [{"role": "user", "content": "hello"}],
        primary_provider="mock",
        primary_model="mock-model",
    )
    assert result == "mock response"
    assert used == "mock/mock-model"


@pytest.mark.asyncio
async def test_route_fallback():
    router = LLMRouter()
    router.register_provider("primary", MockProvider("primary", fail=True))
    router.register_provider("backup", MockProvider("backup"))
    result, used = await router.route(
        [{"role": "user", "content": "hello"}],
        primary_provider="primary",
        primary_model="primary-model",
        fallback_chain=[{"provider": "backup", "model": "backup-model"}],
    )
    assert result == "backup response"
    assert used == "backup/backup-model"


@pytest.mark.asyncio
async def test_route_all_fail():
    router = LLMRouter()
    router.register_provider("fail1", MockProvider("fail1", fail=True))
    router.register_provider("fail2", MockProvider("fail2", fail=True))
    with pytest.raises(RuntimeError, match="All providers failed"):
        await router.route(
            [{"role": "user", "content": "hello"}],
            primary_provider="fail1",
            primary_model="m1",
            fallback_chain=[{"provider": "fail2", "model": "m2"}],
        )


@pytest.mark.asyncio
async def test_route_no_provider():
    router = LLMRouter()
    with pytest.raises(RuntimeError):
        await router.route(
            [{"role": "user", "content": "hello"}],
            primary_provider="nonexistent",
            primary_model="m1",
        )
