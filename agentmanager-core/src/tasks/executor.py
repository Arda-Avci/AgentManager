from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TaskModel
from src.features import FeatureFlag, features
from src.logging.manager import LogManager
from src.logging.models import ThoughtLog, ActionLog
from src.router import LLMRouter
from src.ws_manager import WebSocketManager

_DECOMPOSE_PROMPT = """You are a task decomposition engine. Break the following goal into 3-5 concrete, actionable sub-tasks.

For each sub-task, provide:
- action: the action to take (research / write / analyze / execute)
- param: the specific thing to act on

Return ONLY valid JSON array, no markdown:
[
  {"action": "research", "param": "..."},
  {"action": "write", "param": "..."}
]"""

_EXECUTION_PROMPT = """You are an autonomous agent executing a task.

Goal: {goal}
Sub-task: {action} on "{param}"

Respond with:
Thoughts: What you're trying to achieve
Reasoning: Why this approach
Plan: Step-by-step plan
Criticism: Potential issues
Action: What you'll do now"""


class TaskExecutor:
    def __init__(
        self,
        session: AsyncSession,
        router: LLMRouter,
        ws_manager: WebSocketManager | None = None,
    ):
        self._session = session
        self._router = router
        self._log_manager = LogManager(ws_manager)

    async def execute(self, task_id: str) -> TaskModel | None:
        task = await self._session.get(TaskModel, task_id)
        if not task or task.status != "running":
            return task

        if not features.is_enabled(FeatureFlag.TASK_EXECUTOR):
            task.status = "failed"
            task.result = "TaskExecutor disabled via feature flag"
            await self._session.flush()
            return task

        try:
            result = await self._execute_goal(task)
            task.status = "completed"
            task.result = result
        except Exception as e:
            task.status = "failed"
            task.result = f"Error: {e}"

        await self._session.flush()
        return task

    async def _execute_goal(self, task: TaskModel) -> str:
        thoughts = await self._think(task.goal)
        await self._log_manager.log_thought(
            agent_id=task.agent_id,
            task_id=task.id,
            thought=ThoughtLog(
                agent_id=task.agent_id,
                task_id=task.id,
                thought_type="decomposition",
                content=thoughts,
            ),
        )

        try:
            sub_tasks = json.loads(thoughts)
            if not isinstance(sub_tasks, list):
                sub_tasks = []
        except (json.JSONDecodeError, TypeError):
            sub_tasks = [{"action": "execute", "param": task.goal}]

        results: list[str] = []
        for i, st in enumerate(sub_tasks):
            action = st.get("action", "execute")
            param = st.get("param", task.goal)

            prompt = _EXECUTION_PROMPT.format(goal=task.goal, action=action, param=param)

            agent_result, _ = await self._router.route(
                messages=[{"role": "user", "content": prompt}],
                primary_provider="mock",
                primary_model="mock",
            )

            await self._log_manager.log_action(
                agent_id=task.agent_id,
                task_id=task.id,
                action_log=ActionLog(
                    agent_id=task.agent_id,
                    task_id=task.id,
                    action_name=action,
                    params={"param": param, "index": i},
                    result=agent_result,
                ),
            )

            entry = {
                "step": i,
                "action": action,
                "param": param,
                "result": agent_result,
            }
            results.append(json.dumps(entry))

            chain = task.chain_of_thought or []
            chain.append(entry)
            task.chain_of_thought = chain
            await self._session.flush()

        return json.dumps(results, indent=2)

    async def _think(self, goal: str) -> str:
        result, _ = await self._router.route(
            messages=[{"role": "user", "content": _DECOMPOSE_PROMPT + f"\n\nGoal: {goal}"}],
            primary_provider="mock",
            primary_model="mock",
        )
        return result
