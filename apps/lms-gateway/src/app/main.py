"""FastAPI surface for the LMS gateway service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from os import getenv
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings
from tutor_lib.config import create_app, get_settings
from tutor_lib.integration_hub import (
    AttemptSubmission,
    CanonicalValidationError,
    ConnectorHealth,
    ConnectorState,
    CosmosConnectorStateRepository,
    CosmosDeadLetterRepository,
    CosmosIdempotencyRepository,
    DeadLetterEntry,
    DeadLetterRepository,
    EngagementSignal,
    Enrollment,
    InMemoryConnectorStateRepository,
    InMemoryDeadLetterRepository,
    InMemoryIdempotencyRepository,
    PerformanceResult,
    build_idempotency_key,
    canonical_to_learner_record_event,
)
from tutor_lib.learner_record import (
    CosmosLearnerRecordEventRepository,
    InMemoryLearnerRecordEventRepository,
    LearnerRecordEventRepository,
)
from tutor_lib.middleware import get_authenticated_user
from tutor_lib.middleware.auth import AuthenticatedUser

from app.adapters import BaseLMSAdapter, CanvasAdapter, MoodleAdapter
from app.jobs import SyncJobQueue
from app.store import CosmosSyncJobStore, InMemorySyncJobStore, SyncJobStore

AuthenticatedUserDependency = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]

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
    repository_mode: str = Field(default="cosmos", alias="LMS_REPOSITORY_MODE")


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
def _connector_state_repo() -> InMemoryConnectorStateRepository | CosmosConnectorStateRepository:
    settings = _settings()
    if str(settings.repository_mode).lower() == "memory":
        return InMemoryConnectorStateRepository()
    try:
        cosmos_settings = get_settings()
        return CosmosConnectorStateRepository(cosmos_settings.cosmos)
    except ValidationError:
        return InMemoryConnectorStateRepository()


@lru_cache(maxsize=1)
def _idempotency_repo() -> InMemoryIdempotencyRepository | CosmosIdempotencyRepository:
    settings = _settings()
    if str(settings.repository_mode).lower() == "memory":
        return InMemoryIdempotencyRepository()
    try:
        cosmos_settings = get_settings()
        return CosmosIdempotencyRepository(cosmos_settings.cosmos)
    except ValidationError:
        return InMemoryIdempotencyRepository()


@lru_cache(maxsize=1)
def _dead_letter_repo() -> DeadLetterRepository:
    settings = _settings()
    if str(settings.repository_mode).lower() == "memory":
        return InMemoryDeadLetterRepository()
    try:
        cosmos_settings = get_settings()
        return CosmosDeadLetterRepository(cosmos_settings.cosmos)
    except ValidationError:
        return InMemoryDeadLetterRepository()


@lru_cache(maxsize=1)
def _learner_record_repo() -> LearnerRecordEventRepository:
    settings = _settings()
    if str(settings.repository_mode).lower() == "memory":
        return InMemoryLearnerRecordEventRepository()
    try:
        cosmos_settings = get_settings()
        return CosmosLearnerRecordEventRepository(cosmos_settings.cosmos)
    except ValidationError:
        return InMemoryLearnerRecordEventRepository()


@lru_cache(maxsize=1)
def _settings() -> LMSGatewaySettings:
    return LMSGatewaySettings()  # type: ignore[call-arg]


def _adapter_registry() -> dict[str, BaseLMSAdapter]:
    settings = _settings()
    return {
        "moodle": MoodleAdapter(base_url=settings.moodle_base_url, token=settings.moodle_token),
        "canvas": CanvasAdapter(base_url=settings.canvas_base_url, token=settings.canvas_token),
    }


_SOURCE_EVENT_ID_FIELDS = {
    "enrollment": "external_enrollment_id",
    "submission": "external_submission_id",
    "performance": "external_result_id",
    "engagement": "external_signal_id",
}
_CANONICAL_ENVELOPE_FIELDS = (
    "tenant_id",
    "provider",
    "provider_instance_id",
)
_PUBLIC_CONNECTOR_CONFIG_KEYS = (
    "api_url",
    "base_url",
    "course_filters",
    "display_name",
    "enabled",
    "sync_interval_minutes",
)
_PUBLIC_COURSE_FILTER_KEYS = (
    "course_codes",
    "course_ids",
    "include_archived",
    "term_ids",
)
_PUBLIC_SCALAR_TYPES = (str, int, float, bool)


def _tenant_id_from_connector_id(connector_id: str) -> str | None:
    _, separator, tenant_id = connector_id.rpartition(":")
    if not separator or not tenant_id:
        return None
    return tenant_id


def _public_connector_config(config: dict[str, object] | None) -> dict[str, object]:
    if not config:
        return {}
    public_config: dict[str, object] = {}
    for field_name in _PUBLIC_CONNECTOR_CONFIG_KEYS:
        if field_name not in config:
            continue
        public_value = _public_connector_config_value(field_name, config[field_name])
        if public_value is not None:
            public_config[field_name] = public_value
    return public_config


def _public_connector_config_value(field_name: str, value: object) -> object | None:
    if field_name == "course_filters":
        return _public_course_filters(value)
    if isinstance(value, _PUBLIC_SCALAR_TYPES):
        return value
    if isinstance(value, list):
        return [item for item in value if isinstance(item, _PUBLIC_SCALAR_TYPES)]
    return None


def _public_course_filters(value: object) -> object | None:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, _PUBLIC_SCALAR_TYPES)]
    if not isinstance(value, dict):
        return None

    filters: dict[str, object] = {}
    for field_name in _PUBLIC_COURSE_FILTER_KEYS:
        if field_name not in value:
            continue
        field_value = value[field_name]
        if isinstance(field_value, _PUBLIC_SCALAR_TYPES):
            filters[field_name] = field_value
        elif isinstance(field_value, list):
            filters[field_name] = [
                item for item in field_value if isinstance(item, _PUBLIC_SCALAR_TYPES)
            ]
    return filters or None


def _enforce_tenant_scope(user: AuthenticatedUser, tenant_id: str) -> None:
    if tenant_id not in user.scope.institution_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested tenant is outside the caller scope",
        )


def _source_event_id_from_payload(event_type: str, payload: dict[str, object]) -> str | None:
    source_id_field = _SOURCE_EVENT_ID_FIELDS.get(event_type)
    if source_id_field is None:
        return None
    raw_source_id = payload.get(source_id_field)
    if raw_source_id is None:
        return None
    source_event_id = str(raw_source_id).strip()
    return source_event_id or None


def _require_source_event_id(event_type: str, payload: dict[str, object]) -> str:
    source_event_id = _source_event_id_from_payload(event_type, payload)
    if source_event_id is not None:
        return source_event_id

    source_id_field = _SOURCE_EVENT_ID_FIELDS.get(event_type)
    if source_id_field is None:
        raise CanonicalValidationError(f"Unsupported event_type: {event_type}")
    raise CanonicalValidationError(
        f"Missing stable source event id field: {source_id_field}"
    )


def _parse_canonical_event(
    event_type: str,
    payload: dict[str, object],
) -> Enrollment | AttemptSubmission | PerformanceResult | EngagementSignal:
    try:
        if event_type == "enrollment":
            return Enrollment(**payload)  # type: ignore[arg-type]
        if event_type == "submission":
            return AttemptSubmission(**payload)  # type: ignore[arg-type]
        if event_type == "performance":
            return PerformanceResult(**payload)  # type: ignore[arg-type]
        if event_type == "engagement":
            return EngagementSignal(**payload)  # type: ignore[arg-type]
    except TypeError as exc:
        raise CanonicalValidationError(str(exc)) from exc
    raise CanonicalValidationError(f"Unsupported event_type: {event_type}")


def _enforce_canonical_envelope_consistency(
    *,
    tenant_id: str,
    provider: str,
    provider_instance_id: str,
    event_payload: dict[str, object],
) -> None:
    expected_values = {
        "tenant_id": tenant_id,
        "provider": provider,
        "provider_instance_id": provider_instance_id,
    }
    for field_name in _CANONICAL_ENVELOPE_FIELDS:
        if field_name not in event_payload:
            continue
        actual_value = event_payload[field_name]
        expected_value = expected_values[field_name]
        if actual_value != expected_value:
            raise CanonicalValidationError(
                f"Canonical payload field '{field_name}' must match trusted envelope: "
                f"expected '{expected_value}', received '{actual_value}'"
            )


async def _add_dead_letter(
    *,
    tenant_id: str,
    provider: str,
    provider_instance_id: str,
    source_event_id: str,
    event_type: str,
    error_type: str,
    error_message: str,
    raw_payload: dict[str, object],
) -> DeadLetterEntry:
    now = datetime.now(UTC).isoformat()
    dead_letter = DeadLetterEntry(
        dead_letter_id=str(uuid4()),
        tenant_id=tenant_id,
        provider=provider,
        provider_instance_id=provider_instance_id,
        source_event_id=source_event_id,
        event_type=event_type,
        occurred_at=now,
        received_at=now,
        error_type=error_type,
        error_message=error_message,
        raw_payload=dict(raw_payload),
    )
    return await _dead_letter_repo().add_dead_letter(dead_letter)


async def _process_canonical_payload(
    *,
    tenant_id: str,
    provider: str,
    provider_instance_id: str,
    event_type: str,
    learner_id: str,
    institution_id: str | None,
    event_payload: dict[str, object],
    check_integration_idempotency: bool,
) -> dict[str, object]:
    source_event_id = _require_source_event_id(event_type, event_payload)
    _enforce_canonical_envelope_consistency(
        tenant_id=tenant_id,
        provider=provider,
        provider_instance_id=provider_instance_id,
        event_payload=event_payload,
    )
    idempotency_key = build_idempotency_key(
        tenant_id=tenant_id,
        provider=provider,
        provider_instance_id=provider_instance_id,
        source_event_id=source_event_id,
    )

    idempotency_repo = _idempotency_repo()
    if check_integration_idempotency:
        idem_result = await idempotency_repo.get_processed(idempotency_key)
        if idem_result.already_processed:
            return {
                "status": "duplicate",
                "idempotency_key": idempotency_key,
                "first_processed_at": idem_result.first_processed_at or "",
                "event_id": "",
            }

    canonical_event = _parse_canonical_event(event_type, event_payload)
    learner_event = canonical_to_learner_record_event(
        canonical_event,
        learner_id=learner_id,
        institution_id=institution_id,
        deep_link_base_url="",
    )
    append_result = await _learner_record_repo().append_event_result(learner_event)
    await idempotency_repo.record_processed(idempotency_key)

    return {
        "status": "ingested" if append_result.created else "duplicate",
        "idempotency_key": idempotency_key,
        "event_id": append_result.event.event_id,
        "learner_key": append_result.event.learner_key,
    }


async def _dead_letter_ingestion_failure(
    *,
    request: CanonicalIngestionRequest,
    error_type: str,
    error_message: str,
) -> dict[str, object]:
    source_event_id = _source_event_id_from_payload(
        request.event_type,
        request.event_payload,
    ) or ""
    dead_letter = await _add_dead_letter(
        tenant_id=request.tenant_id,
        provider=request.provider,
        provider_instance_id=request.provider_instance_id,
        source_event_id=source_event_id,
        event_type=request.event_type,
        error_type=error_type,
        error_message=error_message,
        raw_payload=request.event_payload,
    )
    idempotency_key = ""
    if source_event_id:
        idempotency_key = build_idempotency_key(
            tenant_id=request.tenant_id,
            provider=request.provider,
            provider_instance_id=request.provider_instance_id,
            source_event_id=source_event_id,
        )
    return {
        "status": "dead_letter",
        "idempotency_key": idempotency_key,
        "dead_letter_id": dead_letter.dead_letter_id,
        "error": error_message,
    }


def _require_replay_learner_id(learner_id: str | None) -> str:
    if learner_id is None or not learner_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id is required to replay a dead letter",
        )
    return learner_id.strip()


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


# ===== P1: Integration Hub Endpoints =====


class ConnectorRegistrationRequest(BaseModel):
    """Request to register a new connector."""

    tenant_id: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    provider_instance_id: str = Field(..., min_length=1)
    config: dict[str, object] | None = None


class CanonicalIngestionRequest(BaseModel):
    """Request to ingest canonical event into learner record."""

    tenant_id: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    provider_instance_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)  # "enrollment", "submission", "performance", "engagement"
    learner_id: str = Field(..., min_length=1)
    institution_id: str | None = None
    event_payload: dict[str, object]


class ReplayDeadLetterRequest(BaseModel):
    """Request to replay a dead-letter entry."""

    tenant_id: str = Field(..., min_length=1)
    dead_letter_id: str = Field(..., min_length=1)
    event_payload: dict[str, object] | None = None
    learner_id: str | None = None
    institution_id: str | None = None


@app.post("/integration/connectors")
async def register_connector(
    request: ConnectorRegistrationRequest,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """Register a new connector instance."""
    _enforce_tenant_scope(user, request.tenant_id)
    connector_id = f"{request.provider}:{request.provider_instance_id}:{request.tenant_id}"
    state = ConnectorState(
        tenant_id=request.tenant_id,
        provider=request.provider,
        provider_instance_id=request.provider_instance_id,
        connector_id=connector_id,
        status="initializing",
        registered_at=datetime.now(UTC).isoformat(),
        config=request.config,
    )
    saved = await _connector_state_repo().save_connector(state)
    return {
        "connector_id": saved.connector_id,
        "status": saved.status,
        "registered_at": saved.registered_at,
    }


@app.get("/integration/connectors")
async def list_connectors(
    tenant_id: str,
    user: AuthenticatedUserDependency,
) -> list[dict[str, str]]:
    """List all connectors for a tenant."""
    _enforce_tenant_scope(user, tenant_id)
    connectors = await _connector_state_repo().list_connectors(tenant_id)
    return [
        {
            "connector_id": c.connector_id,
            "provider": c.provider,
            "status": c.status,
            "last_sync_at": c.last_sync_at or "",
            "registered_at": c.registered_at,
        }
        for c in connectors
    ]


@app.get("/integration/connectors/{connector_id}")
async def get_connector_state(
    connector_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, object]:
    """Get connector state and health."""
    tenant_id = _tenant_id_from_connector_id(connector_id)
    if tenant_id is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    _enforce_tenant_scope(user, tenant_id)
    state = await _connector_state_repo().get_connector(
        connector_id,
        tenant_id=tenant_id,
    )
    if state is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {
        "connector_id": state.connector_id,
        "tenant_id": state.tenant_id,
        "provider": state.provider,
        "provider_instance_id": state.provider_instance_id,
        "status": state.status,
        "last_sync_at": state.last_sync_at or "",
        "last_sync_cursor": state.last_sync_cursor or "",
        "error_message": state.error_message or "",
        "registered_at": state.registered_at,
        "config": _public_connector_config(state.config),
    }


@app.get("/integration/connectors/{connector_id}/health")
async def get_connector_health(
    connector_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, object]:
    """Get connector health snapshot."""
    tenant_id = _tenant_id_from_connector_id(connector_id)
    if tenant_id is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    _enforce_tenant_scope(user, tenant_id)
    state = await _connector_state_repo().get_connector(
        connector_id,
        tenant_id=tenant_id,
    )
    if state is None:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Build health snapshot
    health_snapshot = ConnectorHealth(
        connector_id=state.connector_id,
        tenant_id=state.tenant_id,
        provider=state.provider,
        status=state.status,
        last_sync_at=state.last_sync_at,
        error_count=1 if state.error_message else 0,
        last_error=state.error_message,
        events_synced_24h=0,  # Would be computed from actual ingestion logs
        avg_sync_duration_seconds=None,
    )

    return {
        "connector_id": health_snapshot.connector_id,
        "provider": health_snapshot.provider,
        "status": health_snapshot.status,
        "last_sync_at": health_snapshot.last_sync_at or "",
        "error_count": health_snapshot.error_count,
        "last_error": health_snapshot.last_error or "",
        "events_synced_24h": health_snapshot.events_synced_24h,
    }


@app.post("/integration/ingest")
async def ingest_canonical_event(
    request: CanonicalIngestionRequest,
    user: AuthenticatedUserDependency,
) -> dict[str, object]:
    """
    Ingest canonical event into learner record with idempotency.

    Validates canonical constraints and converts to LearnerRecordEvent.
    Invalid events (e.g., score > points_possible) go to dead letter queue.
    """
    _enforce_tenant_scope(user, request.tenant_id)
    try:
        return await _process_canonical_payload(
            tenant_id=request.tenant_id,
            provider=request.provider,
            provider_instance_id=request.provider_instance_id,
            event_type=request.event_type,
            learner_id=request.learner_id,
            institution_id=request.institution_id,
            event_payload=request.event_payload,
            check_integration_idempotency=True,
        )
    except CanonicalValidationError as exc:
        return await _dead_letter_ingestion_failure(
            request=request,
            error_type="validation",
            error_message=str(exc),
        )

    except Exception as exc:  # pylint: disable=broad-exception-caught
        return await _dead_letter_ingestion_failure(
            request=request,
            error_type="mapping",
            error_message=str(exc),
        )


@app.get("/integration/dead-letters")
async def list_dead_letters(
    tenant_id: str,
    user: AuthenticatedUserDependency,
    replayed: bool | None = None,
) -> list[dict[str, object]]:
    """List dead-letter entries for a tenant."""
    _enforce_tenant_scope(user, tenant_id)
    entries = await _dead_letter_repo().list_dead_letters(tenant_id, replayed=replayed)
    return [
        {
            "dead_letter_id": e.dead_letter_id,
            "provider": e.provider,
            "event_type": e.event_type,
            "occurred_at": e.occurred_at,
            "error_type": e.error_type,
            "error_message": e.error_message,
            "retry_count": e.retry_count,
            "replayed": e.replayed,
            "replayed_at": e.replayed_at or "",
        }
        for e in entries
    ]


@app.post("/integration/dead-letters/replay")
async def replay_dead_letter(
    request: ReplayDeadLetterRequest,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """Replay a dead-letter entry after manual correction."""
    _enforce_tenant_scope(user, request.tenant_id)
    entry = await _dead_letter_repo().get_dead_letter(
        request.dead_letter_id,
        tenant_id=request.tenant_id,
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Dead letter not found")

    learner_id = _require_replay_learner_id(request.learner_id)
    payload = request.event_payload if request.event_payload is not None else entry.raw_payload

    try:
        process_result = await _process_canonical_payload(
            tenant_id=entry.tenant_id,
            provider=entry.provider,
            provider_instance_id=entry.provider_instance_id,
            event_type=entry.event_type,
            learner_id=learner_id,
            institution_id=request.institution_id,
            event_payload=payload,
            check_integration_idempotency=False,
        )
    except (CanonicalValidationError, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    replayed_at = datetime.now(UTC).isoformat()
    updated = await _dead_letter_repo().mark_replayed(
        request.dead_letter_id,
        replayed_at,
        tenant_id=request.tenant_id,
    )

    if updated is None:
        raise HTTPException(status_code=404, detail="Dead letter not found")

    return {
        "dead_letter_id": updated.dead_letter_id,
        "status": "replayed",
        "replayed_at": replayed_at,
        "retry_count": str(updated.retry_count),
        "event_id": str(process_result["event_id"]),
    }


# ===== P1: Standards Placeholder Endpoints =====


@app.post("/integration/oneroster/import")
async def oneroster_import(
    tenant_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """
    OneRoster CSV import endpoint (P1 placeholder).

    Full implementation in P2 will parse CSV/API roster data and map to canonical contracts.
    """
    _enforce_tenant_scope(user, tenant_id)
    return {
        "status": "placeholder",
        "message": "OneRoster import not yet implemented; P1 provides structure only",
        "tenant_id": tenant_id,
    }


@app.post("/integration/lti/launch")
async def lti_launch(
    tenant_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """
    LTI 1.3 launch endpoint (P1 placeholder).

    Full implementation in P2 will handle OIDC launch, AGS, NRPS, and Deep Linking.
    """
    _enforce_tenant_scope(user, tenant_id)
    return {
        "status": "placeholder",
        "message": "LTI 1.3 launch not yet implemented; P1 provides structure only",
        "tenant_id": tenant_id,
    }


@app.post("/integration/caliper/events")
async def caliper_events(
    tenant_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """
    Caliper 1.2 event ingestion endpoint (P1 placeholder).

    Full implementation in P2 will parse Caliper envelopes and map to canonical contracts.
    """
    _enforce_tenant_scope(user, tenant_id)
    return {
        "status": "placeholder",
        "message": "Caliper event ingestion not yet implemented; P1 provides structure only",
        "tenant_id": tenant_id,
    }


@app.post("/integration/xapi/statements")
async def xapi_statements(
    tenant_id: str,
    user: AuthenticatedUserDependency,
) -> dict[str, str]:
    """
    xAPI statement ingestion endpoint (P1 placeholder).

    Full implementation in P2 will parse xAPI statements and map to canonical contracts.
    """
    _enforce_tenant_scope(user, tenant_id)
    return {
        "status": "placeholder",
        "message": "xAPI statement ingestion not yet implemented; P1 provides structure only",
        "tenant_id": tenant_id,
    }
