"""FastAPI surface for the LMS gateway service."""

from __future__ import annotations

from datetime import UTC, datetime
from datetime import timedelta
from functools import lru_cache
from os import getenv

from fastapi import HTTPException
from pydantic import BaseModel, Field
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from tutor_lib.config import create_app, get_settings

from app.adapters import BaseLMSAdapter, CanvasAdapter, MoodleAdapter
from app.jobs import SyncJobQueue
from app.store import CosmosSyncJobStore, InMemorySyncJobStore, SyncJobStore

app = create_app(
    title="LMS Gateway",
    version="0.1.0",
    description="Adapter gateway for external LMS synchronization.",
)


class SyncRequest(BaseModel):
    adapter: str


class SyncScheduleRequest(BaseModel):
    adapter: str
    interval_minutes: int = 60


class LMSGatewaySettings(BaseSettings):
    moodle_base_url: str = Field(default="", alias="LMS_MOODLE_BASE_URL")
    moodle_token: str = Field(default="", alias="LMS_MOODLE_TOKEN")
    canvas_base_url: str = Field(default="", alias="LMS_CANVAS_BASE_URL")
    canvas_token: str = Field(default="", alias="LMS_CANVAS_TOKEN")


@lru_cache(maxsize=1)
def _job_queue() -> SyncJobQueue:
    return SyncJobQueue(_job_store())


@lru_cache(maxsize=1)
def _job_store() -> SyncJobStore:
    if getenv("LMS_JOB_STORE", "cosmos").lower() == "memory":
        return InMemorySyncJobStore()
    try:
        settings = get_settings()
        return CosmosSyncJobStore(settings.cosmos)
    except ValidationError:
        return InMemorySyncJobStore()


@lru_cache(maxsize=1)
def _settings() -> LMSGatewaySettings:
    return LMSGatewaySettings()  # type: ignore[call-arg]


def _adapter_registry() -> dict[str, BaseLMSAdapter]:
    settings = _settings()
    return {
        "moodle": MoodleAdapter(base_url=settings.moodle_base_url, token=settings.moodle_token),
        "canvas": CanvasAdapter(base_url=settings.canvas_base_url, token=settings.canvas_token),
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/lms/sync")
async def sync(
    payload: SyncRequest,
) -> dict[str, str]:
    adapter = _adapter_registry().get(payload.adapter.lower())
    if adapter is None:
        raise HTTPException(status_code=400, detail="Unsupported LMS adapter")

    courses = await adapter.get_courses()
    students = await adapter.get_students()
    assignments = await adapter.get_assignments()
    pushed = await adapter.push_scores([])

    return {
        "adapter": adapter.provider,
        "status": "completed",
        "courses": str(len(courses)),
        "students": str(len(students)),
        "assignments": str(len(assignments)),
        "scores_pushed": str(pushed),
        "synced_at": datetime.now(UTC).isoformat(),
    }


@app.post("/lms/sync/schedule")
async def schedule_sync(
    payload: SyncScheduleRequest,
) -> dict[str, str]:
    adapter = _adapter_registry().get(payload.adapter.lower())
    if adapter is None:
        raise HTTPException(status_code=400, detail="Unsupported LMS adapter")
    if payload.interval_minutes < 1:
        raise HTTPException(status_code=400, detail="interval_minutes must be >= 1")

    now = datetime.now(UTC)
    next_run = now + timedelta(minutes=payload.interval_minutes)
    job = await _job_queue().create_job(adapter.provider)
    _job_queue().run_in_background(job, adapter)
    return {
        "job_id": job.job_id,
        "adapter": adapter.provider,
        "status": "scheduled",
        "scheduled_at": now.isoformat(),
        "next_run": next_run.isoformat(),
        "interval_minutes": str(payload.interval_minutes),
    }


@app.get("/lms/sync/jobs/{job_id}")
async def get_sync_job(
    job_id: str,
) -> dict[str, str]:
    job = await _job_queue().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    return {
        "job_id": job.job_id,
        "adapter": job.adapter,
        "status": job.status,
        "created_at": job.created_at,
        "started_at": job.started_at or "",
        "completed_at": job.completed_at or "",
        "error": job.error or "",
        "courses": str(job.courses),
        "students": str(job.students),
        "assignments": str(job.assignments),
        "scores_pushed": str(job.scores_pushed),
    }
