"""Mapper from Integration Hub canonical contracts to LearnerRecordEvents."""

from __future__ import annotations

from datetime import UTC, datetime

from tutor_lib.learner_record import (
    LearnerRecordDeepLink,
    LearnerRecordEvent,
    LearnerRecordEventBuilder,
    LearnerRecordSourceMetadata,
    build_learner_key,
    build_trust_metadata,
)

from .contracts import AttemptSubmission, EngagementSignal, Enrollment, PerformanceResult


class CanonicalValidationError(Exception):
    """Raised when canonical event fails validation."""


def validate_canonical_event(event: AttemptSubmission | PerformanceResult | EngagementSignal | Enrollment) -> None:
    """
    Validate canonical event before mapping to learner record.

    Raises:
        CanonicalValidationError: when event violates constraints.
    """
    if isinstance(event, PerformanceResult):
        # Score must not exceed points_possible
        if (
            event.score is not None
            and event.points_possible is not None
            and event.score > event.points_possible
        ):
            raise CanonicalValidationError(
                f"Score {event.score} exceeds points_possible {event.points_possible} "
                f"for activity {event.external_activity_id}"
            )


def canonical_to_learner_record_event(
    event: Enrollment | AttemptSubmission | PerformanceResult | EngagementSignal,
    *,
    learner_id: str,
    institution_id: str | None = None,
    deep_link_base_url: str = "",
) -> LearnerRecordEvent:
    """
    Map canonical Integration Hub contract to LearnerRecordEvent.

    Args:
        event: Canonical event from Integration Hub
        learner_id: Internal learner ID
        institution_id: Optional institution context
        deep_link_base_url: Base URL for constructing deep links

    Returns:
        LearnerRecordEvent with provenance, trust metadata, and idempotency key.
    """
    # Validate first
    validate_canonical_event(event)

    learner_key = build_learner_key(learner_id=learner_id, institution_id=institution_id)
    occurred_at = _extract_occurred_at(event)
    event_type, title, summary = _build_event_metadata(event)

    # Build source metadata
    source = LearnerRecordSourceMetadata(
        service="lms-gateway",
        capability="integration_hub",
        entity_type=type(event).__name__,
        entity_id=_extract_entity_id(event),
        institution_id=institution_id,
    )

    # Build trust metadata - Integration Hub events are external, require review
    trust = build_trust_metadata(
        source_type="external_lms",
        source_ids=[event.provider, event.provider_instance_id, _extract_entity_id(event)],
        generator="integration_hub_mapper",
        note=f"Ingested from {event.provider} via Integration Hub",
        degraded=False,
        evaluation_state="not_required",
        review_status="recommended",
        review_summary="External LMS event; recommend review for high-stakes decisions",
        advisory_only=True,
        workflow_version="integration-hub-v1",
    )

    # Build deep link
    deep_link = LearnerRecordDeepLink(
        label=f"View in {event.provider}",
        href=f"{deep_link_base_url}/external/{event.provider}/{_extract_entity_id(event)}",
    )

    # Use builder
    builder = LearnerRecordEventBuilder(
        learner_id=learner_id,
        learner_key=learner_key,
        event_type=event_type,
        source=source,
    )

    return (
        builder.occurred_at(occurred_at)
        .title(title)
        .summary(summary)
        .status("confirmed")
        .actor(role="learner", actor_id=learner_id)
        .trust(trust)
        .deep_link(label=deep_link.label, href=deep_link.href)
        .build()
    )


def _extract_occurred_at(event: Enrollment | AttemptSubmission | PerformanceResult | EngagementSignal) -> str:
    """Extract or infer occurred_at timestamp from canonical event."""
    if isinstance(event, EngagementSignal):
        return event.occurred_at
    elif isinstance(event, AttemptSubmission) and event.submitted_at:
        return event.submitted_at
    elif isinstance(event, PerformanceResult) and event.graded_at:
        return event.graded_at
    elif isinstance(event, Enrollment) and event.enrolled_at:
        return event.enrolled_at
    else:
        # Fallback to now
        return datetime.now(UTC).isoformat()


def _extract_entity_id(event: Enrollment | AttemptSubmission | PerformanceResult | EngagementSignal) -> str:
    """Extract primary entity ID from canonical event."""
    if isinstance(event, Enrollment):
        return event.external_enrollment_id
    elif isinstance(event, AttemptSubmission):
        return event.external_submission_id
    elif isinstance(event, PerformanceResult):
        return event.external_result_id
    elif isinstance(event, EngagementSignal):
        return event.external_signal_id
    return "unknown"


def _build_event_metadata(
    event: Enrollment | AttemptSubmission | PerformanceResult | EngagementSignal,
) -> tuple[str, str, str]:
    """Build event_type, title, and summary from canonical event."""
    if isinstance(event, Enrollment):
        event_type = "enrollment"
        title = f"Enrolled in course with role {event.role}"
        summary = f"Student enrolled in external context {event.external_context_id} as {event.role} (status: {event.status})"
    elif isinstance(event, AttemptSubmission):
        event_type = "submission"
        title = f"Submitted assignment (attempt {event.attempt_number or 1})"
        summary = f"Student submitted {event.submission_type or 'work'} for activity {event.external_activity_id}"
    elif isinstance(event, PerformanceResult):
        event_type = "performance"
        score_text = f"{event.score}/{event.points_possible}" if event.score is not None else "pending"
        title = f"Performance result: {score_text}"
        summary = (
            f"Student received {event.workflow_state or 'grade'} for activity {event.external_activity_id}: "
            f"{score_text}"
        )
    elif isinstance(event, EngagementSignal):
        event_type = "engagement"
        title = f"Engagement: {event.signal_type}"
        duration = f" ({event.duration_seconds}s)" if event.duration_seconds else ""
        summary = f"Student {event.signal_type} activity{duration}"
    else:
        event_type = "unknown"
        title = "Unknown event"
        summary = "Event type not recognized"

    # Truncate title and summary to reasonable lengths
    title = title[:200] if len(title) > 200 else title
    summary = summary[:500] if len(summary) > 500 else summary

    return event_type, title, summary
