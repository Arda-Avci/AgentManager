from __future__ import annotations

from enum import IntEnum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TaskModel


class TaskPriority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class TaskQueue:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._priorities: dict[str, TaskPriority] = {}

    async def enqueue(
        self,
        agent_id: str,
        goal: str,
        parent_task_id: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> TaskModel:
        task = TaskModel(
            agent_id=agent_id,
            goal=goal,
            parent_task_id=parent_task_id,
            status="pending",
        )
        self._session.add(task)
        await self._session.flush()
        self._priorities[task.id] = priority
        return task

    async def dequeue(self, agent_id: str) -> TaskModel | None:
        result = await self._session.execute(
            select(TaskModel)
            .where(
                TaskModel.agent_id == agent_id,
                TaskModel.status == "pending",
            )
            .order_by(TaskModel.created_at.asc())
            .limit(1)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = "running"
            await self._session.flush()
        return task

    async def list_pending(self, agent_id: str) -> list[TaskModel]:
        result = await self._session.execute(
            select(TaskModel)
            .where(
                TaskModel.agent_id == agent_id,
                TaskModel.status == "pending",
            )
            .order_by(TaskModel.created_at.asc())
        )
        return list(result.scalars().all())

    async def cancel(self, task_id: str) -> TaskModel | None:
        task = await self._session.get(TaskModel, task_id)
        if task and task.status == "pending":
            task.status = "cancelled"
            await self._session.flush()
            self._priorities.pop(task_id, None)
        return task

    async def get_task(self, task_id: str) -> TaskModel | None:
        return await self._session.get(TaskModel, task_id)
