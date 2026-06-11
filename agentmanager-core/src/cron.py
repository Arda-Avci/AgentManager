from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import CronJobModel


class CronRegistry:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_jobs(self, plugin: str | None = None) -> list[CronJobModel]:
        query = select(CronJobModel).where(CronJobModel.is_active == True)
        if plugin:
            query = query.where(CronJobModel.plugin == plugin)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def create_job(self, **kwargs) -> CronJobModel:
        job = CronJobModel(**kwargs)
        self._session.add(job)
        await self._session.flush()
        return job

    async def mark_triggered(self, job_id: str) -> CronJobModel | None:
        job = await self._session.get(CronJobModel, job_id)
        if not job:
            return None
        job.last_triggered = datetime.now(timezone.utc)
        await self._session.flush()
        return job

    async def heartbeat_check(
        self, max_gap_minutes: int = 60
    ) -> list[CronJobModel]:
        result = await self._session.execute(
            select(CronJobModel).where(CronJobModel.is_active == True)
        )
        dangling = []
        now = datetime.now(timezone.utc)
        for job in result.scalars().all():
            if job.last_triggered:
                gap = (now - job.last_triggered).total_seconds() / 60
                if gap > max_gap_minutes:
                    dangling.append(job)
        return dangling

    async def activate_job(self, job_id: str) -> CronJobModel | None:
        job = await self._session.get(CronJobModel, job_id)
        if not job:
            return None
        job.is_active = True
        await self._session.flush()
        return job

    async def deactivate_job(self, job_id: str) -> CronJobModel | None:
        job = await self._session.get(CronJobModel, job_id)
        if not job:
            return None
        job.is_active = False
        await self._session.flush()
        return job

    async def get_job(self, job_id: str) -> CronJobModel | None:
        return await self._session.get(CronJobModel, job_id)

    async def delete_job(self, job_id: str) -> bool:
        job = await self._session.get(CronJobModel, job_id)
        if not job:
            return False
        await self._session.delete(job)
        await self._session.flush()
        return True

    async def get_jobs_by_agent(self, agent_id: str) -> list[CronJobModel]:
        result = await self._session.execute(
            select(CronJobModel).where(CronJobModel.agent_id == agent_id)
        )
        return list(result.scalars().all())
