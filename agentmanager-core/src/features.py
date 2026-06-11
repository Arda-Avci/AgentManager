from __future__ import annotations

import json
import os
from enum import StrEnum
from pathlib import Path
from typing import Any


class FeatureFlag(StrEnum):
    MCP_ENABLED = "MCP_ENABLED"
    TELEGRAM_ENABLED = "TELEGRAM_ENABLED"
    COT_LOGGING = "COT_LOGGING"
    TASK_QUEUE = "TASK_QUEUE"
    TASK_EXECUTOR = "TASK_EXECUTOR"
    LOOP_DETECTION = "LOOP_DETECTION"
    STREAMING_CHAT = "STREAMING_CHAT"
    AUDIT_LOGGING = "AUDIT_LOGGING"
    CONTINUOUS_MODE = "CONTINUOUS_MODE"


_DEFAULT_FLAGS: dict[str, bool] = {
    FeatureFlag.MCP_ENABLED: True,
    FeatureFlag.TELEGRAM_ENABLED: False,
    FeatureFlag.COT_LOGGING: True,
    FeatureFlag.TASK_QUEUE: True,
    FeatureFlag.TASK_EXECUTOR: True,
    FeatureFlag.LOOP_DETECTION: True,
    FeatureFlag.STREAMING_CHAT: True,
    FeatureFlag.AUDIT_LOGGING: False,
    FeatureFlag.CONTINUOUS_MODE: False,
}


class FeatureFlagManager:
    def __init__(self, path: str | Path | None = None):
        self._path = Path(path) if path else Path.cwd() / "flags.json"
        self._flags: dict[str, bool] = dict(_DEFAULT_FLAGS)
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                self._flags.update(data)
            except (json.JSONDecodeError, OSError):
                pass
        for key in list(self._flags):
            env_val = os.environ.get(f"FLAG_{key}")
            if env_val is not None:
                self._flags[key] = env_val.lower() in ("1", "true", "yes")

    def _save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._flags, indent=2))
        except OSError:
            pass

    def is_enabled(self, flag: FeatureFlag | str) -> bool:
        key = str(flag)
        return self._flags.get(key, False)

    def set_enabled(self, flag: FeatureFlag | str, value: bool) -> None:
        self._flags[str(flag)] = value
        self._save()

    def all_flags(self) -> dict[str, bool]:
        return dict(self._flags)

    def reset(self) -> None:
        self._flags = dict(_DEFAULT_FLAGS)
        self._save()


features = FeatureFlagManager()
