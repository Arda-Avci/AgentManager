from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TaskModel
from src.tasks.queue import TaskPriority, TaskQueue


@pytest.mark.asyncio
async def test_enqueue_task(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.enqueue(agent_id="agent-1", goal="Test goal")
    assert task.id is not None
    assert task.agent_id == "agent-1"
    assert task.goal == "Test goal"
    assert task.status == "pending"


@pytest.mark.asyncio
async def test_enqueue_with_priority(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.enqueue(agent_id="agent-1", goal="High priority", priority=TaskPriority.HIGH)
    assert task.goal == "High priority"
    assert task.status == "pending"


@pytest.mark.asyncio
async def test_enqueue_with_parent(db_session: AsyncSession):
    q = TaskQueue(db_session)
    parent = await q.enqueue(agent_id="agent-1", goal="Parent task")
    child = await q.enqueue(agent_id="agent-1", goal="Child task", parent_task_id=parent.id)
    assert child.parent_task_id == parent.id


@pytest.mark.asyncio
async def test_dequeue_task(db_session: AsyncSession):
    q = TaskQueue(db_session)
    await q.enqueue(agent_id="agent-1", goal="Task 1")
    await q.enqueue(agent_id="agent-1", goal="Task 2")

    task = await q.dequeue("agent-1")
    assert task is not None
    assert task.goal == "Task 1"
    assert task.status == "running"


@pytest.mark.asyncio
async def test_dequeue_empty(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.dequeue("nonexistent")
    assert task is None


@pytest.mark.asyncio
async def test_list_pending(db_session: AsyncSession):
    q = TaskQueue(db_session)
    await q.enqueue(agent_id="agent-1", goal="Task A")
    await q.enqueue(agent_id="agent-1", goal="Task B")
    tasks = await q.list_pending("agent-1")
    assert len(tasks) == 2
    assert all(t.status == "pending" for t in tasks)


@pytest.mark.asyncio
async def test_cancel_task(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.enqueue(agent_id="agent-1", goal="Cancel me")
    cancelled = await q.cancel(task.id)
    assert cancelled is not None
    assert cancelled.status == "cancelled"

    pending = await q.list_pending("agent-1")
    assert len(pending) == 0


@pytest.mark.asyncio
async def test_cancel_running_task(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.enqueue(agent_id="agent-1", goal="Running task")
    await q.dequeue("agent-1")
    cancelled = await q.cancel(task.id)
    assert cancelled is None or cancelled.status == "running"


@pytest.mark.asyncio
async def test_get_task_by_id(db_session: AsyncSession):
    q = TaskQueue(db_session)
    task = await q.enqueue(agent_id="agent-1", goal="Find me")
    found = await q.get_task(task.id)
    assert found is not None
    assert found.id == task.id


@pytest.mark.asyncio
async def test_get_task_not_found(db_session: AsyncSession):
    q = TaskQueue(db_session)
    found = await q.get_task("nonexistent")
    assert found is None


@pytest.mark.asyncio
async def test_dequeue_fifo_order(db_session: AsyncSession):
    q = TaskQueue(db_session)
    t1 = await q.enqueue(agent_id="agent-1", goal="First")
    t2 = await q.enqueue(agent_id="agent-1", goal="Second")
    t3 = await q.enqueue(agent_id="agent-1", goal="Third")

    dequeued1 = await q.dequeue("agent-1")
    assert dequeued1.id == t1.id
    dequeued2 = await q.dequeue("agent-1")
    assert dequeued2.id == t2.id
    dequeued3 = await q.dequeue("agent-1")
    assert dequeued3.id == t3.id


@pytest.mark.asyncio
async def test_task_execute_route(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/agents",
        json={"name": "task-agent", "provider": "openai", "model": "gpt-4o"},
    )
    agent_id = create_resp.json()["id"]

    task_resp = await client.post(
        "/api/v1/tasks",
        json={"agent_id": agent_id, "goal": "Test execution"},
    )
    task_id = task_resp.json()["id"]

    exec_resp = await client.post(f"/api/v1/tasks/execute/{task_id}")
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["id"] == task_id
    assert data["status"] in ("completed", "failed")


@pytest.mark.asyncio
async def test_execute_nonexistent_task(client: AsyncClient):
    resp = await client.post("/api/v1/tasks/execute/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_agent_queue_route(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/agents",
        json={"name": "queue-agent", "provider": "openai", "model": "gpt-4o"},
    )
    agent_id = create_resp.json()["id"]

    await client.post("/api/v1/tasks", json={"agent_id": agent_id, "goal": "Queue task 1"})
    await client.post("/api/v1/tasks", json={"agent_id": agent_id, "goal": "Queue task 2"})

    resp = await client.get(f"/api/v1/tasks/queue/{agent_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
