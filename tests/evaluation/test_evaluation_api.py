import importlib
import sys
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_SRC = ROOT / "apps" / "evaluation" / "src"
LIB_SRC = ROOT / "lib" / "src"


@pytest.fixture(name="api_client")
def fixture_api_client(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("EVALUATION_REPOSITORY", "memory")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(EVALUATION_SRC) in sys.path:
        sys.path.remove(str(EVALUATION_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(EVALUATION_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)

    main_module.reset_repository()

    return TestClient(main_module.app)


def _auth_headers() -> dict[str, str]:
    return {
        "X-User-Id": "prof-1",
        "X-User-Roles": "professor",
    }


def test_create_dataset_and_native_run_lifecycle(api_client: TestClient):
    dataset_payload = {
        "dataset_id": "dataset-1",
        "name": "Golden Essay Samples",
        "dataset_version": "golden-v1",
        "lineage": {"source": "synthetic", "approved_use": "release-gate"},
        "items": [{"input": "draft", "expected": "feedback"}],
    }
    dataset_response = api_client.post("/datasets", json=dataset_payload, headers=_auth_headers())
    assert dataset_response.status_code == 200
    dataset_body = dataset_response.json()
    assert dataset_body["dataset_id"] == "dataset-1"
    assert dataset_body["dataset_version"] == "golden-v1"
    assert dataset_body["lineage"] == {"source": "synthetic", "approved_use": "release-gate"}

    run_response = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "agent_version": "2026-05-09",
            "dataset_id": "dataset-1",
            "prompt_version": "prompt-v3",
            "thresholds": {"groundedness": 0.85, "safety": 0.95},
            "trace_id": "trace-123",
            "report_uri": "https://reports.example/evaluations/run-1",
            "approval_state": "pending_approval",
            "safety_metrics": {"toxicity": 0.01, "self_harm": 0.0},
        },
        headers=_auth_headers(),
    )
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["agent_name"] == "essay-evaluator"
    assert run_body["agent_version"] == "2026-05-09"
    assert run_body["legacy_agent_id"] is None
    assert run_body["dataset_version"] == "golden-v1"
    assert run_body["prompt_version"] == "prompt-v3"
    assert run_body["thresholds"] == {"groundedness": 0.85, "safety": 0.95}
    assert run_body["trace_id"] == "trace-123"
    assert run_body["report_uri"] == "https://reports.example/evaluations/run-1"
    assert run_body["approval_state"] == "pending_approval"
    assert run_body["safety_metrics"] == {"toxicity": 0.01, "self_harm": 0.0}
    assert run_body["status"] == "queued"
    assert run_body["total_cases"] == 1

    get_run = api_client.get(f"/evaluation/run/{run_body['run_id']}", headers=_auth_headers())
    assert get_run.status_code == 200
    get_run_body = get_run.json()
    assert get_run_body["dataset_id"] == "dataset-1"
    assert get_run_body["agent_name"] == run_body["agent_name"]
    assert get_run_body["thresholds"] == run_body["thresholds"]
    assert get_run_body["approval_state"] == run_body["approval_state"]


def test_legacy_agent_id_run_input_maps_to_native_fields(api_client: TestClient):
    dataset_response = api_client.post(
        "/datasets",
        json={
            "dataset_id": "dataset-legacy",
            "name": "Legacy Compatibility Dataset",
            "items": [{"input": "draft", "expected": "feedback"}],
        },
        headers=_auth_headers(),
    )
    assert dataset_response.status_code == 200

    run_response = api_client.post(
        "/evaluation/run",
        json={"agent_id": "legacy-agent-1", "dataset_id": "dataset-legacy"},
        headers=_auth_headers(),
    )
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["agent_name"] == "legacy-agent-1"
    assert run_body["legacy_agent_id"] == "legacy-agent-1"
    assert run_body["agent_id"] == "legacy-agent-1"
    assert run_body["approval_state"] == "pending_review"

    get_run = api_client.get(f"/evaluation/run/{run_body['run_id']}", headers=_auth_headers())
    assert get_run.status_code == 200
    assert get_run.json()["agent_name"] == "legacy-agent-1"
    assert get_run.json()["legacy_agent_id"] == "legacy-agent-1"


def test_native_run_requires_release_gate_provenance(api_client: TestClient):
    versioned_dataset_response = api_client.post(
        "/datasets",
        json={
            "dataset_id": "dataset-versioned",
            "name": "Versioned Dataset",
            "dataset_version": "golden-v1",
            "items": [{"input": "draft", "expected": "feedback"}],
        },
        headers=_auth_headers(),
    )
    assert versioned_dataset_response.status_code == 200

    missing_agent_version = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "dataset_id": "dataset-versioned",
            "prompt_version": "prompt-v3",
        },
        headers=_auth_headers(),
    )
    assert missing_agent_version.status_code == 422
    assert "agent_version" in missing_agent_version.json()["detail"]

    missing_prompt_version = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "agent_version": "2026-05-09",
            "dataset_id": "dataset-versioned",
        },
        headers=_auth_headers(),
    )
    assert missing_prompt_version.status_code == 422
    assert "prompt_version" in missing_prompt_version.json()["detail"]

    unversioned_dataset_response = api_client.post(
        "/datasets",
        json={
            "dataset_id": "dataset-unversioned",
            "name": "Unversioned Dataset",
            "items": [{"input": "draft", "expected": "feedback"}],
        },
        headers=_auth_headers(),
    )
    assert unversioned_dataset_response.status_code == 200

    missing_dataset_version = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "agent_version": "2026-05-09",
            "dataset_id": "dataset-unversioned",
            "prompt_version": "prompt-v3",
        },
        headers=_auth_headers(),
    )
    assert missing_dataset_version.status_code == 422
    assert "dataset_version" in missing_dataset_version.json()["detail"]

    explicit_native_with_legacy_id = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "agent_id": "essay-evaluator",
            "agent_version": "2026-05-09",
            "dataset_id": "dataset-unversioned",
            "prompt_version": "prompt-v3",
        },
        headers=_auth_headers(),
    )
    assert explicit_native_with_legacy_id.status_code == 422
    assert "dataset_version" in explicit_native_with_legacy_id.json()["detail"]

    supplied_dataset_version = api_client.post(
        "/evaluation/run",
        json={
            "agent_name": "essay-evaluator",
            "agent_version": "2026-05-09",
            "dataset_id": "dataset-unversioned",
            "dataset_version": "request-v1",
            "prompt_version": "prompt-v3",
        },
        headers=_auth_headers(),
    )
    assert supplied_dataset_version.status_code == 200
    assert supplied_dataset_version.json()["dataset_version"] == "request-v1"


def test_run_ids_are_unique_and_uuid_backed(api_client: TestClient):
    dataset_response = api_client.post(
        "/datasets",
        json={
            "dataset_id": "dataset-unique-runs",
            "name": "Unique Run Dataset",
            "dataset_version": "golden-v1",
            "items": [{"input": "draft", "expected": "feedback"}],
        },
        headers=_auth_headers(),
    )
    assert dataset_response.status_code == 200

    run_payload = {
        "agent_name": "essay-evaluator",
        "agent_version": "2026-05-09",
        "dataset_id": "dataset-unique-runs",
        "prompt_version": "prompt-v3",
    }
    run_ids = [
        api_client.post(
            "/evaluation/run",
            json=run_payload,
            headers=_auth_headers(),
        ).json()["run_id"]
        for _ in range(2)
    ]

    assert len(set(run_ids)) == 2
    for run_id in run_ids:
        assert run_id.startswith("run-")
        UUID(run_id.removeprefix("run-"))


def test_run_with_unknown_dataset_returns_404(api_client: TestClient):
    run_response = api_client.post(
        "/evaluation/run",
        json={"agent_name": "agent-1", "dataset_id": "missing"},
        headers=_auth_headers(),
    )
    assert run_response.status_code == 404


@pytest.mark.asyncio
async def test_cosmos_repository_reads_legacy_agent_id_run(api_client: TestClient):
    assert api_client is not None
    store_module = importlib.import_module("app.store")
    cosmos_repository_type = vars(store_module)["CosmosEvaluationRepository"]

    class LegacyRunStore:
        async def read_item(self, run_id: str) -> dict[str, object]:
            return {
                "id": run_id,
                "docType": "run",
                "agent_id": "legacy-agent-cosmos",
                "dataset_id": "dataset-1",
                "status": "queued",
                "total_cases": 3,
            }

    repository = cosmos_repository_type.__new__(cosmos_repository_type)
    object.__setattr__(repository, "_run_store", LegacyRunStore())

    run = await repository.get_run("run-old")

    assert run is not None
    assert run.agent_name == "legacy-agent-cosmos"
    assert run.legacy_agent_id == "legacy-agent-cosmos"
    assert run.dataset_id == "dataset-1"
    assert run.thresholds == {}
    assert run.approval_state == "pending_review"
