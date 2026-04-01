import importlib
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
AVATAR_SRC = ROOT / "apps" / "avatar" / "src"
LIB_SRC = ROOT / "lib" / "src"


def _install_tutor_lib_agents_stub() -> None:
    agents_module = types.ModuleType("tutor_lib.agents")

    class _AgentSpec:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

    class _AgentRegistry:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def create(self, _spec):
            return object()

    class _AgentRunContext:
        def __init__(self, _agent) -> None:
            pass

        async def run(self, _prompt: str):
            return SimpleNamespace(text="stub-avatar-response")

    agents_module.AgentSpec = _AgentSpec
    agents_module.AgentRegistry = _AgentRegistry
    agents_module.AgentRunContext = _AgentRunContext
    sys.modules["tutor_lib.agents"] = agents_module


@pytest.fixture(name="avatar_main_module")
def fixture_avatar_main_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-5-nano")
    monkeypatch.setenv("ENTRA_AUTH_ENABLED", "false")

    if str(LIB_SRC) in sys.path:
        sys.path.remove(str(LIB_SRC))
    if str(AVATAR_SRC) in sys.path:
        sys.path.remove(str(AVATAR_SRC))
    sys.path.insert(0, str(LIB_SRC))
    sys.path.insert(0, str(AVATAR_SRC))

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app.") or module_name == "tutor_lib.agents":
            sys.modules.pop(module_name, None)

    _install_tutor_lib_agents_stub()

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)
    return main_module


class _AvatarOrchestratorStub:
    def __init__(self) -> None:
        self.calls = []

    async def respond(self, params):
        self.calls.append(params)
        return "stubbed-avatar-answer"


class _SpeechBrokerStub:
    async def create_session(self):
        return SimpleNamespace(
            authorization_token="aad#/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/speech#token",
            region="eastus",
            expires_on=1735689600,
            relay={"Urls": ["turn:relay.example.com"], "Username": "relay-user", "Password": "relay-pass"},
        )


def test_avatar_response_uses_orchestrator_stub(avatar_main_module, monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _AvatarOrchestratorStub()
    monkeypatch.setattr(avatar_main_module, "_avatar", lambda: stub)
    client = TestClient(avatar_main_module.app)

    response = client.post(
        "/response",
        json={"case_id": "case-123", "prompt": "How can I improve my introduction?", "chat_history": []},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "stubbed-avatar-answer"}
    assert len(stub.calls) == 1
    assert stub.calls[0].case_id == "case-123"
    assert stub.calls[0].prompt == "How can I improve my introduction?"


def test_speech_session_token_returns_stubbed_realtime_payload(
    avatar_main_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(avatar_main_module, "_speech_broker", lambda: _SpeechBrokerStub())
    client = TestClient(avatar_main_module.app)

    response = client.get("/speech/session-token")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Speech Session Token Retrieved"
    assert payload["message"] == "Speech session token fetched"
    assert payload["content"]["authorizationToken"].startswith("aad#")
    assert payload["content"]["region"] == "eastus"
    assert payload["content"]["expiresOn"] == 1735689600
    assert payload["content"]["relay"]["Username"] == "relay-user"
