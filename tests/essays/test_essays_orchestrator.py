"""Tests for the essay orchestrator using Azure AI Foundry agents."""

# pylint: disable=redefined-outer-name

import importlib
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture
def essays_app_module_fixture(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    monkeypatch.setenv("MODEL_REASONING_DEPLOYMENT", "o3-mini")

    repo_root = Path(__file__).resolve().parents[2]
    essays_root = repo_root / "apps" / "essays"
    if str(essays_root) not in sys.path:
        sys.path.insert(0, str(essays_root))
    essays_src = essays_root / "src"
    if str(essays_src) not in sys.path:
        sys.path.insert(0, str(essays_src))

    from app.config import get_settings  # pylint: disable=import-error

    get_settings.cache_clear()

    import app.essays as essays_app

    importlib.reload(essays_app)
    return essays_app


@pytest.fixture
def essays_main_module_fixture(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    monkeypatch.setenv("MODEL_REASONING_DEPLOYMENT", "o3-mini")

    repo_root = Path(__file__).resolve().parents[2]
    essays_src = repo_root / "apps" / "essays" / "src"
    lib_src = repo_root / "lib" / "src"

    for entry in (str(essays_src), str(lib_src)):
        if entry not in sys.path:
            sys.path.insert(0, entry)

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)
    return main_module


DEFAULT_RESPONSE = "Overall verdict\n\nStrengths: Solid thesis\n\nImprovements: Tighten conclusion"


class _StubFoundryAgentService:
    response_text = DEFAULT_RESPONSE

    def __init__(self, *_args, **_kwargs):
        self.calls: list[tuple[str, str]] = []

    async def run_agent(self, agent_id: str, prompt: str, **kwargs) -> str:
        self.calls.append((agent_id, prompt))
        return self.response_text


class _FakeCredential:  # noqa: D401 - simple stub credential
    pass


@pytest.mark.asyncio
async def test_orchestrator_uses_default_strategy(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    monkeypatch.setattr(module, "FoundryAgentService", _StubFoundryAgentService)
    _StubFoundryAgentService.response_text = DEFAULT_RESPONSE
    monkeypatch.setattr(module, "DefaultAzureCredential", _FakeCredential)

    provisioned = module.ProvisionedAgent(
        id="agent-default",
        name="General Reviewer",
        instructions="Provide general feedback",
        deployment="gpt-4o",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Swarm(id=assembly_id, topic_name="Topic", essay_id="essay-1", agents=[provisioned])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_swarm", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-1", topic="History", content="Text")
    result = await orchestrator.invoke("assembly-1", essay, [])

    assert result.strategy is module.EssayStrategyType.DEFAULT
    assert result.strengths == ["Solid thesis"]
    assert result.improvements == ["Tighten conclusion"]


@pytest.mark.asyncio
async def test_orchestrator_uses_narrative_strategy(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    monkeypatch.setattr(module, "FoundryAgentService", _StubFoundryAgentService)
    _StubFoundryAgentService.response_text = (
        "Narrative verdict\n\nStrengths: Vivid imagery\n\nImprovements: Clarify ending"
    )
    monkeypatch.setattr(module, "DefaultAzureCredential", _FakeCredential)

    narrative_agent = module.ProvisionedAgent(
        id="agent-narrative",
        name="Narrative Coach",
        instructions="Support creative storytelling",
        deployment="gpt-4o",
    )
    default_agent = module.ProvisionedAgent(
        id="agent-default",
        name="General Reviewer",
        instructions="Provide general feedback",
        deployment="gpt-4o",
    )

    async def _stub_load(_self, assembly_id, **kwargs):  # pragma: no cover - monkeypatched helper
        return module.Swarm(id=assembly_id, topic_name="Topic", essay_id="essay-2", agents=[default_agent, narrative_agent])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_swarm", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-2", topic="Literature", content="Story")
    resources = [
        module.Resource(
            id="res-1",
            essay_id="essay-2",
            objective=["Creative expression"],
        )
    ]
    result = await orchestrator.invoke("assembly-2", essay, resources)

    assert result.strategy is module.EssayStrategyType.NARRATIVE
    assert "Narrative verdict" in result.verdict


@pytest.mark.asyncio
async def test_orchestrator_uses_analytical_strategy_for_theme(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    monkeypatch.setattr(module, "FoundryAgentService", _StubFoundryAgentService)
    _StubFoundryAgentService.response_text = (
        "Analytical verdict\n\nStrengths: Rigorous evidence\n\nImprovements: Expand counterpoints"
    )
    monkeypatch.setattr(module, "DefaultAzureCredential", _FakeCredential)

    analytical_agent = module.ProvisionedAgent(
        id="agent-analytical",
        name="Analytical Reviewer",
        instructions="Analyse evidence",
        deployment="o3-mini",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Swarm(id=assembly_id, topic_name="Topic", essay_id="essay-3", agents=[analytical_agent])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_swarm", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-3", topic="Science", content="Analysis", theme="Analytical Essay")
    result = await orchestrator.invoke("assembly-3", essay, [])

    assert result.strategy is module.EssayStrategyType.ANALYTICAL
    assert result.strengths == ["Rigorous evidence"]


class _StubContainer:
    def __init__(self, existing_ids, not_found):
        self._existing_ids = set(existing_ids)
        self._not_found = not_found

    async def read_item(self, item, partition_key):
        if item not in self._existing_ids or partition_key not in self._existing_ids:
            raise self._not_found("missing")
        return {
            "id": item,
            "topic_name": "Topic",
            "essay_id": "essay-stub",
            "agents": [
                {
                    "id": "agent-1",
                    "name": "General Reviewer",
                    "instructions": "Review essays",
                    "deployment": "gpt-4o",
                    "temperature": 0.2,
                }
            ],
        }


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
async def test_load_swarm_raises_for_missing_assembly(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    not_found = type("NotFound", (Exception,), {})

    def _client_factory(*_args, **_kwargs):
        return _StubCosmosClient(existing_ids=set(), not_found=not_found)

    monkeypatch.setattr(module, "FoundryAgentService", _StubFoundryAgentService)
    monkeypatch.setattr(module, "DefaultAzureCredential", _FakeCredential)
    monkeypatch.setattr(module, "CosmosClient", _client_factory)
    monkeypatch.setattr(module.exceptions, "CosmosResourceNotFoundError", not_found)

    orchestrator = module.EssayOrchestrator()
    essay = module.Essay(id="essay-missing", topic="History", content="Text")

    with pytest.raises(ValueError):
        await orchestrator.invoke("assembly-missing", essay, [])


@pytest.mark.asyncio
async def test_load_swarm_returns_agents(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    not_found = type("NotFound", (Exception,), {})

    def _client_factory(*_args, **_kwargs):
        return _StubCosmosClient(existing_ids={"assembly-present"}, not_found=not_found)

    created: list[_StubFoundryAgentService] = []

    class _RecordingService(_StubFoundryAgentService):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)

    monkeypatch.setattr(module, "FoundryAgentService", _RecordingService)
    _StubFoundryAgentService.response_text = DEFAULT_RESPONSE
    monkeypatch.setattr(module, "DefaultAzureCredential", _FakeCredential)
    monkeypatch.setattr(module, "CosmosClient", _client_factory)
    monkeypatch.setattr(module.exceptions, "CosmosResourceNotFoundError", not_found)

    orchestrator = module.EssayOrchestrator()
    essay = module.Essay(id="essay-present", topic="History", content="Text")

    await orchestrator.invoke("assembly-present", essay, [])
    assert created[0].calls[0][0] == "agent-1"


def test_prepare_resources_prefers_doc_intelligence(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    orchestrator = module.EssayOrchestrator()

    monkeypatch.setattr(module, "extract_text_with_doc_intelligence", lambda *_args, **_kwargs: "di text")
    monkeypatch.setattr(
        module,
        "extract_pdf_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("pypdf fallback should not be called")),
    )

    resource = module.Resource(
        id="res-ocr",
        essay_id="essay-ocr",
        objective=["objective"],
        content_type="application/pdf",
        encoded_content="dGVzdA==",  # base64("test")
    )

    prepared = orchestrator._prepare_resources([resource])

    assert prepared[0].content == "di text"


def test_prepare_resources_falls_back_to_pdf_extraction(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    orchestrator = module.EssayOrchestrator()

    monkeypatch.setattr(module, "extract_text_with_doc_intelligence", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "extract_pdf_text", lambda *_args, **_kwargs: "fallback text")

    resource = module.Resource(
        id="res-fallback",
        essay_id="essay-fallback",
        objective=["objective"],
        content_type="application/pdf",
        encoded_content="dGVzdA==",  # base64("test")
    )

    prepared = orchestrator._prepare_resources([resource])

    assert prepared[0].content == "fallback text"


@pytest.mark.asyncio
async def test_grader_interaction_accepts_essay_id(monkeypatch, essays_main_module_fixture):
    module = essays_main_module_fixture

    async def _stub_get_essay_document(_essay_id: str):
        return {"id": "essay-42", "assembly_id": "asm-42"}

    class _StubOrchestrator:
        def __init__(self):
            self.calls = []

        async def invoke(self, assembly_id, essay, resources):
            self.calls.append((assembly_id, essay.id, len(resources)))
            return type(
                "Result",
                (),
                {
                    "strategy": type("Strategy", (), {"value": "default"})(),
                    "verdict": "Structured verdict",
                    "strengths": ["Strong structure"],
                    "improvements": ["Add evidence"],
                },
            )()

    orchestrator = _StubOrchestrator()
    monkeypatch.setattr(module, "_get_essay_document", _stub_get_essay_document)
    monkeypatch.setattr(module, "orchestrator", orchestrator)

    payload = module.ChatResponse(
        case_id="essay-42",
        essay=module.Essay(id="essay-42", topic="Topic", content="Essay text"),
        resources=[],
    )

    response = await module.grader_interaction(payload)
    body = json.loads(response.body)

    assert response.status_code == 200
    assert orchestrator.calls[0][0] == "asm-42"
    assert body["strategy"] == "default"


@pytest.mark.asyncio
async def test_grader_interaction_returns_400_for_unresolved_case_id(monkeypatch, essays_main_module_fixture):
    module = essays_main_module_fixture

    async def _stub_get_essay_document(_essay_id: str):
        return {"id": "essay-without-assembly", "assembly_id": None}

    monkeypatch.setattr(module, "_get_essay_document", _stub_get_essay_document)

    payload = module.ChatResponse(
        case_id="essay-without-assembly",
        essay=module.Essay(id="essay-without-assembly", topic="Topic", content="Essay text"),
        resources=[],
    )

    with pytest.raises(module.HTTPException) as exc_info:
        await module.grader_interaction(payload)

    assert exc_info.value.status_code == 400
    assert "not linked to an assembly" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_grader_interaction_returns_fallback_when_orchestrator_fails(
    monkeypatch, essays_main_module_fixture
):
    module = essays_main_module_fixture

    async def _stub_get_essay_document(_essay_id: str):
        return None

    class _FailingOrchestrator:
        async def invoke(self, _assembly_id, _essay, _resources):
            raise RuntimeError("RunStatus.FAILED")

    monkeypatch.setattr(module, "_get_essay_document", _stub_get_essay_document)
    monkeypatch.setattr(module, "orchestrator", _FailingOrchestrator())

    payload = module.ChatResponse(
        case_id="assembly-123",
        essay=module.Essay(id="essay-123", topic="Topic", content="Essay text"),
        resources=[],
    )

    response = await module.grader_interaction(payload)
    body = json.loads(response.body)

    assert response.status_code == 200
    assert body["strategy"] == "default"
    assert body["verdict"].strip()
    assert body["strengths"]
    assert body["improvements"]