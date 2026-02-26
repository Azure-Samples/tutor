"""FastAPI surface for the evaluation service."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from os import getenv
from typing import Mapping

from fastapi import Depends, HTTPException
from pydantic import ValidationError
from pydantic import BaseModel
from tutor_lib.config import create_app, get_settings
from tutor_lib.middleware import require_roles

from app.store import (
    CosmosEvaluationRepository,
    DatasetRecord,
    EvaluationRepository,
    InMemoryEvaluationRepository,
    RunRecord,
    to_dict,
)

app = create_app(
    title="Evaluation",
    version="0.1.0",
    description="Agent evaluation orchestration service.",
)


class RunRequest(BaseModel):
    agent_id: str
    dataset_id: str


class DatasetRequest(BaseModel):
    dataset_id: str
    name: str
    items: list[dict[str, str]]


@lru_cache(maxsize=1)
def _repository() -> EvaluationRepository:
    if getenv("EVALUATION_REPOSITORY", "cosmos").lower() == "memory":
        return InMemoryEvaluationRepository()
    try:
        settings = get_settings()
        return CosmosEvaluationRepository(settings.cosmos)
    except ValidationError:
        return InMemoryEvaluationRepository()


def reset_repository() -> None:
    _repository.cache_clear()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/datasets")
async def create_dataset(
    payload: DatasetRequest,
    _: object = Depends(require_roles("professor", "admin")),
) -> Mapping[str, object]:
    dataset = DatasetRecord(dataset_id=payload.dataset_id, name=payload.name, items=payload.items)
    saved = await _repository().create_dataset(dataset)
    return to_dict(saved)


@app.get("/datasets")
async def list_datasets(_: object = Depends(require_roles("professor", "admin"))) -> list[Mapping[str, object]]:
    datasets = await _repository().list_datasets()
    return [to_dict(dataset) for dataset in datasets]


@app.post("/evaluation/run")
async def start_run(
    payload: RunRequest,
    _: object = Depends(require_roles("professor", "admin")),
) -> Mapping[str, object]:
    dataset = await _repository().get_dataset(payload.dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    run = RunRecord(
        run_id=f"run-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        agent_id=payload.agent_id,
        dataset_id=payload.dataset_id,
        status="queued",
        total_cases=len(dataset.items),
    )
    saved = await _repository().create_run(run)
    return to_dict(saved)


@app.get("/evaluation/run/{run_id}")
async def get_run(
    run_id: str,
    _: object = Depends(require_roles("professor", "admin")),
) -> Mapping[str, object]:
    run = await _repository().get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return to_dict(run)
