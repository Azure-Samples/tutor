import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
INSIGHTS_SRC = ROOT / "apps" / "insights" / "src"
LIB_SRC = ROOT / "lib" / "src"


@pytest.fixture(name="api_client")
def fixture_api_client(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("INSIGHTS_REPOSITORY", "memory")

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

    return TestClient(main_module.app)


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


def _content(response):
    return response.json()["content"]


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
