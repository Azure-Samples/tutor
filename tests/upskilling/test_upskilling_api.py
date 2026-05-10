import importlib
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
UPSKILLING_APP = ROOT / "apps" / "upskilling"
LIB_SRC = ROOT / "lib" / "src"


def _install_tutor_lib_agents_stub() -> None:
    agents_module = types.ModuleType("tutor_lib.agents")

    class _AgentReference:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

    class _AgentInvocationRequest:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

    class _FoundryAgentFacade:
        def __init__(self, *_args, **_kwargs) -> None:
            self.requests = []

        async def invoke(self, request):
            self.requests.append(request)
            return SimpleNamespace(
                output_text=(
                    "Well-structured teaching move.\n\n"
                    "Strengths: Clear topic framing.\n\n"
                    "Improvements: Add a formative check."
                )
            )

    agents_module.AgentReference = _AgentReference
    agents_module.AgentInvocationRequest = _AgentInvocationRequest
    agents_module.FoundryAgentFacade = _FoundryAgentFacade
    sys.modules["tutor_lib.agents"] = agents_module


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

    _install_tutor_lib_agents_stub()
    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)

    main_module.reset_repository()

    return TestClient(main_module.app)


def _auth_headers(user_id: str = "prof-1", roles: str = "professor") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Roles": roles,
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


@pytest.mark.parametrize(
    ("method", "path_suffix", "json_payload"),
    [
        ("get", "", None),
        ("put", "", {"title": "Unauthorized Update"}),
        ("delete", "", None),
        ("post", "/evaluate", None),
        ("post", "/advisory-training-plan", None),
    ],
)
def test_plan_id_routes_reject_other_professor(api_client, method, path_suffix, json_payload):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]
    request = getattr(api_client, method)
    kwargs = {"headers": _auth_headers(user_id="prof-2")}
    if json_payload is not None:
        kwargs["json"] = json_payload

    response = request(f"/plans/{plan_id}{path_suffix}", **kwargs)

    assert response.status_code == 403
    owner_response = api_client.get(f"/plans/{plan_id}", headers=_auth_headers())
    assert owner_response.status_code == 200


def test_admin_can_read_other_professors_plan(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))

    response = api_client.get(
        f"/plans/{created['id']}",
        headers=_auth_headers(user_id="admin-1", roles="admin"),
    )

    assert response.status_code == 200


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


def test_advisory_training_plan_is_draft_reviewable_and_persisted(api_client):
    created = _content(api_client.post("/plans", json=_PLAN_PAYLOAD, headers=_auth_headers()))
    plan_id = created["id"]

    r = api_client.post(f"/plans/{plan_id}/advisory-training-plan", headers=_auth_headers())

    assert r.status_code == 200
    plan = _content(r)
    advisory = plan["advisory_training_plan"]
    assert plan["status"] == "draft"
    assert advisory["status"] == "draft"
    assert advisory["human_review_required"] is True
    assert advisory["governance"]["review"]["status"] == "required"
    assert advisory["governance"]["appeal"]["available"] is True
    assert advisory["governance"]["uncertainty"]["wide"] is True
    assert advisory["governance"]["advisory_only"] is True
    assert advisory["governance"]["final_decision"] is False

    persisted = _content(api_client.get(f"/plans/{plan_id}", headers=_auth_headers()))
    assert persisted["advisory_training_plan"]["plan_id"] == plan_id


def test_create_plan_without_auth_returns_401(api_client):
    r = api_client.post("/plans", json=_PLAN_PAYLOAD)
    assert r.status_code == 401
