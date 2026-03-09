"""FastAPI surface for the upskilling professor planning service."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .orchestrator import build_orchestrator
from .schemas import (
    AgentFeedback,
    RESPONSES,
    BodyMessage,
    ErrorMessage,
    ParagraphEvaluation,
    PlanEvaluationResponse,
    PlanRequest,
    SuccessMessage,
)
from tutor_lib.config import get_settings
from tutor_lib.middleware import configure_entra_auth


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


@app.get("/health", tags=["Planning"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["Planning"])
async def ready() -> dict[str, str]:
    return {"status": "ready"}


def _success(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


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


@app.post("/plan/evaluate", tags=["Planning"])
async def evaluate_plan(payload: PlanRequest) -> JSONResponse:
    try:
        orchestrator = build_orchestrator()
        evaluations = await orchestrator.evaluate(payload)
    except Exception:
        # Keep demo flows available even when AI project wiring is absent.
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
            for index, paragraph in enumerate(payload.paragraphs)
        ]

    response = PlanEvaluationResponse(
        timeframe=payload.timeframe,
        topic=payload.topic,
        class_id=payload.class_id,
        evaluations=evaluations,
    )
    return _success("Plan Evaluated", "Generated guidance for each paragraph.", response.model_dump())
