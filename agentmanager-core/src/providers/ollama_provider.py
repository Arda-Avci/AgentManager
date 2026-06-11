from __future__ import annotations

import json
from typing import Any

import httpx

from src.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.model = self.config.get("model", "llama3")

    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": kwargs.get("model", self.model),
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 4096),
                    },
                },
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": kwargs.get("model", self.model),
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 4096),
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        data = json.loads(line)
                        if data.get("message", {}).get("content"):
                            yield data["message"]["content"]

    async def validate(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5)
                response.raise_for_status()
                return True
        except Exception:
            return False
