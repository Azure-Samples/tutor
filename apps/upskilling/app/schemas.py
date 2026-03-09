"""Pydantic models for the upskilling service."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_301_MOVED_PERMANENTLY,
    HTTP_302_FOUND,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_418_IM_A_TEAPOT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)


class BodyMessage(BaseModel):
    """Generic response envelope."""

    success: bool
    type: str | None
    title: str | None
    detail: Any | None


@dataclass
class SuccessMessage:
    """Payload returned on successful operations."""

    title: str | None
    message: str | None
    content: Any | None


@dataclass
class ErrorMessage:
    """Payload returned on failed operations."""

    success: bool
    type: str | None
    title: str | None
    detail: Any | None


class PerformanceSnapshot(BaseModel):
    """Historical performance record for a class/topic."""

    period: str = Field(..., description="Time slice analysed, e.g. 'weekly' or 'semester'.")
    topic: str = Field(..., description="Subject area the performance applies to.")
    proficiency: float = Field(..., ge=0.0, le=1.0, description="Normalised performance score (0-1).")
    highlights: list[str] | None = Field(default=None, description="Strengths observed during the period.")
    gaps: list[str] | None = Field(default=None, description="Areas that need improvement.")


class PlanParagraph(BaseModel):
    """Single paragraph of the proposed class plan."""

    title: str = Field(..., description="Optional heading for the paragraph.")
    content: str = Field(..., description="Paragraph text provided by the professor.")


class PlanRequest(BaseModel):
    """Request payload for evaluating a class plan."""

    timeframe: str = Field(..., description="Planning horizon: week, month, semester, or year.")
    topic: str = Field(..., description="Subject for which the plan is being drafted.")
    class_id: str = Field(..., description="Identifier of the class being planned.")
    paragraphs: list[PlanParagraph] = Field(..., min_items=1)
    performance_history: list[PerformanceSnapshot] = Field(default_factory=list)


class AgentFeedback(BaseModel):
    """Evaluation returned by a single agent for a paragraph."""

    agent: str
    verdict: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class ParagraphEvaluation(BaseModel):
    """Aggregated feedback for a paragraph."""

    paragraph_index: int
    title: str
    feedback: list[AgentFeedback]


class PlanEvaluationResponse(BaseModel):
    """Response payload returned by the evaluation endpoint."""

    timeframe: str
    topic: str
    class_id: str
    evaluations: list[ParagraphEvaluation]


class CreatePlanRequest(BaseModel):
    """Request payload for creating a new teaching plan."""

    title: str = Field(..., description="Plan title, e.g. 'Plano de Ensino — Física 3A'.")
    timeframe: str = Field(..., description="Planning horizon: week, month, semester, or year.")
    topic: str = Field(..., description="Subject for which the plan is being drafted.")
    class_id: str = Field(..., description="Identifier of the class being planned.")
    paragraphs: list[PlanParagraph] = Field(..., min_length=1)
    performance_history: list[PerformanceSnapshot] = Field(default_factory=list)


class UpdatePlanRequest(BaseModel):
    """Request payload for updating an existing teaching plan."""

    title: str | None = None
    timeframe: str | None = None
    topic: str | None = None
    class_id: str | None = None
    paragraphs: list[PlanParagraph] | None = None
    performance_history: list[PerformanceSnapshot] | None = None


RESPONSES: dict[int, dict[str, Any]] = {
    HTTP_200_OK: {"model": BodyMessage},
    HTTP_201_CREATED: {"model": BodyMessage},
    HTTP_202_ACCEPTED: {"model": BodyMessage},
    HTTP_302_FOUND: {"model": BodyMessage},
    HTTP_301_MOVED_PERMANENTLY: {"model": BodyMessage},
    HTTP_307_TEMPORARY_REDIRECT: {"model": BodyMessage},
    HTTP_400_BAD_REQUEST: {"model": BodyMessage},
    HTTP_401_UNAUTHORIZED: {"model": BodyMessage},
    HTTP_403_FORBIDDEN: {"model": BodyMessage},
    HTTP_418_IM_A_TEAPOT: {"model": BodyMessage},
    HTTP_422_UNPROCESSABLE_ENTITY: {"model": BodyMessage},
}
