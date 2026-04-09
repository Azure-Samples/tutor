"""Pydantic schemas and response envelopes for the insights service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

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


class DeepLink(BaseModel):
    """Frontend navigation target for a projected workspace item."""

    label: str
    href: str


class FreshnessMetadata(BaseModel):
    """Read-model freshness and source timing metadata."""

    generated_at: str
    source_updated_at: str | None = None
    status: Literal["fresh", "derived", "stale", "degraded"]
    note: str


class ProvenanceMetadata(BaseModel):
    """Source and workflow lineage for high-impact projections."""

    source_type: str
    source_ids: list[str] = Field(default_factory=list)
    generator: str
    workflow_version: str
    model: str | None = None


class ReviewMetadata(BaseModel):
    """Human review state surfaced alongside advisory outputs."""

    status: Literal["required", "recommended", "not_required", "completed"]
    summary: str


class TrustMetadata(BaseModel):
    """Trust and governance metadata carried by snapshots and record entries."""

    provenance: ProvenanceMetadata
    evaluation_state: Literal["evaluated", "pending", "not_required"]
    human_review: ReviewMetadata
    degraded: bool = False
    advisory_only: bool = True
    note: str


class SnapshotItem(BaseModel):
    """Projected workspace card or row for a role-aware snapshot."""

    item_id: str
    tone: Literal["deterministic", "advisory", "attention"]
    title: str
    summary: str
    metric: str | None = None
    deep_link: DeepLink


class WorkspaceSnapshotPayload(BaseModel):
    """Typed contract for role-specific workspace projections."""

    role: str
    context_id: str
    context_label: str
    summary: str
    freshness: FreshnessMetadata
    trust: TrustMetadata
    deterministic_highlights: list[SnapshotItem] = Field(default_factory=list)
    advisory_items: list[SnapshotItem] = Field(default_factory=list)
    attention_items: list[SnapshotItem] = Field(default_factory=list)
    deep_links: list[DeepLink] = Field(default_factory=list)


class TimelineEvidence(BaseModel):
    """Evidence handle attached to a learner-record entry."""

    evidence_id: str
    label: str
    kind: str
    deep_link: DeepLink | None = None


class LearnerRecordEntry(BaseModel):
    """Append-oriented learner-record entry projected for frontend use."""

    record_id: str
    occurred_at: str
    event_type: str
    source_service: str
    title: str
    summary: str
    status: Literal["confirmed", "advisory", "degraded", "needs_review"]
    actor_role: str
    evidence: list[TimelineEvidence] = Field(default_factory=list)
    trust: TrustMetadata
    deep_link: DeepLink


class CursorPage(BaseModel):
    """Simple cursor contract for learner-record pagination."""

    limit: int = Field(..., ge=1, le=25)
    cursor: str | None = None
    next_cursor: str | None = None
    has_more: bool


class LearnerRecordTimelinePayload(BaseModel):
    """Typed timeline response for learner-record history."""

    learner_id: str
    context_id: str
    context_label: str
    summary: str
    freshness: FreshnessMetadata
    page: CursorPage
    entries: list[LearnerRecordEntry] = Field(default_factory=list)
    deep_links: list[DeepLink] = Field(default_factory=list)


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
