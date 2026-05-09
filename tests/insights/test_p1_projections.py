"""Tests for Insights P1 learner progress and connector health projections."""

import importlib
import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Set test mode before importing app
os.environ["INSIGHTS_REPOSITORY"] = "memory"
os.environ["LEARNER_RECORD_PUBLISHER"] = "noop"
os.environ["ENTRA_AUTH_ENABLED"] = "false"

ROOT = Path(__file__).resolve().parents[2]
INSIGHTS_SRC = ROOT / "apps" / "insights" / "src"
LIB_SRC = ROOT / "lib" / "src"


def _prepare_service_import() -> None:
    for source_path in (LIB_SRC, INSIGHTS_SRC):
        if str(source_path) in sys.path:
            sys.path.remove(str(source_path))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(INSIGHTS_SRC))


def _clear_service_modules() -> None:
    for module_name in list(sys.modules):
        if (
            module_name == "app"
            or module_name.startswith("app.")
            or module_name == "tutor_lib.config"
            or module_name.startswith("tutor_lib.config.")
        ):
            sys.modules.pop(module_name, None)


_prepare_service_import()
_clear_service_modules()

from app import main as insights_main  # noqa: E402

importlib.reload(insights_main)

app = insights_main.app
reset_repository = insights_main.__dict__["reset_repository"]


def _student_headers(user_id: str = "learner-001") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Roles": "student",
    }


def _admin_headers(tenant_id: str = "tenant-123") -> dict[str, str]:
    return {
        "X-User-Id": "admin-1",
        "X-User-Roles": "admin",
        "X-Institution-Ids": tenant_id,
    }


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    """Reset repository state before each test."""
    reset_repository()


@pytest.mark.asyncio
async def test_learner_progress_empty() -> None:
    """Test learner progress endpoint with no events."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/learner-progress/learner-001",
            params={
                "context_id": "student:learner:learner-001",
                "institution_id": "univ-100",
            },
            headers=_student_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["learner_id"] == "learner-001"
    assert data["institution_id"] == "univ-100"
    assert data["overall_status"] == "needs_support"  # No events
    assert len(data["courses"]) == 0
    assert "freshness" in data
    assert "trust" in data


@pytest.mark.asyncio
async def test_learner_progress_with_events() -> None:
    """Test learner progress projection from learner-record events."""
    from datetime import UTC, datetime

    from tutor_lib.learner_record import (
        LearnerRecordEventBuilder,
        LearnerRecordSourceMetadata,
        build_learner_key,
        build_trust_metadata,
    )

    # Add some learner-record events first
    repo = insights_main.__dict__["_learner_record_repository"]()

    learner_key = build_learner_key(learner_id="learner-001", institution_id="univ-100")

    # Create a performance event
    builder = LearnerRecordEventBuilder(
        learner_id="learner-001",
        learner_key=learner_key,
        event_type="performance",
        source=LearnerRecordSourceMetadata(
            service="lms-gateway",
            capability="integration_hub",
            entity_type="PerformanceResult",
            entity_id="course-CS101",
        ),
    )
    event = (
        builder.occurred_at(datetime.now(UTC).isoformat())
        .title("Performance result: 85/100")
        .summary("Student received grade for activity")
        .status("confirmed")
        .actor(role="learner", actor_id="learner-001")
        .trust(
            build_trust_metadata(
                source_type="external_lms",
                source_ids=["canvas", "inst-456"],
                generator="integration_hub_mapper",
                note="Test event",
                degraded=False,
                evaluation_state="not_required",
                review_status="recommended",
                review_summary="External LMS event",
                advisory_only=True,
            )
        )
        .deep_link(label="View", href="/")
        .build()
    )
    await repo.append_event(event)

    # Now query learner progress
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/learner-progress/learner-001",
            params={
                "context_id": "student:learner:learner-001",
                "institution_id": "univ-100",
            },
            headers=_student_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["learner_id"] == "learner-001"
    assert data["overall_status"] == "on_track"
    assert len(data["courses"]) > 0
    assert data["courses"][0]["course_id"] == "course-CS101"


@pytest.mark.asyncio
async def test_learner_progress_rejects_out_of_scope_learner() -> None:
    """Test learner progress scope enforcement matches learner-record timeline."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/learner-progress/learner-002",
            params={"context_id": "student:learner:learner-001"},
            headers=_student_headers("learner-001"),
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_connector_health() -> None:
    """Test connector health dashboard endpoint."""
    from tutor_lib.integration_hub import ConnectorState

    repo = insights_main.__dict__["_connector_state_repository"]()
    await repo.save_connector(
        ConnectorState(
            tenant_id="tenant-123",
            provider="canvas",
            provider_instance_id="inst-456",
            connector_id="canvas:inst-456:tenant-123",
            status="error",
            last_sync_at="2026-05-09T09:00:00Z",
            error_message="Canvas API timeout",
            registered_at="2026-05-01T10:00:00Z",
        )
    )

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/connector-health?tenant_id=tenant-123",
            headers=_admin_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant-123"
    assert data["total_events_24h"] == 0
    assert data["total_errors_24h"] == 1
    assert data["connectors"] == [
        {
            "connector_id": "canvas:inst-456:tenant-123",
            "provider": "canvas",
            "status": "error",
            "last_sync_at": "2026-05-09T09:00:00Z",
            "error_count": 1,
            "last_error": "Canvas API timeout",
            "events_synced_24h": 0,
            "avg_sync_duration_seconds": None,
        }
    ]
    assert "freshness" in data


@pytest.mark.asyncio
async def test_connector_health_rejects_out_of_scope_tenant() -> None:
    """Test connector health tenant scope enforcement."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/connector-health?tenant_id=tenant-123",
            headers=_admin_headers("tenant-other"),
        )

    assert response.status_code == 403
