from __future__ import annotations

import pytest

from src.providers.base import BaseProvider
from src.providers.mock_provider import MockProvider
from src.providers.registry import ProviderRegistry
from src.router import LLMRouter


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_success_mode(self):
        p = MockProvider("test", {"mode": "success", "response": "Hello!"})
        result = await p.chat([{"role": "user", "content": "hi"}])
        assert result == "Hello!"
        assert p.called

    @pytest.mark.asyncio
    async def test_rate_limit_mode(self):
        p = MockProvider("test", {"mode": "rate_limit"})
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await p.chat([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_timeout_mode(self):
        p = MockProvider("test", {"mode": "timeout"})
        with pytest.raises(TimeoutError, match="timed out"):
            await p.chat([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_error_500_mode(self):
        p = MockProvider("test", {"mode": "error_500"})
        with pytest.raises(Exception, match="Internal server error"):
            await p.chat([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_stream_success(self):
        p = MockProvider("test", {"mode": "success", "response": "Hello!"})
        chunks = []
        async for chunk in p.chat_stream([{"role": "user", "content": "hi"}]):
            chunks.append(chunk)
        assert chunks == ["Hello!"]

    @pytest.mark.asyncio
    async def test_validate_success(self):
        p = MockProvider("test", {"mode": "success"})
        assert await p.validate() is True

    @pytest.mark.asyncio
    async def test_validate_fail(self):
        p = MockProvider("test", {"mode": "error_500"})
        assert await p.validate() is False


class TestProviderRegistry:
    def test_create_provider(self):
        registry = ProviderRegistry()
        p = registry.create("mock", "test-mock", {"response": "hello"})
        assert isinstance(p, BaseProvider)
        assert registry.get("test-mock") is p

    def test_create_unknown_type(self):
        registry = ProviderRegistry()
        with pytest.raises(ValueError, match="Unknown provider type"):
            registry.create("nonexistent", "x")

    def test_remove_provider(self):
        registry = ProviderRegistry()
        registry.create("mock", "test-mock")
        assert registry.remove("test-mock") is True
        assert registry.get("test-mock") is None
        assert registry.remove("nonexistent") is False

    def test_list_providers(self):
        registry = ProviderRegistry()
        registry.create("mock", "m1")
        registry.create("mock", "m2")
        items = registry.list()
        assert len(items) == 2
        names = {i["name"] for i in items}
        assert names == {"m1", "m2"}
        assert all(i["type"] == "mock" for i in items)

    def test_known_types(self):
        types = ProviderRegistry.known_types()
        assert "mock" in types
        assert "openai" in types
        assert "anthropic" in types
        assert "gemini" in types
        assert "ollama" in types


class TestRegistryRouterIntegration:
    @pytest.mark.asyncio
    async def test_registry_feeds_router(self):
        registry = ProviderRegistry()
        router = LLMRouter()

        p = registry.create("mock", "my-mock", {"response": "router ok"})
        router.register_provider("my-mock", p)

        result, used = await router.route(
            [{"role": "user", "content": "hi"}],
            primary_provider="my-mock",
            primary_model="mock-model",
        )
        assert result == "router ok"
        assert used == "my-mock/mock-model"

    @pytest.mark.asyncio
    async def test_registry_provider_in_router_fallback(self):
        registry = ProviderRegistry()
        router = LLMRouter()

        p1 = registry.create("mock", "failing", {"mode": "error_500"})
        p2 = registry.create("mock", "backup", {"response": "fallback ok"})
        router.register_provider("failing", p1)
        router.register_provider("backup", p2)

        result, used = await router.route(
            [{"role": "user", "content": "hi"}],
            primary_provider="failing",
            primary_model="m1",
            fallback_chain=[{"provider": "backup", "model": "m2"}],
        )
        assert result == "fallback ok"
        assert used == "backup/m2"
