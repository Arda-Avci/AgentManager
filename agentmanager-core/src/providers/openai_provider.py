from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from src.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.client = AsyncOpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )
        self.model = self.config.get("model", "gpt-4o")

    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def validate(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
