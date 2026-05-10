"""Tests for Insights P2/P3 governed intelligence APIs."""

import importlib
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
INSIGHTS_SRC = ROOT / "apps" / "insights" / "src"
LIB_SRC = ROOT / "lib" / "src"


@pytest.fixture(name="api_client")
def fixture_api_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("INSIGHTS_REPOSITORY", "memory")
    monkeypatch.setenv("LEARNER_RECORD_PUBLISHER", "noop")
    monkeypatch.setenv("ENTRA_AUTH_ENABLED", "false")

    for source_path in (LIB_SRC, INSIGHTS_SRC):
        if str(source_path) in sys.path:
            sys.path.remove(str(source_path))
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


def _supervisor_headers(learner_ids: str | None = None) -> dict[str, str]:
    headers = {
        "X-User-Id": "supervisor-1",
        "X-User-Roles": "supervisor",
        "X-School-Ids": "school-a",
        "X-Institution-Ids": "tenant-123",
    }
    if learner_ids is not None:
        headers["X-Learner-Ids"] = learner_ids
    return headers


def _principal_headers(learner_ids: str | None = None) -> dict[str, str]:
    headers = {
        "X-User-Id": "principal-1",
        "X-User-Roles": "principal",
        "X-School-Ids": "school-a",
        "X-Institution-Ids": "tenant-123",
    }
    if learner_ids is not None:
        headers["X-Learner-Ids"] = learner_ids
    return headers


def _admin_headers() -> dict[str, str]:
    return {
        "X-User-Id": "admin-1",
        "X-User-Roles": "admin",
        "X-Institution-Ids": "tenant-123",
    }


def _student_headers(user_id: str = "learner-1") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Roles": "student",
        "X-Institution-Ids": "tenant-123",
    }


def _alumni_headers(user_id: str = "learner-1") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Roles": "alumni",
        "X-Institution-Ids": "tenant-123",
    }


def _content(response) -> dict[str, Any]:
    return response.json()["content"]


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_school_unit_intelligence_suppresses_small_cells(api_client: TestClient) -> None:
    response = api_client.get(
        "/school-unit-intelligence",
        params={
            "school_id": "school-a",
            "unit_id": "small-cell-unit",
            "tenant_id": "tenant-123",
        },
        headers=_supervisor_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    suppressed_metric = next(metric for metric in content["metrics"] if metric["status"] == "suppressed")
    assert suppressed_metric["value"] is None
    assert suppressed_metric["suppression"]["reason"] == "small_cell"
    assert content["governance"]["suppression"]["suppressed"] is True
    assert content["governance"]["review"]["required"] is True
    assert content["governance"]["final_decision"] is False


def test_school_unit_intelligence_allows_principal_reader_scope(api_client: TestClient) -> None:
    response = api_client.get(
        "/school-unit-intelligence",
        params={
            "school_id": "school-a",
            "unit_id": "principal-dashboard",
            "tenant_id": "tenant-123",
        },
        headers=_principal_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["school_id"] == "school-a"
    assert content["tenant_id"] == "tenant-123"
    assert content["governance"]["advisory_only"] is True
    assert content["governance"]["final_decision"] is False


def test_causal_study_rejects_missing_required_research_inputs(api_client: TestClient) -> None:
    response = api_client.post(
        "/causal-studies",
        json={
            "school_id": "school-a",
            "tenant_id": "tenant-123",
            "treatment": "weekly tutoring",
        },
        headers=_supervisor_headers(),
    )

    assert response.status_code == 400
    assert response.json()["detail"]["missing_fields"] == [
        "dag",
        "outcome",
        "estimand",
        "population",
        "confounders",
        "refutation_checks",
    ]


def test_causal_study_rejects_principal_research_command(api_client: TestClient) -> None:
    response = api_client.post(
        "/causal-studies",
        json={
            "school_id": "school-a",
            "tenant_id": "tenant-123",
            "dag": "weekly tutoring -> mastery growth",
            "treatment": "weekly tutoring",
            "outcome": "mastery growth",
            "estimand": "average treatment effect of weekly tutoring on mastery growth",
            "population": "grade 8 algebra learners",
            "confounders": ["prior_mastery"],
            "refutation_checks": ["placebo outcome"],
        },
        headers=_principal_headers(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_causal_study_returns_reviewable_report(api_client: TestClient) -> None:
    response = api_client.post(
        "/causal-studies",
        json={
            "school_id": "school-a",
            "tenant_id": "tenant-123",
            "dag": "weekly tutoring -> mastery growth; prior_mastery -> weekly tutoring; prior_mastery -> mastery growth",
            "treatment": "weekly tutoring",
            "outcome": "mastery growth",
            "estimand": "average treatment effect of weekly tutoring on mastery growth",
            "population": "grade 8 algebra learners",
            "confounders": ["prior_mastery", "attendance"],
            "refutation_checks": ["placebo outcome", "negative control exposure"],
        },
        headers=_supervisor_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["estimand"] == "average treatment effect of weekly tutoring on mastery growth"
    assert content["adjustment_set"] == ["prior_mastery", "attendance"]
    assert content["dag_edges"][0] == {"source": "weekly tutoring", "target": "mastery growth"}
    assert content["sensitivity_checks"][0]["target"] == "prior_mastery"
    assert content["refutation_results"][0]["status"] == "needs_review"
    assert content["governance"]["review"]["status"] == "required"
    assert content["governance"]["appeal"]["available"] is True
    assert content["governance"]["advisory_only"] is True


def test_causal_study_accepts_structured_dag_edges(api_client: TestClient) -> None:
    response = api_client.post(
        "/causal-studies",
        json={
            "school_id": "school-a",
            "tenant_id": "tenant-123",
            "dag_edges": [
                {"source": "weekly tutoring", "target": "mastery growth"},
                {"source": "prior mastery", "target": "weekly tutoring"},
            ],
            "treatment": "weekly tutoring",
            "outcome": "mastery growth",
            "estimand": "average treatment effect of weekly tutoring on mastery growth",
            "population": "grade 8 algebra learners",
            "confounders": ["prior mastery"],
            "refutation_checks": ["placebo outcome"],
        },
        headers=_supervisor_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["dag"] == "weekly tutoring -> mastery growth; prior mastery -> weekly tutoring"
    assert content["dag_edges"][0] == {"source": "weekly tutoring", "target": "mastery growth"}


def test_causal_study_rejects_dag_without_treatment_or_outcome(api_client: TestClient) -> None:
    response = api_client.post(
        "/causal-studies",
        json={
            "school_id": "school-a",
            "tenant_id": "tenant-123",
            "dag": "attendance -> engagement",
            "treatment": "weekly tutoring",
            "outcome": "mastery growth",
            "estimand": "average treatment effect of weekly tutoring on mastery growth",
            "population": "grade 8 algebra learners",
            "confounders": ["prior_mastery"],
            "refutation_checks": ["placebo outcome"],
        },
        headers=_supervisor_headers(),
    )

    assert response.status_code == 400
    assert response.json()["detail"]["invalid_fields"] == [
        {"field": "dag", "reason": "treatment must appear in dag or dag_edges"},
        {"field": "dag", "reason": "outcome must appear in dag or dag_edges"},
    ]


def test_conformal_risk_abstains_and_suppresses_label_when_uncertain(api_client: TestClient) -> None:
    response = api_client.get(
        "/conformal-risk/learner-1",
        params={
            "context_id": "student:learner:learner-1",
            "tenant_id": "tenant-123",
            "sample_count": 8,
            "interval_width": 0.5,
        },
        headers=_student_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["abstention"]["abstained"] is True
    assert content["abstention"]["degraded"] is True
    assert content["risks"][0]["risk_label"] is None
    assert content["risks"][0]["score"] is None
    assert content["governance"]["calibration"]["sample_count"] == 8
    assert content["governance"]["coverage"]["minimum_required"] == 30


def test_conformal_risk_rejects_student_access_to_other_learner(api_client: TestClient) -> None:
    response = api_client.get(
        "/conformal-risk/learner-1",
        params={
            "context_id": "student:learner:learner-2",
            "tenant_id": "tenant-123",
        },
        headers=_student_headers(user_id="learner-2"),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("headers", "context_id"),
    [
        (_supervisor_headers(), "supervisor:school:school-a"),
        (_principal_headers(), "principal:school:school-a"),
    ],
)
def test_conformal_risk_rejects_school_only_leader_scope(
    api_client: TestClient,
    headers: dict[str, str],
    context_id: str,
) -> None:
    response = api_client.get(
        "/conformal-risk/learner-1",
        params={
            "context_id": context_id,
            "tenant_id": "tenant-123",
            "school_id": "school-a",
        },
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("headers", "context_id"),
    [
        (_supervisor_headers(learner_ids="learner-1"), "supervisor:school:school-a"),
        (_principal_headers(learner_ids="learner-1"), "principal:school:school-a"),
    ],
)
def test_conformal_risk_allows_explicit_leader_learner_scope(
    api_client: TestClient,
    headers: dict[str, str],
    context_id: str,
) -> None:
    response = api_client.get(
        "/conformal-risk/learner-1",
        params={
            "context_id": context_id,
            "tenant_id": "tenant-123",
            "school_id": "school-a",
        },
        headers=headers,
    )

    assert response.status_code == 200


def test_conformal_risk_allows_admin_scope(api_client: TestClient) -> None:
    response = api_client.get(
        "/conformal-risk/learner-1",
        params={
            "context_id": "admin:institution:tenant-123",
            "tenant_id": "tenant-123",
        },
        headers=_admin_headers(),
    )

    assert response.status_code == 200


def test_lifelong_network_returns_minimized_research_and_portfolio_shape(api_client: TestClient) -> None:
    response = api_client.get(
        "/lifelong-network/learner-1",
        params={
            "context_id": "alumni:learner:learner-1",
            "tenant_id": "tenant-123",
        },
        headers=_alumni_headers(),
    )

    assert response.status_code == 200
    content = _content(response)
    assert content["credentials"][0]["status"] == "active"
    assert content["portfolio_artifacts"][0]["evidence_refs"] == ["evidence:project-rubric"]
    assert content["research_datasets"][0]["de_identified"] is True
    assert content["data_use_agreements"][0]["prohibited_uses"]
    assert content["publication_approvals"][0]["status"] == "review_required"
    assert content["data_minimization"]["direct_identifiers"] == "not_returned"
    assert content["data_minimization"]["learner_scoped_identifiers"] == "present_only_within_learner_authorized_context"
    assert all("email" not in node for node in _walk(content))


def test_lifelong_network_enforces_tenant_scope_when_provided(api_client: TestClient) -> None:
    response = api_client.get(
        "/lifelong-network/learner-1",
        params={
            "context_id": "alumni:learner:learner-1",
            "tenant_id": "tenant-other",
        },
        headers=_alumni_headers(),
    )

    assert response.status_code == 403