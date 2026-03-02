"""In-process sync job queue for LMS synchronization."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import httpx
from app.adapters import BaseLMSAdapter, SyncResult

if TYPE_CHECKING:
    from app.store import SyncJobStore


@dataclass
class SyncJob:
    job_id: str
    adapter: str
    status: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    courses: int = 0
    students: int = 0
    assignments: int = 0
    scores_pushed: int = 0


class SyncJobQueue:
    def __init__(self, store: SyncJobStore) -> None:
        self._store = store

    async def create_job(self, adapter: str) -> SyncJob:
        job = SyncJob(
            job_id=str(uuid4()),
            adapter=adapter,
            status="queued",
            created_at=datetime.now(UTC).isoformat(),
        )
        return await self._store.create_job(job)

    async def get_job(self, job_id: str) -> SyncJob | None:
        return await self._store.get_job(job_id)

    def run_in_background(self, job: SyncJob, adapter: BaseLMSAdapter) -> None:
        asyncio.create_task(self._run_job(job, adapter))

    async def _run_job(self, job: SyncJob, adapter: BaseLMSAdapter) -> None:
        job.status = "running"
        job.started_at = datetime.now(UTC).isoformat()
        await self._store.update_job(job)
        try:
            result = await self._execute_sync(adapter)
            job.status = "completed"
            job.courses = result.courses
            job.students = result.students
            job.assignments = result.assignments
            job.scores_pushed = result.scores_pushed
        except (httpx.HTTPError, RuntimeError, ValueError, LookupError) as exc:
            job.status = "failed"
            job.error = str(exc)
        finally:
            job.completed_at = datetime.now(UTC).isoformat()
            await self._store.update_job(job)

    async def _execute_sync(self, adapter: BaseLMSAdapter) -> SyncResult:
        courses = await adapter.get_courses()
        students = await adapter.get_students()
        assignments = await adapter.get_assignments()
        pushed = await adapter.push_scores([])
        return SyncResult(
            adapter=adapter.provider,
            courses=len(courses),
            students=len(students),
            assignments=len(assignments),
            scores_pushed=pushed,
        )
