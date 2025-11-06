"""Pydantic models for the upskilling service."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    type: Optional[str]
    title: Optional[str]
    detail: Optional[Any]


@dataclass
class SuccessMessage:
    """Payload returned on successful operations."""

    title: Optional[str]
    message: Optional[str]
    content: Optional[Any]


@dataclass
class ErrorMessage:
    """Payload returned on failed operations."""

    success: bool
    type: Optional[str]
    title: Optional[str]
    detail: Optional[Any]


class PerformanceSnapshot(BaseModel):
    """Historical performance record for a class/topic."""

    period: str = Field(..., description="Time slice analysed, e.g. 'weekly' or 'semester'.")
    topic: str = Field(..., description="Subject area the performance applies to.")
    proficiency: float = Field(..., ge=0.0, le=1.0, description="Normalised performance score (0-1).")
    highlights: Optional[List[str]] = Field(default=None, description="Strengths observed during the period.")
    gaps: Optional[List[str]] = Field(default=None, description="Areas that need improvement.")


class PlanParagraph(BaseModel):
    """Single paragraph of the proposed class plan."""

    title: str = Field(..., description="Optional heading for the paragraph.")
    content: str = Field(..., description="Paragraph text provided by the professor.")


class PlanRequest(BaseModel):
    """Request payload for evaluating a class plan."""

    timeframe: str = Field(..., description="Planning horizon: week, month, semester, or year.")
    topic: str = Field(..., description="Subject for which the plan is being drafted.")
    class_id: str = Field(..., description="Identifier of the class being planned.")
    paragraphs: List[PlanParagraph] = Field(..., min_items=1)
    performance_history: List[PerformanceSnapshot] = Field(default_factory=list)


class AgentFeedback(BaseModel):
    """Evaluation returned by a single agent for a paragraph."""

    agent: str
    verdict: str
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class ParagraphEvaluation(BaseModel):
    """Aggregated feedback for a paragraph."""

    paragraph_index: int
    title: str
    feedback: List[AgentFeedback]


class PlanEvaluationResponse(BaseModel):
    """Response payload returned by the evaluation endpoint."""

    timeframe: str
    topic: str
    class_id: str
    evaluations: List[ParagraphEvaluation]


RESPONSES: Dict[int, Dict[str, Any]] = {
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
