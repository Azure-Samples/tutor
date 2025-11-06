import importlib
import types

import pytest


@pytest.fixture
def essays_module(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    monkeypatch.setenv("MODEL_REASONING_DEPLOYMENT", "o3-mini")

    from common import config as common_config

    common_config.get_settings.cache_clear()

    import essays.app.essays as essays_app

    importlib.reload(essays_app)
    return essays_app


class _StubAgentRegistry:
    def __init__(self, *_args, **_kwargs):
        self.specs = []

    def create(self, spec):
        self.specs.append(spec)
        return types.SimpleNamespace(get_new_thread=lambda: "thread-id")


class _StubRunContext:
    def __init__(self, *_args, **_kwargs):
        pass

    async def run(self, *_args, **_kwargs):
        return types.SimpleNamespace(
            text="Overall verdict\n\nStrengths: Solid thesis\n\nImprovements: Tighten conclusion"
        )


@pytest.mark.asyncio
async def test_orchestrator_uses_default_strategy(monkeypatch, essays_module):
    monkeypatch.setattr(essays_module, "AgentRegistry", _StubAgentRegistry)
    monkeypatch.setattr(essays_module, "AgentRunContext", _StubRunContext)
    monkeypatch.setattr(essays_module, "DefaultAzureCredential", lambda: object())

    async def _stub_ensure(self, assembly_id):
        self._checked = assembly_id

    monkeypatch.setattr(essays_module.EssayOrchestrator, "_ensure_assembly_exists", _stub_ensure, raising=False)

    orchestrator = essays_module.EssayOrchestrator()

    essay = essays_module.Essay(id="essay-1", topic="History", content="Text")
    result = await orchestrator.invoke("assembly-1", essay, [])

    assert result.strategy is essays_module.EssayStrategyType.DEFAULT
    assert result.strengths == ["Solid thesis"]
    assert result.improvements == ["Tighten conclusion"]


class _NarrativeRunContext(_StubRunContext):
    async def run(self, *_args, **_kwargs):
        return types.SimpleNamespace(
            text="Narrative verdict\n\nStrengths: Vivid imagery\n\nImprovements: Clarify ending"
        )


@pytest.mark.asyncio
async def test_orchestrator_uses_narrative_strategy(monkeypatch, essays_module):
    monkeypatch.setattr(essays_module, "AgentRegistry", _StubAgentRegistry)
    monkeypatch.setattr(essays_module, "AgentRunContext", _NarrativeRunContext)
    monkeypatch.setattr(essays_module, "DefaultAzureCredential", lambda: object())

    async def _stub_ensure(self, assembly_id):  # pragma: no cover - monkeypatched helper
        self._checked = assembly_id

    monkeypatch.setattr(essays_module.EssayOrchestrator, "_ensure_assembly_exists", _stub_ensure, raising=False)

    orchestrator = essays_module.EssayOrchestrator()

    essay = essays_module.Essay(id="essay-2", topic="Literature", content="Story")
    resources = [
        essays_module.Resource(
            id="res-1",
            essay_id="essay-2",
            objective=["Creative expression"],
        )
    ]
    result = await orchestrator.invoke("assembly-2", essay, resources)

    assert result.strategy is essays_module.EssayStrategyType.NARRATIVE
    assert "Narrative verdict" in result.verdict


class _AnalyticalRunContext(_StubRunContext):
    async def run(self, *_args, **_kwargs):
        return types.SimpleNamespace(
            text="Analytical verdict\n\nStrengths: Rigorous evidence\n\nImprovements: Expand counterpoints"
        )


@pytest.mark.asyncio
async def test_orchestrator_uses_analytical_strategy_for_theme(monkeypatch, essays_module):
    monkeypatch.setattr(essays_module, "AgentRegistry", _StubAgentRegistry)
    monkeypatch.setattr(essays_module, "AgentRunContext", _AnalyticalRunContext)
    monkeypatch.setattr(essays_module, "DefaultAzureCredential", lambda: object())

    async def _stub_ensure(self, assembly_id):
        self._checked = assembly_id

    monkeypatch.setattr(essays_module.EssayOrchestrator, "_ensure_assembly_exists", _stub_ensure, raising=False)

    orchestrator = essays_module.EssayOrchestrator()

    essay = essays_module.Essay(id="essay-3", topic="Science", content="Analysis", theme="Analytical Essay")
    result = await orchestrator.invoke("assembly-3", essay, [])

    assert result.strategy is essays_module.EssayStrategyType.ANALYTICAL
    assert result.strengths == ["Rigorous evidence"]


class _StubContainer:
    def __init__(self, existing_ids, not_found):
        self._existing_ids = set(existing_ids)
        self._not_found = not_found

    async def read_item(self, item, partition_key):
        if item not in self._existing_ids or partition_key not in self._existing_ids:
            raise self._not_found("missing")
        return {"id": item}


class _StubDatabase:
    def __init__(self, existing_ids, not_found):
        self._existing_ids = existing_ids
        self._not_found = not_found

    async def read(self):
        return None

    def get_container_client(self, _name):
        return _StubContainer(self._existing_ids, self._not_found)


class _StubCosmosClient:
    def __init__(self, existing_ids, not_found):
        self._database = _StubDatabase(existing_ids, not_found)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def get_database_client(self, _name):
        return self._database


@pytest.mark.asyncio
async def test_ensure_assembly_exists_raises(monkeypatch, essays_module):
    not_found = type("NotFound", (Exception,), {})

    def _client_factory(*_args, **_kwargs):
        return _StubCosmosClient(existing_ids=set(), not_found=not_found)

    monkeypatch.setattr(essays_module, "AgentRegistry", _StubAgentRegistry)
    monkeypatch.setattr(essays_module, "AgentRunContext", _StubRunContext)
    monkeypatch.setattr(essays_module, "DefaultAzureCredential", lambda: object())
    monkeypatch.setattr(essays_module, "CosmosClient", _client_factory)
    monkeypatch.setattr(essays_module.exceptions, "CosmosResourceNotFoundError", not_found)

    orchestrator = essays_module.EssayOrchestrator()

    with pytest.raises(ValueError):
        await orchestrator._ensure_assembly_exists("assembly-missing")


@pytest.mark.asyncio
async def test_ensure_assembly_exists_succeeds(monkeypatch, essays_module):
    not_found = type("NotFound", (Exception,), {})

    def _client_factory(*_args, **_kwargs):
        return _StubCosmosClient(existing_ids={"assembly-present"}, not_found=not_found)

    monkeypatch.setattr(essays_module, "AgentRegistry", _StubAgentRegistry)
    monkeypatch.setattr(essays_module, "AgentRunContext", _StubRunContext)
    monkeypatch.setattr(essays_module, "DefaultAzureCredential", lambda: object())
    monkeypatch.setattr(essays_module, "CosmosClient", _client_factory)
    monkeypatch.setattr(essays_module.exceptions, "CosmosResourceNotFoundError", not_found)

    orchestrator = essays_module.EssayOrchestrator()

    await orchestrator._ensure_assembly_exists("assembly-present")