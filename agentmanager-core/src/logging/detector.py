from __future__ import annotations

from collections import Counter

from src.features import FeatureFlag, features
from src.logging.manager import LogManager
from src.logging.models import ActionLog


class LoopDetector:
    def __init__(self, log_manager: LogManager):
        self._log_manager = log_manager

    def detect_loop(self, agent_id: str, task_id: str, recent_actions: int = 10) -> bool:
        if not features.is_enabled(FeatureFlag.LOOP_DETECTION):
            return False
        chain = self._log_manager.get_chain(agent_id, task_id)
        actions = [e.action for e in chain if e.type == "action" and e.action]
        recent = actions[-recent_actions:]
        if len(recent) < 3:
            return False
        signatures = [f"{a.action_name}:{json_params(a.params)}" for a in recent]
        counts = Counter(signatures)
        most_common_count = counts.most_common(1)[0][1] if counts else 0
        return most_common_count >= 3

    def suggest_fix(self, agent_id: str, task_id: str) -> str | None:
        chain = self._log_manager.get_chain(agent_id, task_id)
        actions = [e.action for e in chain if e.type == "action" and e.action]
        if len(actions) < 3:
            return None
        signatures = [f"{a.action_name}:{json_params(a.params)}" for a in actions]
        counts = Counter(signatures)
        repeat, count = counts.most_common(1)[0] if counts else ("", 0)
        if count < 3:
            return None
        action_name = repeat.split(":")[0]
        return (
            f"Loop detected: '{action_name}' repeated {count} times. "
            f"Suggested fix: Try a different approach or break the task into smaller steps."
        )


def json_params(params: dict | None) -> str:
    if not params:
        return ""
    import json
    return json.dumps(params, sort_keys=True)
