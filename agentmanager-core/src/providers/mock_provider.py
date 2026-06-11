from __future__ import annotations

from typing import Any

from src.providers.base import BaseProvider


class MockProvider(BaseProvider):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self._mode = self.config.get("mode", "success")
        self._response_text = self.config.get("response", "Mock response")
        self.called = False

    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        self.called = True
        if self._mode in ("rate_limit", "timeout", "error_500"):
            raise _error_for_mode(self._mode)
        return self._response_text

    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        self.called = True
        if self._mode in ("rate_limit", "timeout", "error_500"):
            raise _error_for_mode(self._mode)
        yield self._response_text

    async def validate(self) -> bool:
        return self._mode == "success"


def _error_for_mode(mode: str) -> Exception:
    if mode == "rate_limit":
        return Exception("Rate limit exceeded (mock)")
    if mode == "timeout":
        return TimeoutError("Request timed out (mock)")
    if mode == "error_500":
        return Exception("Internal server error (mock)")
    return Exception("Unknown mock error")
