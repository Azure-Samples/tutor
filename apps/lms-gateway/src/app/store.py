"""Sync job persistence backends for LMS Gateway."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict

from azure.cosmos import exceptions as cosmos_exceptions
from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD

from app.jobs import SyncJob


class SyncJobStore(ABC):
    @abstractmethod
    async def create_job(self, job: SyncJob) -> SyncJob:
        raise NotImplementedError

    @abstractmethod
    async def update_job(self, job: SyncJob) -> SyncJob:
        raise NotImplementedError

    @abstractmethod
    async def get_job(self, job_id: str) -> SyncJob | None:
        raise NotImplementedError


class InMemorySyncJobStore(SyncJobStore):
    def __init__(self) -> None:
        self._jobs: dict[str, SyncJob] = {}

    async def create_job(self, job: SyncJob) -> SyncJob:
        self._jobs[job.job_id] = job
        return job

    async def update_job(self, job: SyncJob) -> SyncJob:
        self._jobs[job.job_id] = job
        return job

    async def get_job(self, job_id: str) -> SyncJob | None:
        return self._jobs.get(job_id)


class CosmosSyncJobStore(SyncJobStore):
    def __init__(self, cosmos: CosmosConfig) -> None:
        self._crud = CosmosCRUD(cosmos.resources_container, cosmos)

    async def create_job(self, job: SyncJob) -> SyncJob:
        await self._crud.create_item(self._to_payload(job))
        return job

    async def update_job(self, job: SyncJob) -> SyncJob:
        await self._crud.create_item(self._to_payload(job))
        return job

    async def get_job(self, job_id: str) -> SyncJob | None:
        try:
            item = await self._crud.read_item(job_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
        if item.get("docType") != "lms_sync_job":
            return None
        return self._from_payload(item)

    @staticmethod
    def _to_payload(job: SyncJob) -> dict[str, object]:
        payload = asdict(job)
        payload["id"] = job.job_id
        payload["docType"] = "lms_sync_job"
        return payload

    @staticmethod
    def _from_payload(payload: dict[str, object]) -> SyncJob:
        def parse_int(value: object) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.strip():
                return int(value)
            return 0

        def parse_optional_str(value: object) -> str | None:
            if isinstance(value, str) and value:
                return value
            return None

        return SyncJob(
            job_id=str(payload["job_id"]),
            adapter=str(payload["adapter"]),
            status=str(payload["status"]),
            created_at=str(payload["created_at"]),
            started_at=parse_optional_str(payload.get("started_at")),
            completed_at=parse_optional_str(payload.get("completed_at")),
            error=parse_optional_str(payload.get("error")),
            courses=parse_int(payload.get("courses")),
            students=parse_int(payload.get("students")),
            assignments=parse_int(payload.get("assignments")),
            scores_pushed=parse_int(payload.get("scores_pushed")),
        )
