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
    HTTP_422_UNPROCESSABLE_CONTENT,
)
from tutor_lib.intelligence import (
    AbstentionMetadata,
    CalibrationMetadata,
    CoverageMetadata,
    DriftMetadata,
    IntelligenceGovernanceMetadata,
    SuppressionMetadata,
    UncertaintyMetadata,
)
from tutor_lib.lifelong_network import (
    AlumniAffiliation,
    CommunityEvent,
    CredentialAward,
    CredentialDefinition,
    DataUseAgreement,
    DeIdentificationRun,
    MentorRelationship,
    PortfolioArtifact,
    PublicationApproval,
    ReEntryPathway,
    ResearchDataset,
    VerificationRequest,
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
    page: CursorPage
    entries: list[LearnerRecordEntry] = Field(default_factory=list)


# ===== P1: Learner Progress And Strategy Read Models =====


class CourseProgressItem(BaseModel):
    """Course progress snapshot for a learner."""

    course_id: str
    course_title: str
    completion_rate: float = Field(..., ge=0, le=1)
    assignments_completed: int
    assignments_total: int
    avg_score: float | None = None
    last_activity_at: str | None = None
    status: Literal["active", "completed", "at_risk", "inactive"]


class MasteryItem(BaseModel):
    """Competency or topic mastery signal."""

    competency_id: str
    competency_label: str
    mastery_level: Literal["emerging", "developing", "proficient", "advanced"]
    evidence_count: int
    last_assessed_at: str | None = None
    confidence: float = Field(..., ge=0, le=1)


class RiskIndicator(BaseModel):
    """Student risk signal with advisory context."""

    risk_id: str
    risk_type: Literal["attendance", "performance", "engagement", "completion"]
    severity: Literal["low", "medium", "high"]
    title: str
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


class LearnerProgressPayload(BaseModel):
    """Learner progress and strategy read model (P1)."""

    learner_id: str
    institution_id: str | None = None
    overall_status: Literal["on_track", "needs_support", "at_risk", "excelling"]
    courses: list[CourseProgressItem] = Field(default_factory=list)
    mastery: list[MasteryItem] = Field(default_factory=list)
    risks: list[RiskIndicator] = Field(default_factory=list)
    freshness: FreshnessMetadata
    trust: TrustMetadata


# ===== P1: Connector Health Read Model =====


class ConnectorHealthItem(BaseModel):
    """Connector health snapshot for monitoring."""

    connector_id: str
    provider: str
    status: Literal["active", "paused", "error", "initializing"]
    last_sync_at: str | None = None
    error_count: int = 0
    last_error: str | None = None
    events_synced_24h: int = 0
    avg_sync_duration_seconds: float | None = None


class ConnectorHealthPayload(BaseModel):
    """Connector health dashboard for a tenant (P1)."""

    tenant_id: str
    connectors: list[ConnectorHealthItem] = Field(default_factory=list)
    total_events_24h: int = 0
    total_errors_24h: int = 0
    freshness: FreshnessMetadata


# ===== P2/P3: Governed Intelligence And Lifelong Network Read Models =====


class SchoolUnitMetric(BaseModel):
    """Suppression-aware school-unit intelligence metric."""

    metric_id: str
    label: str | None = None
    value: float | None = Field(default=None, ge=0, le=1)
    sample_count: int = Field(..., ge=0)
    status: Literal["visible", "suppressed"]
    suppression: SuppressionMetadata


class SchoolUnitIntelligencePayload(BaseModel):
    """Supervisor-facing school-unit intelligence read model."""

    school_id: str
    unit_id: str
    tenant_id: str | None = None
    generated_at: str
    metrics: list[SchoolUnitMetric] = Field(default_factory=list)
    governance: IntelligenceGovernanceMetadata


class CausalDagEdge(BaseModel):
    """Directed DAG edge supplied by the research command."""

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)


class CausalSensitivityCheck(BaseModel):
    """Structured sensitivity check attached to a causal report."""

    check_id: str
    method: str
    target: str
    status: Literal["planned", "passed", "needs_review"]
    summary: str


class CausalRefutationResult(BaseModel):
    """Structured refutation result attached to a causal report."""

    check: str
    status: Literal["passed", "needs_review"]
    result: str


class CausalStudyCommand(BaseModel):
    """Command payload for deterministic causal-study report generation."""

    school_id: str = Field(..., min_length=1)
    tenant_id: str | None = None
    dag: str | None = None
    dag_edges: list[CausalDagEdge] | None = None
    treatment: str | None = None
    outcome: str | None = None
    estimand: str | None = None
    population: str | None = None
    confounders: list[str] | None = None
    refutation_checks: list[str] | None = None


class CausalStudyReport(BaseModel):
    """Deterministic causal-study report with validation and governance state."""

    study_id: str
    school_id: str
    tenant_id: str | None = None
    generated_at: str
    dag: str
    dag_edges: list[CausalDagEdge]
    treatment: str
    outcome: str
    estimand: str
    population: str
    adjustment_set: list[str]
    refutation_checks: list[str]
    sensitivity_checks: list[CausalSensitivityCheck]
    refutation_results: list[CausalRefutationResult]
    effect_estimate: float
    uncertainty: UncertaintyMetadata
    governance: IntelligenceGovernanceMetadata


class ConformalRiskItem(BaseModel):
    """Conformal risk item with label suppression."""

    risk_id: str
    risk_type: Literal["attendance", "performance", "engagement", "completion"]
    risk_label: str | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    sample_count: int = Field(..., ge=0)
    uncertainty: UncertaintyMetadata
    suppression: SuppressionMetadata


class ConformalRiskReport(BaseModel):
    """Conformal risk report with abstention and drift state."""

    learner_id: str
    context_id: str
    tenant_id: str | None = None
    generated_at: str
    calibration: CalibrationMetadata
    coverage: CoverageMetadata
    drift: DriftMetadata
    abstention: AbstentionMetadata
    risks: list[ConformalRiskItem] = Field(default_factory=list)
    governance: IntelligenceGovernanceMetadata


class LifelongLearnerNetworkPayload(BaseModel):
    """Learner-centered P3 lifelong network payload."""

    learner_id: str
    context_id: str
    tenant_id: str | None = None
    generated_at: str
    credential_definitions: list[CredentialDefinition] = Field(default_factory=list)
    credentials: list[CredentialAward] = Field(default_factory=list)
    portfolio_artifacts: list[PortfolioArtifact] = Field(default_factory=list)
    verification_requests: list[VerificationRequest] = Field(default_factory=list)
    alumni_affiliations: list[AlumniAffiliation] = Field(default_factory=list)
    re_entry_pathways: list[ReEntryPathway] = Field(default_factory=list)
    mentor_relationships: list[MentorRelationship] = Field(default_factory=list)
    community_events: list[CommunityEvent] = Field(default_factory=list)
    research_datasets: list[ResearchDataset] = Field(default_factory=list)
    data_use_agreements: list[DataUseAgreement] = Field(default_factory=list)
    de_identification_runs: list[DeIdentificationRun] = Field(default_factory=list)
    publication_approvals: list[PublicationApproval] = Field(default_factory=list)
    data_minimization: dict[str, str] = Field(default_factory=dict)
    governance: IntelligenceGovernanceMetadata


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
    HTTP_422_UNPROCESSABLE_CONTENT: {"model": BodyMessage},
}
