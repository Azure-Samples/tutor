"""FastAPI surface for the evaluation service."""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from os import getenv
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError, model_validator
from tutor_lib.config import create_app, get_settings

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
    agent_name: str
    agent_version: str | None = None
    legacy_agent_id: str | None = None
    dataset_id: str
    dataset_version: str | None = None
    prompt_version: str | None = None
    thresholds: dict[str, float] = Field(default_factory=dict)
    trace_id: str | None = None
    report_uri: str | None = None
    approval_state: str = "pending_review"
    safety_metrics: dict[str, float] = Field(default_factory=dict)
    legacy_only_payload: bool = Field(default=False, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def hydrate_legacy_agent_reference(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        payload = dict(value)
        legacy_agent_id = payload.get("legacy_agent_id") or payload.get("agent_id")
        legacy_only_payload = legacy_agent_id is not None and not payload.get("agent_name")
        if legacy_agent_id is not None and not payload.get("legacy_agent_id"):
            payload["legacy_agent_id"] = str(legacy_agent_id)
        if legacy_agent_id is not None and not payload.get("agent_name"):
            payload["agent_name"] = str(legacy_agent_id)
        payload["legacy_only_payload"] = legacy_only_payload
        return payload


class DatasetRequest(BaseModel):
    dataset_id: str
    name: str
    items: list[dict[str, str]]
    dataset_version: str | None = None
    lineage: dict[str, object] = Field(default_factory=dict)


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
) -> Mapping[str, object]:
    dataset = DatasetRecord(
        dataset_id=payload.dataset_id,
        name=payload.name,
        items=payload.items,
        dataset_version=payload.dataset_version,
        lineage=payload.lineage,
    )
    saved = await _repository().create_dataset(dataset)
    return to_dict(saved)


@app.get("/datasets")
async def list_datasets() -> list[Mapping[str, object]]:
    datasets = await _repository().list_datasets()
    return [to_dict(dataset) for dataset in datasets]


def _new_run_id() -> str:
    return f"run-{uuid4().hex}"


def _is_native_run(payload: RunRequest) -> bool:
    return not payload.legacy_only_payload


def _has_text(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_release_gate_provenance(
    payload: RunRequest,
    resolved_dataset_version: str | None,
) -> None:
    if not _is_native_run(payload):
        return

    missing_fields: list[str] = []
    if not _has_text(payload.agent_version):
        missing_fields.append("agent_version")
    if not _has_text(resolved_dataset_version):
        missing_fields.append("dataset_version")
    if not _has_text(payload.prompt_version):
        missing_fields.append("prompt_version")

    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                "Native evaluation runs require release-gate provenance: "
                + ", ".join(missing_fields)
            ),
        )


@app.post("/evaluation/run")
async def start_run(
    payload: RunRequest,
) -> Mapping[str, object]:
    dataset = await _repository().get_dataset(payload.dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    resolved_dataset_version = payload.dataset_version or dataset.dataset_version
    _validate_release_gate_provenance(payload, resolved_dataset_version)

    run = RunRecord(
        run_id=_new_run_id(),
        agent_name=payload.agent_name,
        agent_version=payload.agent_version,
        legacy_agent_id=payload.legacy_agent_id,
        dataset_id=payload.dataset_id,
        dataset_version=resolved_dataset_version,
        prompt_version=payload.prompt_version,
        thresholds=payload.thresholds,
        trace_id=payload.trace_id,
        report_uri=payload.report_uri,
        approval_state=payload.approval_state,
        safety_metrics=payload.safety_metrics,
        status="queued",
        total_cases=len(dataset.items),
    )
    saved = await _repository().create_run(run)
    return to_dict(saved)


@app.get("/evaluation/run/{run_id}")
async def get_run(
    run_id: str,
) -> Mapping[str, object]:
    run = await _repository().get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return to_dict(run)
