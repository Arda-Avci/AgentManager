from __future__ import annotations

import os
from functools import lru_cache


class BotConfig:
    token: str = ""
    api_base_url: str = "http://127.0.0.1:3010"
    allowed_user_ids: list[int] = []

    def __init__(self) -> None:
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.api_base_url = os.getenv("CORE_API_BASE_URL", "http://127.0.0.1:3010")
        raw = os.getenv("ALLOWED_USER_IDS", "")
        self.allowed_user_ids = [int(x.strip()) for x in raw.split(",") if x.strip()]


@lru_cache
def get_config() -> BotConfig:
    return BotConfig()
