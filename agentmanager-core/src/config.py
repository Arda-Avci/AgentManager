from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgentManager Core"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./agentmanager.db"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 3010
    secret_key: str = "change-me-in-production"
    allowed_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
