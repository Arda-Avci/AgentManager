from __future__ import annotations

from typing import Any

from google import genai

from src.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.client = genai.Client(api_key=self.config.get("api_key"))
        self.model = self.config.get("model", "gemini-2.0-flash")

    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        contents = _convert_messages(messages)

        response = await self.client.aio.models.generate_content(
            model=kwargs.get("model", self.model),
            contents=contents,
            config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 4096),
            },
        )
        return response.text or ""

    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        contents = _convert_messages(messages)

        async for chunk in self.client.aio.models.generate_content_stream(
            model=kwargs.get("model", self.model),
            contents=contents,
            config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 4096),
            },
        ):
            if chunk.text:
                yield chunk.text

    async def validate(self) -> bool:
        try:
            await self.client.aio.models.get(model=self.model)
            return True
        except Exception:
            return False


def _convert_messages(messages: list[dict]) -> list[dict]:
    contents = []
    for msg in messages:
        role = "user" if msg["role"] in ("user", "system") else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents
