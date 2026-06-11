from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.enums import AgentStatus
from src.database.models import TaskModel
from src.features import FeatureFlag, features
from src.router import LLMRouter
from src.tasks.executor import TaskExecutor
from src.tasks.queue import TaskQueue
from src.ws_manager import WebSocketManager

_EVALUATE_PROMPT = """You are an autonomous agent evaluator. Determine if the goal has been achieved.

Goal: {goal}
Completed so far:
{results}

Has the goal been fully achieved? Answer ONLY with a JSON object:
{{"achieved": true/false, "reason": "short explanation", "next_action": "what to do next if not achieved"}}"""

_GENERATE_NEXT_PROMPT = """You are an autonomous agent planner. Based on the progress so far, what is the next sub-task to complete the goal?

Goal: {goal}
Progress:
{results}

Respond with a single, concrete next sub-task. Be specific about what to do.
Return ONLY: {{"action": "research|write|analyze|execute", "param": "what to do next"}}"""


class ContinuousMode:
    def __init__(
        self,
        session: AsyncSession,
        router: LLMRouter,
        ws_manager: WebSocketManager | None = None,
    ):
        self._session = session
        self._router = router
        self._ws_manager = ws_manager
        self._states: dict[str, dict[str, Any]] = {}

    async def start(
        self, agent_id: str, goal: str, max_iterations: int = 10
    ) -> dict[str, Any]:
        if not features.is_enabled(FeatureFlag.CONTINUOUS_MODE):
            return {"error": "Continuous mode is disabled via feature flag"}

        if agent_id in self._states and self._states[agent_id].get("status") in ("active", "paused"):
            return {"error": "Agent already has an active continuous loop"}

        state: dict[str, Any] = {
            "status": "active",
            "goal": goal,
            "max_iterations": max_iterations,
            "current_iteration": 0,
            "results": [],
            "agent_id": agent_id,
        }
        self._states[agent_id] = state

        await self._broadcast(agent_id, "continuous:started", {
            "goal": goal, "max_iterations": max_iterations,
        })

        for iteration in range(1, max_iterations + 1):
            if state["status"] == "stopped":
                break
            if state["status"] == "paused":
                while state["status"] == "paused":
                    import asyncio
                    await asyncio.sleep(0.5)
                if state["status"] == "stopped":
                    break

            state["current_iteration"] = iteration

            task = TaskModel(
                agent_id=agent_id,
                goal=f"[Iteration {iteration}/{max_iterations}] {goal}",
                status="pending",
            )
            self._session.add(task)
            await self._session.flush()

            task.status = "running"
            await self._session.flush()

            executor = TaskExecutor(self._session, self._router, self._ws_manager)
            result_task = await executor.execute(task.id)

            entry = {
                "iteration": iteration,
                "task_id": task.id,
                "result": result_task.result if result_task else None,
            }
            state["results"].append(entry)

            await self._broadcast(agent_id, "continuous:iteration", entry)

            evaluation = await self._evaluate(goal, state["results"])
            if evaluation.get("achieved"):
                state["status"] = "completed"
                await self._broadcast(agent_id, "continuous:completed", {
                    "goal": goal,
                    "iterations": iteration,
                    "final_result": result_task.result if result_task else None,
                })
                return self._summarize(state)

        if state["status"] == "active":
            state["status"] = "completed"
            await self._broadcast(agent_id, "continuous:completed", {
                "goal": goal,
                "iterations": max_iterations,
                "note": "Reached max iterations",
            })

        return self._summarize(state)

    async def stop(self, agent_id: str) -> dict[str, Any]:
        state = self._states.get(agent_id)
        if not state:
            return {"error": "No active continuous loop for this agent"}
        state["status"] = "stopped"
        await self._broadcast(agent_id, "continuous:stopped", {})
        return self._summarize(state)

    async def pause(self, agent_id: str) -> dict[str, Any]:
        state = self._states.get(agent_id)
        if not state or state["status"] != "active":
            return {"error": "No active continuous loop to pause"}
        state["status"] = "paused"
        await self._broadcast(agent_id, "continuous:paused", {})
        return self._summarize(state)

    async def resume(self, agent_id: str) -> dict[str, Any]:
        state = self._states.get(agent_id)
        if not state or state["status"] != "paused":
            return {"error": "No paused continuous loop to resume"}
        state["status"] = "active"
        await self._broadcast(agent_id, "continuous:resumed", {})
        return self._summarize(state)

    def get_status(self, agent_id: str) -> dict[str, Any]:
        state = self._states.get(agent_id)
        if not state:
            return {"status": "inactive", "agent_id": agent_id}
        return self._summarize(state)

    async def _evaluate(self, goal: str, results: list[dict]) -> dict[str, Any]:
        results_str = json.dumps(results, indent=2)
        prompt = _EVALUATE_PROMPT.format(goal=goal, results=results_str)
        try:
            result, _ = await self._router.route(
                messages=[{"role": "user", "content": prompt}],
                primary_provider="mock",
                primary_model="mock",
            )
            cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {"achieved": False, "reason": "Evaluation failed", "next_action": "retry"}

    async def _generate_next(
        self, goal: str, results: list[dict]
    ) -> dict[str, str]:
        results_str = json.dumps(results, indent=2)
        prompt = _GENERATE_NEXT_PROMPT.format(goal=goal, results=results_str)
        try:
            result, _ = await self._router.route(
                messages=[{"role": "user", "content": prompt}],
                primary_provider="mock",
                primary_model="mock",
            )
            cleaned = result.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {"action": "execute", "param": goal}

    def _summarize(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent_id": state["agent_id"],
            "status": state["status"],
            "goal": state["goal"],
            "current_iteration": state["current_iteration"],
            "max_iterations": state["max_iterations"],
            "results_count": len(state["results"]),
            "last_result": state["results"][-1] if state["results"] else None,
        }

    async def _broadcast(self, agent_id: str, event: str, data: dict) -> None:
        if self._ws_manager:
            await self._ws_manager.broadcast(agent_id, event, data)
