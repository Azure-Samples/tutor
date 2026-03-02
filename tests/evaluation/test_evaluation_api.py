import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
EVALUATION_SRC = ROOT / "apps" / "evaluation" / "src"
LIB_SRC = ROOT / "lib" / "src"
if str(EVALUATION_SRC) not in sys.path:
    sys.path.insert(0, str(EVALUATION_SRC))
if str(LIB_SRC) not in sys.path:
    sys.path.insert(0, str(LIB_SRC))


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


def test_create_dataset_and_run_lifecycle(api_client: TestClient):
    dataset_payload = {
        "dataset_id": "dataset-1",
        "name": "Golden Essay Samples",
        "items": [{"input": "draft", "expected": "feedback"}],
    }
    dataset_response = api_client.post("/datasets", json=dataset_payload, headers=_auth_headers())
    assert dataset_response.status_code == 200
    assert dataset_response.json()["dataset_id"] == "dataset-1"

    run_response = api_client.post(
        "/evaluation/run",
        json={"agent_id": "agent-1", "dataset_id": "dataset-1"},
        headers=_auth_headers(),
    )
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["status"] == "queued"
    assert run_body["total_cases"] == 1

    get_run = api_client.get(f"/evaluation/run/{run_body['run_id']}", headers=_auth_headers())
    assert get_run.status_code == 200
    assert get_run.json()["dataset_id"] == "dataset-1"


def test_run_with_unknown_dataset_returns_404(api_client: TestClient):
    run_response = api_client.post(
        "/evaluation/run",
        json={"agent_id": "agent-1", "dataset_id": "missing"},
        headers=_auth_headers(),
    )
    assert run_response.status_code == 404
