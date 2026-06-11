from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    def __init__(self, name: str, config: dict | None = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs: Any) -> str:
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
        ...

    @abstractmethod
    async def validate(self) -> bool:
        ...
