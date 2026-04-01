"""Pydantic schemas and response envelopes for the insights service."""

from __future__ import annotations

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


class BriefingRequest(BaseModel):
    """Request payload for generating a school briefing report."""

    school_id: str = Field(..., min_length=1)
    week_of: str | None = None
    on_demand: bool = False


class FeedbackRequest(BaseModel):
    """Request payload for a supervisor briefing feedback entry."""

    report_id: str = Field(..., min_length=1)
    school_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comments: str | None = None


class FeedbackEntry(BaseModel):
    """Feedback payload returned for report feedback queries."""

    feedback_id: str
    report_id: str
    school_id: str
    supervisor_id: str
    rating: int = Field(..., ge=1, le=5)
    comments: str | None = None
    submitted_at: str


class PilotMetrics(BaseModel):
    """Aggregated pilot telemetry used for go/no-go reporting."""

    total_reports: int = Field(..., ge=0)
    total_feedback: int = Field(..., ge=0)
    reports_with_feedback: int = Field(..., ge=0)
    average_rating: float | None = Field(default=None, ge=1, le=5)
    feedback_rate: float = Field(..., ge=0, le=1)
    school_count: int = Field(..., ge=0)


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
