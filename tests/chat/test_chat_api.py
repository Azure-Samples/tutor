import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
CHAT_SRC = ROOT / "apps" / "chat" / "src"
LIB_SRC = ROOT / "lib" / "src"


@pytest.fixture(name="chat_client")
def fixture_chat_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ENTRA_AUTH_ENABLED", "false")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(CHAT_SRC) in sys.path:
        sys.path.remove(str(CHAT_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(CHAT_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)

    return TestClient(main_module.app)


def test_guide_returns_tutoring_guidance(chat_client: TestClient) -> None:
    response = chat_client.post(
        "/guide",
        json={
            "student_id": "student-1",
            "course_id": "course-1",
            "message": "How do I structure my thesis paragraph?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["student_id"] == "student-1"
    assert payload["course_id"] == "course-1"
    assert payload["prompt"] == "How do I structure my thesis paragraph?"
    assert isinstance(payload["guidance"], str)


def test_guide_rejects_empty_prompt_and_message(chat_client: TestClient) -> None:
    response = chat_client.post(
        "/guide",
        json={
            "student_id": "student-1",
            "course_id": "course-1",
            "prompt": "   ",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Either 'prompt' or 'message' is required"}
