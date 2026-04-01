"""FastAPI surface for the supervisor insights service."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from functools import lru_cache
from os import getenv
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from tutor_lib.config import create_app, get_settings
from tutor_lib.middleware import require_roles
from tutor_lib.middleware.auth import AuthenticatedUser

from app.indicators import (
    AttendanceStrategy,
    DeterministicFabricReadAdapter,
    FabricReadAdapter,
    IndicatorStrategy,
    StandardizedAssessmentStrategy,
    TaskCompletionStrategy,
)
from app.orchestrator import build_briefing
from app.schemas import (
    BodyMessage,
    BriefingRequest,
    ErrorMessage,
    FeedbackRequest,
    SuccessMessage,
)
from app.store import (
    CosmosInsightsRepository,
    FeedbackRecord,
    InMemoryInsightsRepository,
    InsightsRepository,
    ReportRecord,
    feedback_to_dict,
    pilot_metrics_to_dict,
    report_to_dict,
)

app = create_app(
    title="Insights",
    version="0.1.0",
    description="Supervisor insight reports with school-scoped governance.",
)


@lru_cache(maxsize=1)
def _repository() -> InsightsRepository:
    if getenv("INSIGHTS_REPOSITORY", "cosmos").lower() == "memory":
        return InMemoryInsightsRepository()
    try:
        settings = get_settings()
        if not _cosmos_endpoint_configured(settings.cosmos.endpoint):
            return InMemoryInsightsRepository()
        return CosmosInsightsRepository(settings.cosmos)
    except ValidationError:
        return InMemoryInsightsRepository()


def _cosmos_endpoint_configured(endpoint: str) -> bool:
    parsed = urlparse(endpoint.strip())
    return bool(parsed.scheme and parsed.netloc)


@lru_cache(maxsize=1)
def _fabric_adapter() -> FabricReadAdapter:
    return DeterministicFabricReadAdapter()


def reset_repository() -> None:
    _repository.cache_clear()
    _fabric_adapter.cache_clear()
    _indicator_strategies.cache_clear()


@lru_cache(maxsize=1)
def _indicator_strategies() -> tuple[IndicatorStrategy, ...]:
    return (
        StandardizedAssessmentStrategy(fabric_adapter=_fabric_adapter()),
        AttendanceStrategy(fabric_adapter=_fabric_adapter()),
        TaskCompletionStrategy(fabric_adapter=_fabric_adapter()),
    )


require_supervisor = require_roles("supervisor", "admin")
require_supervisor_dep = Depends(require_supervisor)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


def _success(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


def _created(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(body))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    body = BodyMessage(
        success=False,
        type="validation",
        title="Invalid request payload",
        detail={"invalid-params": list(exc.errors())},
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder(body))


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    body = ErrorMessage(
        success=False,
        type="internal",
        title="Unexpected error",
        detail={"message": str(exc)},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(body))


def _parse_school_ids(raw_school_ids: Any) -> set[str]:
    if raw_school_ids is None:
        return set()
    if isinstance(raw_school_ids, str):
        return {item.strip() for item in raw_school_ids.split(",") if item.strip()}
    if isinstance(raw_school_ids, list):
        return {str(item).strip() for item in raw_school_ids if str(item).strip()}
    return set()


def _pilot_enabled() -> bool:
    return getenv("INSIGHTS_PILOT_ENABLED", "false").lower() in {"1", "true", "yes", "on"}


def _pilot_school_ids() -> set[str]:
    return _parse_school_ids(getenv("INSIGHTS_PILOT_SCHOOL_IDS", ""))


def _pilot_supervisor_ids() -> set[str]:
    return _parse_school_ids(getenv("INSIGHTS_PILOT_SUPERVISOR_IDS", ""))


def _resolve_school_scope(
    user: AuthenticatedUser,
    request: Request,
    requested_school_id: str | None = None,
) -> set[str] | None:
    if "admin" in user.roles:
        return None

    claim_school_ids = _parse_school_ids(user.claims.get("school_ids") or user.claims.get("schoolIds"))
    if claim_school_ids:
        return claim_school_ids

    if user.tenant_id == "local-dev":
        header_school_ids = _parse_school_ids(request.headers.get("X-School-Ids", ""))
        if header_school_ids:
            return header_school_ids
        if requested_school_id:
            return {requested_school_id}

    return set()


def _resolve_allowed_school_ids(
    user: AuthenticatedUser,
    request: Request,
    school_id: str | None,
) -> set[str] | None:
    scope = _resolve_school_scope(user, request, requested_school_id=school_id)

    if school_id is not None:
        if scope is not None and school_id not in scope:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requested school is outside the caller scope",
            )
        return {school_id}

    if scope is None:
        return None
    if scope:
        return scope

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No school scope claim available for report listing",
    )


def _apply_pilot_school_scope(
    allowed_school_ids: set[str] | None,
    *,
    requested_school_id: str | None = None,
) -> set[str] | None:
    if not _pilot_enabled():
        return allowed_school_ids

    pilot_school_ids = _pilot_school_ids()
    if not pilot_school_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pilot school scope is not configured",
        )

    if requested_school_id and requested_school_id not in pilot_school_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested school is outside the active pilot scope",
        )

    if allowed_school_ids is None:
        return set(pilot_school_ids)

    scoped_school_ids = allowed_school_ids.intersection(pilot_school_ids)
    if not scoped_school_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller school scope does not overlap with pilot scope",
        )
    return scoped_school_ids


def _enforce_school_scope(
    user: AuthenticatedUser,
    request: Request,
    school_id: str,
) -> None:
    scope = _resolve_school_scope(user, request, requested_school_id=school_id)
    if scope is None:
        return
    if school_id not in scope:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested school is outside the caller scope",
        )


def _enforce_pilot_supervisor_scope(user: AuthenticatedUser) -> None:
    if not _pilot_enabled():
        return

    supervisors = _pilot_supervisor_ids()
    if not supervisors or user.subject not in supervisors:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller is outside the active pilot supervisor scope",
        )


def _enforce_pilot_school_scope(school_id: str) -> None:
    if not _pilot_enabled():
        return

    schools = _pilot_school_ids()
    if not schools or school_id not in schools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested school is outside the active pilot scope",
        )


@app.post("/briefing")
async def create_briefing(
    payload: BriefingRequest,
    request: Request,
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)
    _enforce_pilot_school_scope(payload.school_id)
    _enforce_school_scope(user, request, payload.school_id)

    briefing = await build_briefing(
        payload.school_id,
        list(_indicator_strategies()),
        week_of=payload.week_of,
    )

    report = ReportRecord(
        report_id=str(uuid4()),
        school_id=payload.school_id,
        supervisor_id=user.subject,
        week_of=payload.week_of,
        generated_at=datetime.now(UTC).isoformat(),
        source="on_demand" if payload.on_demand else "weekly",
        indicators=[asdict(snapshot) for snapshot in briefing.indicators],
        trends=briefing.trends,
        alerts=briefing.alerts,
        focus_points=briefing.focus_points,
        improvements=briefing.improvements,
    )

    saved = await _repository().create_report(report)
    return _created(
        "Briefing Created",
        "Supervisor briefing report generated and stored.",
        report_to_dict(saved),
    )


@app.get("/reports")
async def list_reports(
    request: Request,
    school_id: str | None = Query(default=None),
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)

    allowed_school_ids = _resolve_allowed_school_ids(user, request, school_id)
    allowed_school_ids = _apply_pilot_school_scope(allowed_school_ids, requested_school_id=school_id)

    reports = await _repository().list_reports(allowed_school_ids)
    return _success(
        "Reports Retrieved",
        "Insight reports fetched.",
        [report_to_dict(report) for report in reports],
    )


@app.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    request: Request,
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)

    report = await _repository().get_report(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    _enforce_pilot_school_scope(report.school_id)
    _enforce_school_scope(user, request, report.school_id)
    return _success("Report Retrieved", "Insight report fetched.", report_to_dict(report))


@app.post("/feedback")
async def create_feedback(
    payload: FeedbackRequest,
    request: Request,
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)

    report = await _repository().get_report(payload.report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if payload.school_id != report.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback school_id must match report school_id")

    _enforce_pilot_school_scope(payload.school_id)
    _enforce_school_scope(user, request, payload.school_id)

    feedback = FeedbackRecord(
        feedback_id=str(uuid4()),
        report_id=payload.report_id,
        school_id=payload.school_id,
        supervisor_id=user.subject,
        rating=payload.rating,
        comments=payload.comments,
        submitted_at=datetime.now(UTC).isoformat(),
    )
    saved = await _repository().create_feedback(feedback)
    return _created("Feedback Saved", "Supervisor feedback stored.", feedback_to_dict(saved))


@app.get("/reports/{report_id}/feedback")
async def list_report_feedback(
    report_id: str,
    request: Request,
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)

    report = await _repository().get_report(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    _enforce_pilot_school_scope(report.school_id)
    _enforce_school_scope(user, request, report.school_id)

    feedback_rows = await _repository().list_feedback(report_id)
    return _success(
        "Feedback Retrieved",
        "Report feedback fetched.",
        [feedback_to_dict(row) for row in feedback_rows],
    )


@app.get("/pilot/metrics")
async def get_pilot_metrics(
    request: Request,
    school_id: str | None = Query(default=None),
    user: AuthenticatedUser = require_supervisor_dep,
) -> JSONResponse:
    _enforce_pilot_supervisor_scope(user)

    allowed_school_ids = _resolve_allowed_school_ids(user, request, school_id)
    allowed_school_ids = _apply_pilot_school_scope(allowed_school_ids, requested_school_id=school_id)

    metrics = await _repository().get_pilot_metrics(allowed_school_ids)
    return _success("Pilot Metrics Retrieved", "Pilot metrics fetched.", pilot_metrics_to_dict(metrics))
