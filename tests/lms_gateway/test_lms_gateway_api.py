import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
LMS_SRC = ROOT / "apps" / "lms-gateway" / "src"
LIB_SRC = ROOT / "lib" / "src"


def _set_required_env() -> None:
    import os

    os.environ["COSMOS_ENDPOINT"] = "https://localhost:8081/"
    os.environ["COSMOS_DATABASE"] = "unit-test-db"
    os.environ["PROJECT_ENDPOINT"] = "https://fake-endpoint.azure.com/"
    os.environ["LMS_JOB_STORE"] = "memory"


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


def test_lms_sync_for_moodle_completes():
    _set_required_env()
    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(LMS_SRC) in sys.path:
        sys.path.remove(str(LMS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    from app import main

    importlib.reload(main)
    client = TestClient(main.app)

    response = client.post("/lms/sync", json={"adapter": "moodle"}, headers=_admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["adapter"] == "moodle"
    assert body["status"] == "completed"


def test_lms_sync_unknown_adapter_returns_400():
    _set_required_env()
    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(LMS_SRC) in sys.path:
        sys.path.remove(str(LMS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    from app import main

    importlib.reload(main)
    client = TestClient(main.app)

    response = client.post("/lms/sync", json={"adapter": "unknown"}, headers=_admin_headers())
    assert response.status_code == 400


def test_lms_sync_schedule_returns_next_run():
    _set_required_env()
    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(LMS_SRC) in sys.path:
        sys.path.remove(str(LMS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    from app import main

    importlib.reload(main)
    client = TestClient(main.app)

    response = client.post(
        "/lms/sync/schedule",
        json={"adapter": "canvas", "interval_minutes": 30},
        headers=_admin_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "scheduled"
    assert body["adapter"] == "canvas"
    assert body["job_id"]

    status_response = client.get(f"/lms/sync/jobs/{body['job_id']}", headers=_professor_headers())
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["job_id"] == body["job_id"]
    assert status_body["adapter"] == "canvas"


def test_lms_sync_job_unknown_returns_404():
    _set_required_env()
    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(LMS_SRC) in sys.path:
        sys.path.remove(str(LMS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    from app import main

    importlib.reload(main)
    client = TestClient(main.app)

    response = client.get("/lms/sync/jobs/missing", headers=_professor_headers())
    assert response.status_code == 404


def test_lms_sync_schedule_rejects_invalid_interval():
    _set_required_env()
    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(LMS_SRC) in sys.path:
        sys.path.remove(str(LMS_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(LMS_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)
    from app import main

    importlib.reload(main)
    client = TestClient(main.app)

    response = client.post(
        "/lms/sync/schedule",
        json={"adapter": "canvas", "interval_minutes": 0},
        headers=_admin_headers(),
    )
    assert response.status_code == 400
