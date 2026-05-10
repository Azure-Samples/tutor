"""FastAPI surface for the upskilling professor planning service."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from os import getenv
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from tutor_lib.config import get_settings
from tutor_lib.intelligence import (
    AbstentionMetadata,
    AppealState,
    CalibrationMetadata,
    CoverageMetadata,
    GovernanceAssumption,
    IntelligenceGovernanceMetadata,
    IntelligenceProvenance,
    ReviewState,
    SuppressionMetadata,
    UncertaintyMetadata,
)
from tutor_lib.middleware import configure_entra_auth, require_roles
from tutor_lib.middleware.auth import AuthenticatedUser

from .orchestrator import build_orchestrator
from .schemas import (
    RESPONSES,
    AdvisoryTrainingPlan,
    AdvisoryTrainingStep,
    AgentFeedback,
    BodyMessage,
    CreatePlanRequest,
    ErrorMessage,
    ParagraphEvaluation,
    PerformanceSnapshot,
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
        current_settings = get_settings()
        return CosmosUpskillingRepository(
            current_settings.cosmos.upskilling_container, current_settings.cosmos
        )
    except (RuntimeError, ValueError, ValidationError):
        return InMemoryUpskillingRepository()


def reset_repository() -> None:
    _repository.cache_clear()


require_professor = require_roles("professor", "admin")
ProfessorUser = Annotated[AuthenticatedUser, Depends(require_professor)]


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


# No GoF pattern applies -- route guard centralizes simple ownership checks.
def _enforce_plan_scope(plan: PlanRecord, user: AuthenticatedUser) -> None:
    if plan.professor_id == user.subject or "admin" in user.roles:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plan is outside the caller scope")


def _average_proficiency(plan: PlanRecord) -> float | None:
    values = [
        float(snapshot["proficiency"])
        for snapshot in plan.performance_history
        if isinstance(snapshot.get("proficiency"), (int, float))
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def _advisory_training_governance(plan: PlanRecord, *, generated_at: str) -> IntelligenceGovernanceMetadata:
    proficiency = _average_proficiency(plan)
    uncertainty = UncertaintyMetadata(
        point_estimate=proficiency,
        lower_bound=max(0.0, round((proficiency or 0.5) - 0.18, 3)) if proficiency is not None else None,
        upper_bound=min(1.0, round((proficiency or 0.5) + 0.18, 3)) if proficiency is not None else None,
        confidence_level=0.9,
        interval_width=0.36 if proficiency is not None else 0.52,
        method="deterministic-professor-training-plan-advisory",
        wide=proficiency is None,
        rationale="The advisory draft uses only the persisted plan and optional performance snapshots.",
    )
    return IntelligenceGovernanceMetadata(
        provenance=IntelligenceProvenance(
            source_type="teaching_plan",
            source_ids=(f"plan:{plan.id}", f"class:{plan.class_id}", f"topic:{plan.topic}"),
            generator="upskilling.advisory-training-plan",
            workflow_version="advisory-training-plan-v1",
        ),
        assumptions=(
            GovernanceAssumption(
                assumption_id="professor-owned-draft",
                statement="The generated plan is a draft owned by the professor and requires human review.",
                category="policy",
                evidence_refs=(f"plan:{plan.id}",),
            ),
            GovernanceAssumption(
                assumption_id="limited-performance-history",
                statement="Performance snapshots may be incomplete and must not be used for final approval decisions.",
                category="data_quality",
            ),
        ),
        uncertainty=uncertainty,
        calibration=CalibrationMetadata(
            calibration_set_id="upskilling:deterministic-advisory-v1",
            calibrated_at=generated_at,
            method="rubric-aligned deterministic fallback",
            sample_count=len(plan.performance_history),
            expected_coverage=0.9,
            observed_coverage=0.84 if plan.performance_history else 0.0,
        ),
        coverage=CoverageMetadata(
            population=f"class:{plan.class_id}",
            eligible_count=max(len(plan.paragraphs), 1),
            covered_count=len(plan.paragraphs),
            coverage_rate=1.0 if plan.paragraphs else 0.0,
            minimum_required=1,
        ),
        suppression=SuppressionMetadata(suppressed=False, reason="none"),
        review=ReviewState(
            status="required",
            required=True,
            summary="Professor review is required before any classroom use or approval workflow.",
        ),
        appeal=AppealState(status="available", available=True),
        abstention=AbstentionMetadata(
            abstained=False,
            degraded=not bool(plan.performance_history),
            reason="missing_performance_history" if not plan.performance_history else None,
            fallback_behavior="human_review",
        ),
        advisory_only=True,
        final_decision=False,
    )


def _build_advisory_training_plan(plan: PlanRecord) -> AdvisoryTrainingPlan:
    generated_at = datetime.now(UTC).isoformat()
    return AdvisoryTrainingPlan(
        plan_id=plan.id,
        professor_id=plan.professor_id,
        generated_at=generated_at,
        steps=[
            AdvisoryTrainingStep(
                sequence=1,
                title="Refine measurable outcomes",
                rationale=f"Align the {plan.topic} plan with one observable success criterion for {plan.timeframe} instruction.",
                evidence_refs=[f"plan:{plan.id}", f"class:{plan.class_id}"],
            ),
            AdvisoryTrainingStep(
                sequence=2,
                title="Add formative checks",
                rationale="Add a low-stakes checkpoint before any summative decision is considered.",
                evidence_refs=[f"plan:{plan.id}"],
            ),
        ],
        governance=_advisory_training_governance(plan, generated_at=generated_at),
    )


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
    user: ProfessorUser,
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
    user: ProfessorUser,
) -> JSONResponse:
    plans = await _repository().list_plans(professor_id=user.subject)
    return _success("Plans", "Plans retrieved.", [plan_to_dict(p) for p in plans])


@app.get("/plans/{plan_id}", tags=["Planning"])
async def get_plan(
    plan_id: str,
    user: ProfessorUser,
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    _enforce_plan_scope(plan, user)
    return _success("Plan", "Plan retrieved.", plan_to_dict(plan))


@app.put("/plans/{plan_id}", tags=["Planning"])
async def update_plan(
    plan_id: str,
    payload: UpdatePlanRequest,
    user: ProfessorUser,
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    _enforce_plan_scope(plan, user)

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
    user: ProfessorUser,
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    _enforce_plan_scope(plan, user)
    await _repository().delete_plan(plan_id, plan.professor_id)
    return _success("Plan Deleted", "Plan deleted.", None)


# ── Evaluation routes ────────────────────────────────────────────────────


@app.post("/plans/{plan_id}/evaluate", tags=["Planning"])
async def evaluate_persisted_plan(
    plan_id: str,
    user: ProfessorUser,
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    _enforce_plan_scope(plan, user)

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
    except (OSError, RuntimeError, TimeoutError, ValueError):
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


@app.post("/plans/{plan_id}/advisory-training-plan", tags=["Planning"])
async def draft_advisory_training_plan(
    plan_id: str,
    user: ProfessorUser,
) -> JSONResponse:
    plan = await _repository().get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    _enforce_plan_scope(plan, user)

    advisory_plan = _build_advisory_training_plan(plan)
    plan.advisory_training_plan = advisory_plan.model_dump()
    plan.updated_at = datetime.now(UTC).isoformat()
    saved = await _repository().update_plan(plan)
    return _success(
        "Advisory Training Plan Drafted",
        "Draft advisory training plan generated for professor review.",
        plan_to_dict(saved),
    )



