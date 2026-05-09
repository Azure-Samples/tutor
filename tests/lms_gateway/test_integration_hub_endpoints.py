"""Tests for LMS Gateway Integration Hub P1 endpoints."""

import importlib
import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Set test mode before importing app
os.environ["LMS_REPOSITORY_MODE"] = "memory"
os.environ["ENTRA_AUTH_ENABLED"] = "false"

ROOT = Path(__file__).resolve().parents[2]
LMS_SRC = ROOT / "apps" / "lms-gateway" / "src"
LIB_SRC = ROOT / "lib" / "src"


def _prepare_service_import() -> None:
    for source_path in (LIB_SRC, LMS_SRC):
        if str(source_path) in sys.path:
            sys.path.remove(str(source_path))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))


def _clear_app_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)


_prepare_service_import()
_clear_app_modules()

from app import main as lms_main  # noqa: E402

importlib.reload(lms_main)

app = lms_main.app


def _tenant_headers(tenant_id: str = "tenant-123") -> dict[str, str]:
    return {
        "X-User-Id": "admin-1",
        "X-User-Roles": "admin",
        "X-Institution-Ids": tenant_id,
    }


def reset_repository() -> None:
    """Reset repository caches for test isolation."""
    for cache_name in (
        "_connector_state_repo",
        "_dead_letter_repo",
        "_idempotency_repo",
        "_learner_record_repo",
        "_job_queue",
        "_job_store",
        "_settings",
    ):
        lms_main.__dict__[cache_name].cache_clear()


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    """Reset repository state before each test."""
    reset_repository()


@pytest.mark.asyncio
async def test_register_connector() -> None:
    """Test connector registration endpoint."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/connectors",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "connector_id" in data
    assert data["status"] == "initializing"
    assert "registered_at" in data


@pytest.mark.asyncio
async def test_get_connector_state_returns_public_config_projection() -> None:
    """Test connector detail responses only expose allowlisted config fields."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register_response = await client.post(
            "/integration/connectors",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "config": {
                    "base_url": "https://canvas.example",
                    "course_filters": {
                        "course_ids": ["course-CS101"],
                        "access_token": "nested-token",
                    },
                    "access_token": "raw-token",
                    "password": "raw-password",
                    "clientSecret": "raw-secret",
                    "api_key": "raw-key",
                    "nested": {
                        "refreshToken": "raw-refresh-token",
                        "display_name": "Canvas production",
                    },
                    "headers": [{"Authorization": "Bearer raw-authorization"}],
                },
            },
        )
        connector_id = register_response.json()["connector_id"]

        response = await client.get(
            f"/integration/connectors/{connector_id}",
            headers=_tenant_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    config = data["config"]
    assert config == {
        "base_url": "https://canvas.example",
        "course_filters": {"course_ids": ["course-CS101"]},
    }

    serialized_response = response.text
    assert "nested-token" not in serialized_response
    assert "raw-token" not in serialized_response
    assert "raw-password" not in serialized_response
    assert "raw-secret" not in serialized_response
    assert "raw-key" not in serialized_response
    assert "raw-refresh-token" not in serialized_response
    assert "raw-authorization" not in serialized_response
    assert "nested" not in serialized_response
    assert "headers" not in serialized_response


@pytest.mark.asyncio
async def test_integration_endpoint_rejects_cross_tenant_request() -> None:
    """Test Integration Hub endpoints reject tenants outside caller scope."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/connectors",
            headers=_tenant_headers("tenant-allowed"),
            json={
                "tenant_id": "tenant-denied",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
            },
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_connectors() -> None:
    """Test list connectors endpoint."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register a connector first
        await client.post(
            "/integration/connectors",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
            },
        )

        # List connectors
        response = await client.get(
            "/integration/connectors?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["provider"] == "canvas"


@pytest.mark.asyncio
async def test_ingest_canonical_event_enrollment() -> None:
    """Test canonical event ingestion for enrollment."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "enrollment",
                "learner_id": "learner-001",
                "institution_id": "univ-100",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_enrollment_id": "enroll-001",
                    "external_user_id": "user-200",
                    "external_context_id": "course-CS101",
                    "role": "learner",
                    "status": "active",
                    "enrolled_at": "2026-05-01T10:00:00Z",
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"
    assert "event_id" in data
    assert "learner_key" in data


@pytest.mark.asyncio
async def test_ingest_canonical_event_idempotency() -> None:
    """Test idempotency prevents duplicate ingestion."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "tenant_id": "tenant-123",
            "provider": "canvas",
            "provider_instance_id": "inst-456",
            "event_type": "enrollment",
            "learner_id": "learner-001",
            "event_payload": {
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "external_enrollment_id": "enroll-001",  # Used for idempotency
                "external_user_id": "user-200",
                "external_context_id": "course-CS101",
                "role": "learner",
                "status": "active",
                "enrolled_at": "2026-05-01T10:00:00Z",
            },
        }

        # First ingestion
        response1 = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json=payload,
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["status"] == "ingested"

        # Second ingestion (duplicate) - same payload
        response2 = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json=payload,
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["status"] == "duplicate"
        assert data2["idempotency_key"] == data1["idempotency_key"]


@pytest.mark.asyncio
async def test_ingest_canonical_event_invalid_score() -> None:
    """Test invalid performance result goes to dead letter queue."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-001",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 110.0,
                    "points_possible": 100.0,
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dead_letter"
    assert "dead_letter_id" in data
    assert "Score 110.0 exceeds points_possible 100.0" in data["error"]


@pytest.mark.asyncio
async def test_invalid_ingestion_does_not_mark_idempotency_processed() -> None:
    """Test corrected event can ingest after invalid payload dead-letters."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        invalid_payload = {
            "tenant_id": "tenant-123",
            "provider": "canvas",
            "provider_instance_id": "inst-456",
            "event_type": "performance",
            "learner_id": "learner-001",
            "event_payload": {
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "external_result_id": "result-002",
                "external_activity_id": "activity-100",
                "external_user_id": "user-200",
                "score": 110.0,
                "points_possible": 100.0,
                "graded_at": "2026-05-05T14:30:00Z",
            },
        }
        invalid_response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json=invalid_payload,
        )
        assert invalid_response.status_code == 200
        assert invalid_response.json()["status"] == "dead_letter"

        corrected_payload = {
            **invalid_payload,
            "event_payload": {
                **invalid_payload["event_payload"],
                "score": 88.0,
            },
        }
        corrected_response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json=corrected_payload,
        )

    assert corrected_response.status_code == 200
    assert corrected_response.json()["status"] == "ingested"


@pytest.mark.asyncio
async def test_ingest_dead_letters_payload_envelope_mismatch() -> None:
    """Test canonical payload envelope mismatches are dead-lettered."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-other",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-mismatch",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 88.0,
                    "points_possible": 100.0,
                },
            },
        )
        dead_letters = await client.get(
            "/integration/dead-letters?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dead_letter"
    assert "tenant_id" in data["error"]
    assert "trusted envelope" in data["error"]
    assert dead_letters.status_code == 200
    assert len(dead_letters.json()) == 1
    assert dead_letters.json()[0]["error_type"] == "validation"


@pytest.mark.asyncio
async def test_ingest_dead_letters_missing_payload_envelope_field() -> None:
    """Test missing canonical fields use dataclass validation dead-lettering."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-missing-envelope",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 88.0,
                    "points_possible": 100.0,
                },
            },
        )
        dead_letters = await client.get(
            "/integration/dead-letters?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dead_letter"
    assert "tenant_id" in data["error"]
    assert dead_letters.status_code == 200
    assert len(dead_letters.json()) == 1
    assert dead_letters.json()[0]["error_type"] == "validation"


@pytest.mark.asyncio
async def test_list_dead_letters() -> None:
    """Test list dead letters endpoint."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ingest invalid event to create dead letter
        await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-001",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 110.0,
                    "points_possible": 100.0,
                },
            },
        )

        # List dead letters
        response = await client.get(
            "/integration/dead-letters?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["error_type"] == "validation"
    assert not data[0]["replayed"]


@pytest.mark.asyncio
async def test_replay_dead_letter() -> None:
    """Test replay dead letter endpoint."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create dead letter
        ingest_response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-001",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 110.0,
                    "points_possible": 100.0,
                },
            },
        )
        dead_letter_id = ingest_response.json()["dead_letter_id"]

        failed_replay_response = await client.post(
            "/integration/dead-letters/replay",
            headers=_tenant_headers(),
            json={"tenant_id": "tenant-123", "dead_letter_id": dead_letter_id},
        )

        list_after_failed_replay = await client.get(
            "/integration/dead-letters?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

        replay_response = await client.post(
            "/integration/dead-letters/replay",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "dead_letter_id": dead_letter_id,
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-001",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 92.0,
                    "points_possible": 100.0,
                },
            },
        )

    assert failed_replay_response.status_code == 422
    assert not list_after_failed_replay.json()[0]["replayed"]
    assert replay_response.status_code == 200
    data = replay_response.json()
    assert data["status"] == "replayed"
    assert data["retry_count"] == "1"
    assert data["event_id"]


@pytest.mark.asyncio
async def test_replay_dead_letter_rejects_payload_envelope_mismatch() -> None:
    """Test replay validates corrected payload against stored envelope."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ingest_response = await client.post(
            "/integration/ingest",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "provider": "canvas",
                "provider_instance_id": "inst-456",
                "event_type": "performance",
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "canvas",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-replay-mismatch",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 110.0,
                    "points_possible": 100.0,
                },
            },
        )
        dead_letter_id = ingest_response.json()["dead_letter_id"]

        replay_response = await client.post(
            "/integration/dead-letters/replay",
            headers=_tenant_headers(),
            json={
                "tenant_id": "tenant-123",
                "dead_letter_id": dead_letter_id,
                "learner_id": "learner-001",
                "event_payload": {
                    "tenant_id": "tenant-123",
                    "provider": "moodle",
                    "provider_instance_id": "inst-456",
                    "external_result_id": "result-replay-mismatch",
                    "external_activity_id": "activity-100",
                    "external_user_id": "user-200",
                    "score": 92.0,
                    "points_possible": 100.0,
                },
            },
        )
        list_after_replay = await client.get(
            "/integration/dead-letters?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )

    assert replay_response.status_code == 422
    assert "provider" in replay_response.json()["detail"]
    assert "trusted envelope" in replay_response.json()["detail"]
    assert not list_after_replay.json()[0]["replayed"]


@pytest.mark.asyncio
async def test_standards_placeholder_endpoints() -> None:
    """Test P1 placeholder endpoints for standards."""
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # OneRoster
        response_or = await client.post(
            "/integration/oneroster/import?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )
        assert response_or.status_code == 200
        assert "placeholder" in response_or.json()["status"]

        # LTI
        response_lti = await client.post(
            "/integration/lti/launch?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )
        assert response_lti.status_code == 200
        assert "placeholder" in response_lti.json()["status"]

        # Caliper
        response_cal = await client.post(
            "/integration/caliper/events?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )
        assert response_cal.status_code == 200
        assert "placeholder" in response_cal.json()["status"]

        # xAPI
        response_xapi = await client.post(
            "/integration/xapi/statements?tenant_id=tenant-123",
            headers=_tenant_headers(),
        )
        assert response_xapi.status_code == 200
        assert "placeholder" in response_xapi.json()["status"]
