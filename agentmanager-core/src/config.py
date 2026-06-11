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

    master_key: str = "change-me-master-key-32-bytes-long!"

    rate_limit_per_minute: int = 60

    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
