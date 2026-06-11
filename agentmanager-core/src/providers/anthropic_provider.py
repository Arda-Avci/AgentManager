from __future__ import annotations

from typing import Any

from anthropic import AsyncAnthropic

from src.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.client = AsyncAnthropic(api_key=self.config.get("api_key"))
        self.model = self.config.get("model", "claude-sonnet-4-20250514")

    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})

        response = await self.client.messages.create(
            model=kwargs.get("model", self.model),
            system=system_msg,
            messages=chat_messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.content[0].text

    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})

        async with self.client.messages.stream(
            model=kwargs.get("model", self.model),
            system=system_msg,
            messages=chat_messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def validate(self) -> bool:
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False
