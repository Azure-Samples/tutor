import importlib
from collections import defaultdict

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")

    from common import config as common_config

    common_config.get_settings.cache_clear()

    from configuration.app import main

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
                raise Exception("not found") from exc

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


def test_create_and_list_students(client: TestClient):
    payload = {"id": "student-1", "name": "Ada", "email": "ada@example.com", "class_id": "class-1"}

    response = client.post("/students", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Student Created"
    assert body["content"]["id"] == "student-1"

    listing = client.get("/students", headers=_auth_headers())
    assert listing.status_code == 200
    items = listing.json()["content"]
    assert len(items) == 1
    assert items[0]["name"] == "Ada"


def test_assign_cases_to_group(client: TestClient):
    group_payload = {
        "id": "group-1",
        "name": "Group A",
        "class_id": "class-1",
        "student_ids": ["student-1"],
    }
    create_response = client.post("/groups", json=group_payload, headers=_auth_headers())
    assert create_response.status_code == 200

    assign_response = client.post(
        "/groups/group-1/assign-cases",
        json={"case_ids": ["case-1", "case-2"]},
        headers=_auth_headers(),
    )
    assert assign_response.status_code == 200
    updated = assign_response.json()["content"]
    assert updated["assigned_case_ids"] == ["case-1", "case-2"]
