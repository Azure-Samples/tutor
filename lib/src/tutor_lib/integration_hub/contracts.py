"""Canonical Integration Hub contracts for external learning systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ConnectorStatus = Literal["active", "paused", "error", "initializing"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ExternalIdentity:
    """Maps provider users to tenant-scoped learner/professor/supervisor identities."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_user_id: str
    external_username: str | None = None
    display_name: str | None = None
    email: str | None = None
    internal_user_id: str | None = None
    role: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearningContext:
    """Course, class, cohort, program, unit, term, section, or activity grouping."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_context_id: str
    context_type: str  # "course", "section", "program", "cohort", "unit"
    title: str
    code: str | None = None
    term: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    institution_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Enrollment:
    """Role and lifecycle state in a learning context."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_enrollment_id: str
    external_user_id: str
    external_context_id: str
    role: str  # "learner", "instructor", "ta", "observer"
    status: str  # "active", "completed", "withdrawn", "inactive"
    enrolled_at: str | None = None
    completed_at: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearningActivity:
    """Assignment, quiz, reading, discussion, lab, project, video, or tool launch."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_activity_id: str
    external_context_id: str
    activity_type: str  # "assignment", "quiz", "discussion", "reading", "video", "tool_launch"
    title: str
    description: str | None = None
    points_possible: float | None = None
    due_date: str | None = None
    published_at: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AttemptSubmission:
    """Attempt, submission, answer, draft, interaction, or uploaded evidence."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_submission_id: str
    external_activity_id: str
    external_user_id: str
    attempt_number: int | None = None
    submitted_at: str | None = None
    submission_type: str | None = None  # "online_text", "file_upload", "url", "media"
    body: str | None = None
    attachments: list[str] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PerformanceResult:
    """Grade, rubric score, mastery signal, feedback, grading state."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_result_id: str
    external_activity_id: str
    external_user_id: str
    score: float | None = None
    points_possible: float | None = None
    grade: str | None = None
    graded_at: str | None = None
    grader_id: str | None = None
    feedback: str | None = None
    workflow_state: str | None = None  # "graded", "pending", "excused"


@dataclass(frozen=True, slots=True, kw_only=True)
class EngagementSignal:
    """Attendance, access, media, reading, forum, practice, or tool-use metric."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    external_signal_id: str
    external_user_id: str
    external_context_id: str | None = None
    external_activity_id: str | None = None
    signal_type: str  # "attendance", "page_view", "video_play", "forum_post", "practice"
    occurred_at: str
    duration_seconds: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectorState:
    """Connector instance registration and sync state."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    connector_id: str
    status: ConnectorStatus
    last_sync_at: str | None = None
    last_sync_cursor: str | None = None
    error_message: str | None = None
    registered_at: str
    config: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectorHealth:
    """Connector health snapshot for monitoring and alerting."""

    connector_id: str
    tenant_id: str
    provider: str
    status: ConnectorStatus
    last_sync_at: str | None = None
    error_count: int = 0
    last_error: str | None = None
    events_synced_24h: int = 0
    avg_sync_duration_seconds: float | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class DeadLetterEntry:
    """Failed ingestion event for manual review and replay."""

    dead_letter_id: str
    tenant_id: str
    provider: str
    provider_instance_id: str
    source_event_id: str
    event_type: str
    occurred_at: str
    received_at: str
    error_type: str  # "validation", "mapping", "duplicate", "constraint"
    error_message: str
    raw_payload: dict[str, Any]
    retry_count: int = 0
    replayed: bool = False
    replayed_at: str | None = None
