import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
INSIGHTS_SRC = ROOT / "apps" / "insights" / "src"
LIB_SRC = ROOT / "lib" / "src"


@pytest.fixture(name="insights_module")
def fixture_insights_module(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("INSIGHTS_REPOSITORY", "memory")
    monkeypatch.setenv("LEARNER_RECORD_PUBLISHER", "memory")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(INSIGHTS_SRC) in sys.path:
        sys.path.remove(str(INSIGHTS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(INSIGHTS_SRC))

    for module_name in list(sys.modules):
        if (
            module_name == "app"
            or module_name.startswith("app.")
            or module_name == "tutor_lib.config"
            or module_name.startswith("tutor_lib.config.")
        ):
            sys.modules.pop(module_name, None)

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)
    main_module.reset_repository()

    return main_module


@pytest.fixture(name="api_client")
def fixture_api_client(insights_module):
    return TestClient(insights_module.app)


def _supervisor_headers(school_ids: str = "school-a") -> dict[str, str]:
    return {
        "X-User-Id": "supervisor-1",
        "X-User-Roles": "supervisor",
        "X-School-Ids": school_ids,
    }


def _admin_headers() -> dict[str, str]:
    return {
        "X-User-Id": "admin-1",
        "X-User-Roles": "admin",
    }


def _professor_headers() -> dict[str, str]:
    return {
        "X-User-Id": "prof-1",
        "X-User-Roles": "professor",
    }


def _principal_headers(school_ids: str = "school-a") -> dict[str, str]:
    return {
        "X-User-Id": "principal-1",
        "X-User-Roles": "principal",
        "X-School-Ids": school_ids,
    }


def _student_headers(user_id: str = "learner-1") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Roles": "student",
    }


def _content(response):
    return response.json()["content"]


def _learner_record_module():
    if str(LIB_SRC) not in sys.path:
        sys.path.insert(0, str(LIB_SRC))
    return importlib.import_module("tutor_lib.learner_record")


def _sample_event(module, *, learner_id: str, title: str, occurred_at: str, event_type: str, status: str = "confirmed", compensates_event_id: str | None = None):
    learner_key = module.build_learner_key(learner_id=learner_id)
    builder = module.LearnerRecordEventBuilder(
        learner_id=learner_id,
        learner_key=learner_key,
        event_type=event_type,
        source=module.LearnerRecordSourceMetadata(
            service="tests.insights",
            capability="unit-test",
            entity_type="test_event",
            entity_id=f"{event_type}:{title}",
        ),
    )
    builder = (
        builder.occurred_at(occurred_at)
        .recorded_at(occurred_at)
        .title(title)
        .summary(f"Summary for {title}")
        .status(status)
        .actor(role="professor", actor_id="prof-1")
        .deep_link(label="Open related surface", href="/essays")
        .add_evidence(
            module.LearnerRecordEvidenceRef(
                evidence_id=f"evidence:{title}",
                label="Test evidence",
                kind="unit-test",
                deep_link=module.LearnerRecordDeepLink(
                    label="Open related surface",
                    href="/essays",
                ),
            )
        )
        .trust(
            module.build_trust_metadata(
                source_type="unit-test",
                source_ids=[f"learner:{learner_id}", f"title:{title}"],
                generator="tests.insights",
                note="Unit-test trust payload",
                degraded=status == "degraded",
                evaluation_state="evaluated",
                review_status="required",
                review_summary="Unit-test review state",
                advisory_only=status != "confirmed",
            )
        )
    )
    if compensates_event_id is not None:
        builder = builder.compensates(
            event_id=compensates_event_id,
            reason="Corrected by unit test",
        )
    return builder.build()


def _create_report(api_client: TestClient, school_id: str, headers: dict[str, str]) -> dict[str, object]:
    response = api_client.post(
        "/briefing",
        json={"school_id": school_id, "week_of": "2026-W13", "on_demand": True},
        headers=headers,
    )
    assert response.status_code == 201
    return _content(response)


def test_briefing_report_and_feedback_lifecycle(api_client: TestClient):
    report = _create_report(api_client, "school-a", _supervisor_headers("school-a,school-b"))
    assert report["school_id"] == "school-a"
    assert isinstance(report["trends"], list)
    assert isinstance(report["alerts"], list)
    assert isinstance(report["focus_points"], list)
    assert isinstance(report["improvements"], list)

    list_response = api_client.get("/reports", headers=_supervisor_headers("school-a,school-b"))
    assert list_response.status_code == 200
    reports = _content(list_response)
    assert len(reports) == 1

    get_response = api_client.get(
        f"/reports/{report['report_id']}",
        headers=_supervisor_headers("school-a,school-b"),
    )
    assert get_response.status_code == 200

    feedback_response = api_client.post(
        "/feedback",
        json={
            "report_id": report["report_id"],
            "school_id": "school-a",
            "rating": 5,
            "comments": "Very actionable.",
        },
        headers=_supervisor_headers("school-a,school-b"),
    )
    assert feedback_response.status_code == 201
    feedback = _content(feedback_response)
    assert feedback["report_id"] == report["report_id"]

    feedback_list_response = api_client.get(
        f"/reports/{report['report_id']}/feedback",
        headers=_supervisor_headers("school-a,school-b"),
    )
    assert feedback_list_response.status_code == 200
    feedback_rows = _content(feedback_list_response)
    assert len(feedback_rows) == 1
    assert feedback_rows[0]["feedback_id"] == feedback["feedback_id"]

    refreshed_report = _content(
        api_client.get(f"/reports/{report['report_id']}", headers=_supervisor_headers("school-a,school-b"))
    )
    assert refreshed_report["feedback_count"] == 1

    metrics_response = api_client.get("/pilot/metrics", headers=_supervisor_headers("school-a,school-b"))
    assert metrics_response.status_code == 200
    metrics = _content(metrics_response)
    assert metrics["total_reports"] == 1
    assert metrics["total_feedback"] == 1
    assert metrics["reports_with_feedback"] == 1
    assert metrics["average_rating"] == 5
    assert metrics["feedback_rate"] == 1


def test_out_of_scope_school_is_forbidden(api_client: TestClient):
    response = api_client.post(
        "/briefing",
        json={"school_id": "school-b", "week_of": "2026-W13", "on_demand": True},
        headers=_supervisor_headers("school-a"),
    )
    assert response.status_code == 403


def test_out_of_scope_report_read_is_forbidden(api_client: TestClient):
    created = _create_report(api_client, "school-z", _admin_headers())

    forbidden = api_client.get(
        f"/reports/{created['report_id']}",
        headers=_supervisor_headers("school-a"),
    )
    assert forbidden.status_code == 403

    feedback_forbidden = api_client.get(
        f"/reports/{created['report_id']}/feedback",
        headers=_supervisor_headers("school-a"),
    )
    assert feedback_forbidden.status_code == 403


def test_supervisor_without_scope_claim_cannot_list_reports(api_client: TestClient):
    api_client.post(
        "/briefing",
        json={"school_id": "school-a", "week_of": "2026-W13"},
        headers=_supervisor_headers("school-a"),
    )

    list_response = api_client.get(
        "/reports",
        headers={"X-User-Id": "supervisor-1", "X-User-Roles": "supervisor"},
    )
    assert list_response.status_code == 403


def test_local_dev_fallback_allows_targeted_school_write(api_client: TestClient):
    response = api_client.post(
        "/briefing",
        json={"school_id": "school-fallback", "week_of": "2026-W13"},
        headers={"X-User-Id": "supervisor-1", "X-User-Roles": "supervisor"},
    )
    assert response.status_code == 201


def test_pilot_scope_allows_allowlisted_supervisor_and_school(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INSIGHTS_PILOT_ENABLED", "true")
    monkeypatch.setenv("INSIGHTS_PILOT_SCHOOL_IDS", "school-a")
    monkeypatch.setenv("INSIGHTS_PILOT_SUPERVISOR_IDS", "supervisor-1")

    report = _create_report(api_client, "school-a", _supervisor_headers("school-a"))
    assert report["school_id"] == "school-a"

    metrics_response = api_client.get("/pilot/metrics", headers=_supervisor_headers("school-a"))
    assert metrics_response.status_code == 200
    metrics = _content(metrics_response)
    assert metrics["total_reports"] == 1
    assert metrics["school_count"] == 1


def test_pilot_scope_rejects_non_allowlisted_supervisor(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INSIGHTS_PILOT_ENABLED", "true")
    monkeypatch.setenv("INSIGHTS_PILOT_SCHOOL_IDS", "school-a")
    monkeypatch.setenv("INSIGHTS_PILOT_SUPERVISOR_IDS", "supervisor-9")

    response = api_client.post(
        "/briefing",
        json={"school_id": "school-a", "week_of": "2026-W13", "on_demand": True},
        headers=_supervisor_headers("school-a"),
    )
    assert response.status_code == 403


def test_pilot_scope_rejects_non_allowlisted_school(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INSIGHTS_PILOT_ENABLED", "true")
    monkeypatch.setenv("INSIGHTS_PILOT_SCHOOL_IDS", "school-a")
    monkeypatch.setenv("INSIGHTS_PILOT_SUPERVISOR_IDS", "supervisor-1")

    response = api_client.post(
        "/briefing",
        json={"school_id": "school-b", "week_of": "2026-W13", "on_demand": True},
        headers=_supervisor_headers("school-a,school-b"),
    )
    assert response.status_code == 403


def test_pilot_metrics_honors_school_query_scope(api_client: TestClient):
    _create_report(api_client, "school-a", _supervisor_headers("school-a,school-b"))
    _create_report(api_client, "school-b", _supervisor_headers("school-a,school-b"))

    metrics_response = api_client.get(
        "/pilot/metrics",
        params={"school_id": "school-a"},
        headers=_supervisor_headers("school-a,school-b"),
    )
    assert metrics_response.status_code == 200
    metrics = _content(metrics_response)
    assert metrics["total_reports"] == 1
    assert metrics["school_count"] == 1


def test_workspace_snapshot_reuses_stored_report_for_principal(api_client: TestClient):
    report = _create_report(api_client, "school-a", _admin_headers())

    response = api_client.get(
        "/workspace-snapshots/principal",
        params={"context_id": "principal:school:school-a"},
        headers=_principal_headers("school-a"),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["role"] == "principal"
    assert content["context_id"] == "principal:school:school-a"
    assert content["freshness"]["status"] == "fresh"
    assert content["trust"]["provenance"]["source_ids"][0] == report["report_id"]
    assert content["deterministic_highlights"]
    assert content["deep_links"][0]["href"] == "/configuration/supervisor"


def test_workspace_snapshot_rejects_out_of_scope_context(api_client: TestClient):
    response = api_client.get(
        "/workspace-snapshots/supervisor",
        params={"context_id": "supervisor:school:school-b"},
        headers=_supervisor_headers("school-a"),
    )

    assert response.status_code == 403


def test_learner_record_returns_cursor_shape(api_client: TestClient):
    response = api_client.get(
        "/learner-records/learner-1",
        params={"context_id": "student:learner:learner-1", "limit": 2},
        headers=_student_headers("learner-1"),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["learner_id"] == "learner-1"
    assert content["context_id"] == "student:learner:learner-1"
    assert content["page"] == {
        "limit": 2,
        "cursor": None,
        "next_cursor": "2",
        "has_more": True,
    }
    assert len(content["entries"]) == 2
    assert content["entries"][0]["trust"]["provenance"]["source_ids"][1] == "learner:learner-1"
    assert content["entries"][0]["deep_link"]["href"]


def test_learner_record_rejects_out_of_scope_learner(api_client: TestClient):
    response = api_client.get(
        "/learner-records/learner-2",
        params={"context_id": "student:learner:learner-1"},
        headers=_student_headers("learner-1"),
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_learner_record_repository_append_is_idempotent(insights_module):
    learner_record = _learner_record_module()
    repository = insights_module._learner_record_repository()
    publisher = insights_module._learner_record_event_publisher()

    base_event = _sample_event(
        learner_record,
        learner_id="learner-1",
        title="Essay feedback appended",
        occurred_at="2026-04-08T09:00:00Z",
        event_type="essay_feedback",
    )
    compensation_event = _sample_event(
        learner_record,
        learner_id="learner-1",
        title="Essay feedback corrected",
        occurred_at="2026-04-08T10:00:00Z",
        event_type="essay_feedback_corrected",
        status="needs_review",
        compensates_event_id=base_event.event_id,
    )

    first_append = await repository.append_event(base_event)
    second_append = await repository.append_event(base_event)
    stored_compensation = await repository.append_event(compensation_event)
    events = await repository.list_events(learner_key=base_event.learner_key)

    assert first_append.event_id == second_append.event_id
    assert len(events) == 2
    assert stored_compensation.compensation is not None
    assert stored_compensation.compensation.compensates_event_id == base_event.event_id
    assert isinstance(publisher, learner_record.InMemoryLearnerRecordEventPublisher)
    assert [event.event_id for event in publisher.published_events] == [
        base_event.event_id,
        compensation_event.event_id,
    ]


def test_learner_record_replays_persisted_events_in_order(api_client: TestClient, insights_module):
    learner_record = _learner_record_module()
    repository = insights_module._learner_record_repository()

    older_event = _sample_event(
        learner_record,
        learner_id="learner-1",
        title="Older event",
        occurred_at="2026-04-08T08:00:00Z",
        event_type="older_event",
    )
    newer_event = _sample_event(
        learner_record,
        learner_id="learner-1",
        title="Newer event",
        occurred_at="2026-04-08T11:00:00Z",
        event_type="newer_event",
    )

    import asyncio

    asyncio.run(repository.append_event(older_event))
    asyncio.run(repository.append_event(newer_event))

    response = api_client.get(
        "/learner-records/learner-1",
        params={"context_id": "student:learner:learner-1", "limit": 10},
        headers=_student_headers("learner-1"),
    )

    assert response.status_code == 200
    content = _content(response)
    assert [entry["title"] for entry in content["entries"]] == ["Newer event", "Older event"]
    assert content["entries"][0]["source_service"] == "tests.insights"


def test_learner_record_seed_backfill_is_persisted_once(api_client: TestClient, insights_module):
    publisher = insights_module._learner_record_event_publisher()

    response = api_client.get(
        "/learner-records/learner-1",
        params={"context_id": "student:learner:learner-1", "limit": 10},
        headers=_student_headers("learner-1"),
    )
    assert response.status_code == 200

    repeated_response = api_client.get(
        "/learner-records/learner-1",
        params={"context_id": "student:learner:learner-1", "limit": 10},
        headers=_student_headers("learner-1"),
    )
    assert repeated_response.status_code == 200

    repository = insights_module._learner_record_repository()
    learner_record = _learner_record_module()
    stored_events = __import__("asyncio").run(
        repository.list_events(learner_key=learner_record.build_learner_key(learner_id="learner-1"))
    )

    assert len(stored_events) == len(_content(response)["entries"])
    assert [event.event_id for event in stored_events] == [
        event.event_id for event in __import__("asyncio").run(
            repository.list_events(learner_key=learner_record.build_learner_key(learner_id="learner-1"))
        )
    ]
    assert isinstance(publisher, learner_record.InMemoryLearnerRecordEventPublisher)
    assert [event.event_id for event in publisher.published_events] == [
        event.event_id for event in stored_events
    ]


def test_non_supervisor_role_is_forbidden(api_client: TestClient):
    response = api_client.get("/reports", headers=_professor_headers())
    assert response.status_code == 403

    metrics_response = api_client.get("/pilot/metrics", headers=_professor_headers())
    assert metrics_response.status_code == 403


def test_missing_authentication_is_rejected(api_client: TestClient):
    response = api_client.get("/reports")
    assert response.status_code == 401


def test_blank_cosmos_endpoint_falls_back_to_in_memory(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("INSIGHTS_REPOSITORY", raising=False)
    monkeypatch.setenv("COSMOS_ENDPOINT", "")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(INSIGHTS_SRC) in sys.path:
        sys.path.remove(str(INSIGHTS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(INSIGHTS_SRC))

    for module_name in list(sys.modules):
        if (
            module_name == "app"
            or module_name.startswith("app.")
            or module_name == "tutor_lib.config"
            or module_name.startswith("tutor_lib.config.")
        ):
            sys.modules.pop(module_name, None)

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)
    main_module.get_settings.cache_clear()
    main_module.reset_repository()

    repository = main_module._repository()

    assert isinstance(repository, main_module.InMemoryInsightsRepository)
