from __future__ import annotations

from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import BaseProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.mock_provider import MockProvider
from src.providers.ollama_provider import OllamaProvider
from src.providers.openai_provider import OpenAIProvider

_PROVIDER_CLASSES: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "mock": MockProvider,
}


class ProviderRegistry:
    def __init__(self) -> None:
        self._instances: dict[str, BaseProvider] = {}

    def register_type(self, provider_type: str, cls: type[BaseProvider]) -> None:
        _PROVIDER_CLASSES[provider_type] = cls

    def create(
        self, provider_type: str, name: str, config: dict | None = None
    ) -> BaseProvider:
        cls = _PROVIDER_CLASSES.get(provider_type)
        if not cls:
            raise ValueError(
                f"Unknown provider type '{provider_type}'. "
                f"Available: {list(_PROVIDER_CLASSES)}"
            )
        provider = cls(name, config)
        self._instances[name] = provider
        return provider

    def get(self, name: str) -> BaseProvider | None:
        return self._instances.get(name)

    def remove(self, name: str) -> bool:
        return bool(self._instances.pop(name, None))

    def list(self) -> list[dict]:
        return [
            {
                "name": name,
                "type": _resolve_type(prov),
            }
            for name, prov in self._instances.items()
        ]

    @classmethod
    def known_types(cls) -> list[str]:
        return list(_PROVIDER_CLASSES)


def _resolve_type(provider: BaseProvider) -> str:
    cls_name = type(provider).__name__
    for t, cls in _PROVIDER_CLASSES.items():
        if cls.__name__ == cls_name:
            return t
    return cls_name.lower().replace("provider", "")
