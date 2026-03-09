import importlib
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
UPSKILLING_APP = ROOT / "apps" / "upskilling"
LIB_SRC = ROOT / "lib" / "src"
if str(UPSKILLING_APP) not in sys.path:
    sys.path.insert(0, str(UPSKILLING_APP))
if str(LIB_SRC) not in sys.path:
    sys.path.insert(0, str(LIB_SRC))


def _stub_agent_framework_azure():
    for mod_name in (
        "agent_framework_azure_ai",
        "agent_framework_azure_ai._agent_provider",
        "agent_framework_azure_ai._chat_client",
        "agent_framework_azure_ai._shared",
        "agent_framework.azure",
        "agent_framework.azure.ai",
    ):
        if mod_name not in sys.modules:
            sys.modules[mod_name] = types.ModuleType(mod_name)
    af_azure = sys.modules["agent_framework.azure"]
    af_azure.AzureAIAgentClient = MagicMock  # type: ignore[attr-defined]


_PLAN_PAYLOAD = {
    "title": "Test Plan",
    "timeframe": "week",
    "topic": "Physics",
    "class_id": "class-1",
    "paragraphs": [{"title": "Intro", "content": "Start with the basics."}],
    "performance_history": [],
}


@pytest.fixture(name="api_client")
def fixture_api_client(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("UPSKILLING_REPOSITORY", "memory")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(UPSKILLING_APP) in sys.path:
        sys.path.remove(str(UPSKILLING_APP))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(UPSKILLING_APP))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
        if module_name.startswith("tutor_lib.agents"):
            sys.modules.pop(module_name, None)

    _stub_agent_framework_azure()
    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)

    main_module._repository.cache_clear()

    return TestClient(main_module.app)


def _auth_headers() -> dict[str, str]:
    return {
        "X-User-Id": "prof-1",
        "X-User-Roles": "professor",
    }


def _content(response):
    return response.json()["content"]


def test_create_plan_returns_201(api_client):
    r = api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers())
    assert r.status_code == 201
    plan = _content(r)
    assert "id" in plan
    assert plan["status"] == "draft"
    assert plan["professor_id"] == "prof-1"


def test_list_plans_returns_created_plans(api_client):
    api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers())
    api_client.post("/plans", json={**_PLAN_PAYLOAD, "title": "Second Plan"}, headers=_auth_headers())
    r = api_client.get("/plans", headers=_auth_headers())
    assert r.status_code == 200
    plans = _content(r)
    assert len(plans) == 2


def test_get_plan_by_id(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    r = api_client.get(f"/plans/{plan_id}", headers=_auth_headers())
    assert r.status_code == 200
    plan = _content(r)
    assert plan["id"] == plan_id
    assert plan["title"] == _PLAN_PAYLOAD["title"]


def test_get_missing_plan_returns_404(api_client):
    r = api_client.get("/plans/non-existent-id", headers=_auth_headers())
    assert r.status_code == 404


def test_update_plan(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    r = api_client.put(f"/plans/{plan_id}", json={"title": "Updated Title"}, headers=_auth_headers())
    assert r.status_code == 200
    updated = _content(r)
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "draft"


def test_update_evaluated_plan_changes_to_revised(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    api_client.post(f"/plans/{plan_id}/evaluate", headers=_auth_headers())
    r = api_client.put(f"/plans/{plan_id}", json={"title": "Revised Title"}, headers=_auth_headers())
    assert r.status_code == 200
    updated = _content(r)
    assert updated["status"] == "revised"


def test_delete_plan(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    r = api_client.delete(f"/plans/{plan_id}", headers=_auth_headers())
    assert r.status_code == 200
    r = api_client.get(f"/plans/{plan_id}", headers=_auth_headers())
    assert r.status_code == 404


def test_evaluate_persisted_plan(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    r = api_client.post(f"/plans/{plan_id}/evaluate", headers=_auth_headers())
    assert r.status_code == 200
    plan = _content(r)
    assert plan["status"] == "evaluated"
    assert isinstance(plan["evaluations"], list)
    assert len(plan["evaluations"]) > 0


def test_stateless_evaluate_backward_compat(api_client):
    payload = {
        "timeframe": _PLAN_PAYLOAD["timeframe"],
        "topic": _PLAN_PAYLOAD["topic"],
        "class_id": _PLAN_PAYLOAD["class_id"],
        "paragraphs": _PLAN_PAYLOAD["paragraphs"],
        "performance_history": _PLAN_PAYLOAD["performance_history"],
    }
    r = api_client.post("/plan/evaluate", json=payload, headers=_auth_headers())
    assert r.status_code == 200
    result = _content(r)
    assert "evaluations" in result


def test_create_plan_without_auth_returns_401(api_client):
    r = api_client.post("/plans", json=_PLAN_PAYLOAD)
    assert r.status_code == 401
