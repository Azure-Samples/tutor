"""FastAPI surface for the upskilling professor planning service."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from os import getenv
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tutor_lib.config import get_settings
from tutor_lib.middleware import configure_entra_auth, require_roles
from tutor_lib.middleware.auth import AuthenticatedUser

from .orchestrator import build_orchestrator
from .schemas import (
    RESPONSES,
    AgentFeedback,
    BodyMessage,
    CreatePlanRequest,
    ErrorMessage,
    ParagraphEvaluation,
    PerformanceSnapshot,
    PlanEvaluationResponse,
    PlanParagraph,
    PlanRequest,
    SuccessMessage,
    UpdatePlanRequest,
)
from .store import (
    CosmosUpskillingRepository,
    InMemoryUpskillingRepository,
    PlanRecord,
    UpskillingRepository,
    plan_to_dict,
)

settings = get_settings()

app = FastAPI(
    title="Upskilling",
    version="1.0.0",
    description="Guides professors through data-informed class planning.",
    openapi_tags=[
        {"name": "Planning", "description": "Evaluate class plans with iterative coaching."},
    ],
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore[arg-type]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=r"https://.*\.azurestaticapps\.net",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
configure_entra_auth(app)


@lru_cache(maxsize=1)
def _repository() -> UpskillingRepository:
    if getenv("UPSKILLING_REPOSITORY", "cosmos").lower() == "memory":
        return InMemoryUpskillingRepository()
    try:
        settings = get_settings()
        return CosmosUpskillingRepository(
            settings.cosmos.upskilling_container, settings.cosmos
        )
    except Exception:
        return InMemoryUpskillingRepository()


require_professor = require_roles("professor", "admin")


@app.get("/health", tags=["Planning"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["Planning"])
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


# ── CRUD routes ──────────────────────────────────────────────────────────


@app.post("/plans", tags=["Planning"])
async def create_plan(
    payload: CreatePlanRequest,
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    now = datetime.now(UTC).isoformat()
    record = PlanRecord(
        id=str(uuid4()),
        professor_id=user.subject,
        title=payload.title,
        timeframe=payload.timeframe,
        topic=payload.topic,
        class_id=payload.class_id,
        status="draft",
        paragraphs=[{"title": p.title, "content": p.content} for p in payload.paragraphs],
        performance_history=[snap.model_dump() for snap in payload.performance_history],
        created_at=now,
        updated_at=now,
    )
    saved = await _repository().create_plan(record)
    return _created("Plan Created", "Teaching plan persisted.", plan_to_dict(saved))


@app.get("/plans", tags=["Planning"])
async def list_plans(
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    plans = await _repository().list_plans(professor_id=user.subject)
    return _success("Plans", "Plans retrieved.", [plan_to_dict(p) for p in plans])


@app.get("/plans/{plan_id}", tags=["Planning"])
async def get_plan(
    plan_id: str,
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return _success("Plan", "Plan retrieved.", plan_to_dict(plan))


@app.put("/plans/{plan_id}", tags=["Planning"])
async def update_plan(
    plan_id: str,
    payload: UpdatePlanRequest,
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    if payload.title is not None:
        plan.title = payload.title
    if payload.timeframe is not None:
        plan.timeframe = payload.timeframe
    if payload.topic is not None:
        plan.topic = payload.topic
    if payload.class_id is not None:
        plan.class_id = payload.class_id
    if payload.paragraphs is not None:
        plan.paragraphs = [{"title": p.title, "content": p.content} for p in payload.paragraphs]
    if payload.performance_history is not None:
        plan.performance_history = [snap.model_dump() for snap in payload.performance_history]

    plan.updated_at = datetime.now(UTC).isoformat()

    if plan.status == "evaluated":
        plan.status = "revised"

    saved = await _repository().update_plan(plan)
    return _success("Plan Updated", "Teaching plan updated.", plan_to_dict(saved))


@app.delete("/plans/{plan_id}", tags=["Planning"])
async def delete_plan(
    plan_id: str,
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    await _repository().delete_plan(plan_id, plan.professor_id)
    return _success("Plan Deleted", "Plan deleted.", None)


# ── Evaluation routes ────────────────────────────────────────────────────


@app.post("/plans/{plan_id}/evaluate", tags=["Planning"])
async def evaluate_persisted_plan(
    plan_id: str,
    user: AuthenticatedUser = Depends(require_professor),
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    request = PlanRequest(
        timeframe=plan.timeframe,
        topic=plan.topic,
        class_id=plan.class_id,
        paragraphs=[PlanParagraph(**p) for p in plan.paragraphs],
        performance_history=[PerformanceSnapshot(**s) for s in plan.performance_history],
    )

    try:
        orchestrator = build_orchestrator()
        evaluations = await orchestrator.evaluate(request)
    except Exception:
        evaluations = [
            ParagraphEvaluation(
                paragraph_index=index,
                title=paragraph.title,
                feedback=[
                    AgentFeedback(
                        agent="coaching-fallback",
                        verdict="Needs refinement",
                        strengths=["Clear topic framing"],
                        improvements=["Add one measurable learning outcome and one formative check"],
                    )
                ],
            )
            for index, paragraph in enumerate(request.paragraphs)
        ]

    plan.evaluations = [e.model_dump() for e in evaluations]
    plan.status = "evaluated"
    plan.updated_at = datetime.now(UTC).isoformat()
    saved = await _repository().update_plan(plan)
    return _success("Plan Evaluated", "Generated guidance for each paragraph.", plan_to_dict(saved))



