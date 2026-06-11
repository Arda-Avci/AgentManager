from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    parameters: type[BaseModel] = BaseModel

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    @abstractmethod
    async def execute(self, params: BaseModel) -> Any:
        ...

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.model_json_schema(),
        }
