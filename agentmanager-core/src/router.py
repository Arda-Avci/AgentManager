from __future__ import annotations

from typing import Any

from src.providers.base import BaseProvider
from src.providers.openai_provider import OpenAIProvider


class LLMRouter:
    def __init__(self):
        self._providers: dict[str, BaseProvider] = {}

    def register_provider(self, name: str, provider: BaseProvider) -> None:
        self._providers[name] = provider

    def get_provider(self, name: str) -> BaseProvider | None:
        return self._providers.get(name)

    async def route(
        self,
        messages: list[dict],
        primary_provider: str,
        primary_model: str,
        fallback_chain: list[dict] | None = None,
        **kwargs: Any,
    ) -> tuple[str, str]:
        attempts = [(primary_provider, primary_model)]
        if fallback_chain:
            attempts.extend(
                (fb.get("provider", primary_provider), fb.get("model", primary_model))
                for fb in fallback_chain
            )

        last_error: Exception | None = None
        for provider_name, model_name in attempts:
            provider = self._providers.get(provider_name)
            if not provider:
                continue
            try:
                result = await provider.chat(messages, model=model_name, **kwargs)
                return result, f"{provider_name}/{model_name}"
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"All providers failed for primary={primary_provider}/{primary_model}. "
            f"Last error: {last_error}"
        )

    async def route_stream(
        self,
        messages: list[dict],
        primary_provider: str,
        primary_model: str,
        fallback_chain: list[dict] | None = None,
        **kwargs: Any,
    ) -> Any:
        attempts = [(primary_provider, primary_model)]
        if fallback_chain:
            attempts.extend(
                (fb.get("provider", primary_provider), fb.get("model", primary_model))
                for fb in fallback_chain
            )

        for provider_name, model_name in attempts:
            provider = self._providers.get(provider_name)
            if not provider:
                continue
            try:
                async for chunk in provider.chat_stream(messages, model=model_name, **kwargs):
                    yield chunk
                return
            except Exception:
                continue

        raise RuntimeError(f"All providers failed for stream")
