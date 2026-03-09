import importlib
import sys
from collections import defaultdict
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
LIB_SRC = ROOT / "lib" / "src"
CONFIG_SRC = ROOT / "apps" / "configuration" / "src"


@pytest.fixture(name="api_client")
def fixture_api_client(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(CONFIG_SRC) in sys.path:
        sys.path.remove(str(CONFIG_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(CONFIG_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)

    from tutor_lib import config as common_config

    common_config.get_settings.cache_clear()

    from app import main

    importlib.reload(main)

    storage: dict[str, dict[str, dict]] = defaultdict(dict)

    class StubRepo:
        def __init__(self, container: str) -> None:
            self._container = container

        async def list_items(self) -> list[dict]:
            return list(storage[self._container].values())

        async def create_item(self, item: dict) -> dict:
            storage[self._container][item["id"]] = item
            return item

        async def read_item(self, item_id: str) -> dict:
            try:
                return storage[self._container][item_id]
            except KeyError as exc:
                raise LookupError("not found") from exc

        async def update_item(self, item_id: str, item: dict) -> dict:
            storage[self._container][item_id] = item
            return item

        async def delete_item(self, item_id: str) -> None:
            storage[self._container].pop(item_id, None)

    def stub_crud(container: str) -> StubRepo:
        return StubRepo(container)

    monkeypatch.setattr(main, "_crud", stub_crud, raising=False)

    return TestClient(main.app)


def _auth_headers() -> dict[str, str]:
    return {"X-User-Id": "prof-1"}


def test_create_and_list_students(api_client: TestClient):
    payload = {"id": "student-1", "name": "Ada", "email": "ada@example.com", "class_id": "class-1"}

    response = api_client.post("/students", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Student Created"
    assert body["content"]["id"] == "student-1"

    listing = api_client.get("/students", headers=_auth_headers())
    assert listing.status_code == 200
    items = listing.json()["content"]
    assert len(items) == 1
    assert items[0]["name"] == "Ada"


def test_assign_cases_to_group(api_client: TestClient):
    group_payload = {
        "id": "group-1",
        "name": "Group A",
        "class_id": "class-1",
        "student_ids": ["student-1"],
    }
    create_response = api_client.post("/groups", json=group_payload, headers=_auth_headers())
    assert create_response.status_code == 200

    assign_response = api_client.post(
        "/groups/group-1/assign-cases",
        json={"case_ids": ["case-1", "case-2"]},
        headers=_auth_headers(),
    )
    assert assign_response.status_code == 200
    updated = assign_response.json()["content"]
    assert updated["assigned_case_ids"] == ["case-1", "case-2"]


def test_bulk_sync_roster(api_client: TestClient):
    payload = {
        "students": [{"id": "student-2", "name": "Lin", "email": "lin@example.com", "class_id": "class-2"}],
        "professors": [{"id": "prof-2", "name": "Prof Lin", "email": "prof.lin@example.com", "courses": []}],
        "courses": [{"id": "course-2", "name": "Literature", "professor_id": "prof-2", "class_ids": []}],
        "classes": [{"id": "class-2", "name": "Class B", "course_id": "course-2", "student_ids": []}],
        "groups": [
            {
                "id": "group-2",
                "name": "Group B",
                "class_id": "class-2",
                "student_ids": ["student-2"],
                "assigned_case_ids": [],
            }
        ],
    }

    response = api_client.post("/lms/bulk-sync", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Bulk Sync Completed"
    assert body["content"] == {
        "students": 1,
        "professors": 1,
        "courses": 1,
        "classes": 1,
        "groups": 1,
    }
