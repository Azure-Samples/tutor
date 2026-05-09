"""Tests for Integration Hub canonical contracts and repositories."""

from datetime import UTC, datetime
from hashlib import sha256
from types import SimpleNamespace

import pytest
from tutor_lib.config import CosmosConfig
from tutor_lib.integration_hub import (
    AttemptSubmission,
    CanonicalValidationError,
    ConnectorState,
    CosmosIdempotencyRepository,
    DeadLetterEntry,
    EngagementSignal,
    Enrollment,
    InMemoryConnectorStateRepository,
    InMemoryDeadLetterRepository,
    InMemoryIdempotencyRepository,
    PerformanceResult,
    build_idempotency_key,
    canonical_to_learner_record_event,
    validate_canonical_event,
)


def test_build_idempotency_key() -> None:
    """Test idempotency key construction."""
    key = build_idempotency_key(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        source_event_id="event-789",
    )
    assert key == "tenant-123|canvas|inst-456|event-789"

    key_with_version = build_idempotency_key(
        tenant_id="tenant-123",
        provider="moodle",
        provider_instance_id="inst-001",
        source_event_id="event-555",
        event_version="v2",
    )
    assert key_with_version == "tenant-123|moodle|inst-001|event-555|v2"


def test_cosmos_config_integration_hub_container_defaults() -> None:
    """Test dedicated Integration Hub container defaults."""
    config = CosmosConfig()  # type: ignore[call-arg]

    assert config.integration_idempotency_container == "integration_idempotency"
    assert config.integration_connectors_container == "integration_connectors"
    assert config.integration_dead_letters_container == "integration_dead_letters"


@pytest.mark.asyncio
async def test_idempotency_repository() -> None:
    """Test idempotency tracking repository."""
    repo = InMemoryIdempotencyRepository()

    key = "tenant-1|canvas|inst-1|event-100"

    initial = await repo.get_processed(key)
    assert not initial.already_processed
    assert initial.first_processed_at is None

    # First record should return not processed before this call
    recorded = await repo.record_processed(key)
    assert not recorded.already_processed
    assert recorded.idempotency_key == key
    assert recorded.first_processed_at is not None

    checked = await repo.get_processed(key)
    assert checked.already_processed
    assert checked.first_processed_at == recorded.first_processed_at

    repeated_record = await repo.record_processed(key)
    assert repeated_record.already_processed
    assert repeated_record.first_processed_at == recorded.first_processed_at

    # Compatibility method should still check and record in one call
    compat_key = "tenant-1|canvas|inst-1|event-101"
    result = await repo.check_and_record(compat_key)
    assert not result.already_processed
    assert result.idempotency_key == compat_key
    assert result.first_processed_at is not None

    # Second check should return already processed
    result2 = await repo.check_and_record(compat_key)
    assert result2.already_processed
    assert result2.first_processed_at == result.first_processed_at


@pytest.mark.asyncio
async def test_idempotency_repository_check_and_record_compatibility() -> None:
    """Test idempotency compatibility method records on first check."""
    repo = InMemoryIdempotencyRepository()

    key = "tenant-1|canvas|inst-1|event-100"

    result = await repo.check_and_record(key)
    assert not result.already_processed
    assert result.idempotency_key == key
    assert result.first_processed_at is not None

    # Second check should return already processed
    result2 = await repo.check_and_record(key)
    assert result2.already_processed
    assert result2.first_processed_at == result.first_processed_at


@pytest.mark.asyncio
async def test_cosmos_idempotency_repository_uses_hashed_document_id(monkeypatch) -> None:
    """Test Cosmos idempotency records use safe document IDs."""
    stores = []

    class FakeCosmosCRUD:
        def __init__(self, container_name: str, _cosmos: CosmosConfig) -> None:
            self.container_name = container_name
            self.created_payload: dict[str, object] | None = None
            self.partition_key: str | None = None
            stores.append(self)

        async def create_item_strict(
            self,
            payload: dict[str, object],
            *,
            partition_key: str | None = None,
        ) -> SimpleNamespace:
            self.created_payload = payload
            self.partition_key = partition_key
            return SimpleNamespace(created=True, item=payload)

    monkeypatch.setattr(
        "tutor_lib.integration_hub.repositories.CosmosCRUD",
        FakeCosmosCRUD,
    )
    repo = CosmosIdempotencyRepository(CosmosConfig())  # type: ignore[call-arg]
    key = build_idempotency_key(
        tenant_id="tenant-1",
        provider="canvas",
        provider_instance_id="inst-1",
        source_event_id="event/with?query=1",
        event_version="v2",
    )

    result = await repo.record_processed(key)

    assert not result.already_processed
    assert len(stores) == 1
    assert stores[0].container_name == "integration_idempotency"
    assert stores[0].partition_key == "tenant-1"
    expected_doc_id = f"idempotency:{sha256(key.encode('utf-8')).hexdigest()}"
    assert stores[0].created_payload == {
        "id": expected_doc_id,
        "docType": "idempotency_record",
        "tenant_id": "tenant-1",
        "provider": "canvas",
        "provider_instance_id": "inst-1",
        "source_event_id": "event/with?query=1",
        "event_version": "v2",
        "idempotency_key": key,
        "processed_at": result.first_processed_at,
    }


@pytest.mark.asyncio
async def test_connector_state_repository() -> None:
    """Test connector state repository."""
    repo = InMemoryConnectorStateRepository()

    state = ConnectorState(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        connector_id="canvas:inst-456:tenant-123",
        status="active",
        registered_at=datetime.now(UTC).isoformat(),
    )

    # Save connector
    saved = await repo.save_connector(state)
    assert saved.connector_id == state.connector_id

    # Get connector
    retrieved = await repo.get_connector(state.connector_id)
    assert retrieved is not None
    assert retrieved.provider == "canvas"
    assert retrieved.status == "active"

    # List connectors by tenant
    connectors = await repo.list_connectors("tenant-123")
    assert len(connectors) == 1
    assert connectors[0].connector_id == state.connector_id


@pytest.mark.asyncio
async def test_dead_letter_repository() -> None:
    """Test dead-letter repository."""
    repo = InMemoryDeadLetterRepository()

    entry = DeadLetterEntry(
        dead_letter_id="dl-001",
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        source_event_id="event-100",
        event_type="performance",
        occurred_at=datetime.now(UTC).isoformat(),
        received_at=datetime.now(UTC).isoformat(),
        error_type="validation",
        error_message="Score exceeds points_possible",
        raw_payload={"score": 110, "points_possible": 100},
    )

    # Add dead letter
    added = await repo.add_dead_letter(entry)
    assert added.dead_letter_id == "dl-001"
    assert not added.replayed

    # List dead letters
    entries = await repo.list_dead_letters("tenant-123", replayed=False)
    assert len(entries) == 1
    assert entries[0].dead_letter_id == "dl-001"

    retrieved = await repo.get_dead_letter("dl-001", tenant_id="tenant-123")
    assert retrieved is not None
    assert retrieved.dead_letter_id == "dl-001"

    cross_tenant = await repo.get_dead_letter("dl-001", tenant_id="tenant-other")
    assert cross_tenant is None

    denied_update = await repo.mark_replayed(
        "dl-001",
        datetime.now(UTC).isoformat(),
        tenant_id="tenant-other",
    )
    assert denied_update is None

    # Mark replayed
    replayed_at = datetime.now(UTC).isoformat()
    updated = await repo.mark_replayed("dl-001", replayed_at, tenant_id="tenant-123")
    assert updated is not None
    assert updated.replayed
    assert updated.replayed_at == replayed_at
    assert updated.retry_count == 1


def test_validate_canonical_event_valid_performance() -> None:
    """Test validation passes for valid performance result."""
    event = PerformanceResult(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_result_id="result-001",
        external_activity_id="activity-100",
        external_user_id="user-200",
        score=85.0,
        points_possible=100.0,
    )

    # Should not raise
    validate_canonical_event(event)


def test_validate_canonical_event_invalid_performance() -> None:
    """Test validation fails when score exceeds points_possible."""
    event = PerformanceResult(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_result_id="result-001",
        external_activity_id="activity-100",
        external_user_id="user-200",
        score=110.0,
        points_possible=100.0,
    )

    with pytest.raises(CanonicalValidationError) as exc_info:
        validate_canonical_event(event)

    assert "Score 110.0 exceeds points_possible 100.0" in str(exc_info.value)


def test_canonical_to_learner_record_enrollment() -> None:
    """Test mapping enrollment to learner record event."""
    enrollment = Enrollment(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_enrollment_id="enroll-001",
        external_user_id="user-200",
        external_context_id="course-CS101",
        role="learner",
        status="active",
        enrolled_at="2026-05-01T10:00:00Z",
    )

    event = canonical_to_learner_record_event(
        enrollment,
        learner_id="learner-123",
        institution_id="univ-456",
    )

    assert event.event_type == "enrollment"
    assert event.learner_id == "learner-123"
    assert "Enrolled in course with role learner" in event.title
    assert event.source.service == "lms-gateway"
    assert event.trust.advisory_only
    assert event.trust.human_review.status == "recommended"


def test_canonical_to_learner_record_performance() -> None:
    """Test mapping performance result to learner record event."""
    performance = PerformanceResult(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_result_id="result-001",
        external_activity_id="activity-100",
        external_user_id="user-200",
        score=85.0,
        points_possible=100.0,
        graded_at="2026-05-05T14:30:00Z",
    )

    event = canonical_to_learner_record_event(
        performance,
        learner_id="learner-123",
        institution_id="univ-456",
    )

    assert event.event_type == "performance"
    assert "85.0/100.0" in event.title
    assert event.occurred_at.startswith("2026-05-05T14:30:00")
    assert event.trust.provenance.generator == "integration_hub_mapper"


def test_canonical_to_learner_record_engagement() -> None:
    """Test mapping engagement signal to learner record event."""
    engagement = EngagementSignal(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_signal_id="signal-001",
        external_user_id="user-200",
        external_context_id="course-CS101",
        signal_type="page_view",
        occurred_at="2026-05-09T08:15:00Z",
        duration_seconds=120,
    )

    event = canonical_to_learner_record_event(
        engagement,
        learner_id="learner-123",
    )

    assert event.event_type == "engagement"
    assert "page_view" in event.title
    assert event.occurred_at.startswith("2026-05-09T08:15:00")


def test_canonical_to_learner_record_submission() -> None:
    """Test mapping submission to learner record event."""
    submission = AttemptSubmission(
        tenant_id="tenant-123",
        provider="canvas",
        provider_instance_id="inst-456",
        external_submission_id="sub-001",
        external_activity_id="activity-100",
        external_user_id="user-200",
        attempt_number=1,
        submitted_at="2026-05-04T16:45:00Z",
        submission_type="file_upload",
    )

    event = canonical_to_learner_record_event(
        submission,
        learner_id="learner-123",
    )

    assert event.event_type == "submission"
    assert "attempt 1" in event.title
    assert event.occurred_at.startswith("2026-05-04T16:45:00")
