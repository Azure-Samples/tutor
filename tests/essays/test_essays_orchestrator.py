"""Tests for the essay orchestrator using Azure AI Foundry agents."""

# pylint: disable=redefined-outer-name

import importlib
import json
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


def _install_tutor_lib_agents_stub() -> None:
    """Inject a lightweight tutor_lib.agents module for unit-test imports."""

    agents_module = types.ModuleType("tutor_lib.agents")

    @dataclass(frozen=True)
    class _ImportSafeAgentReference:
        agent_name: str
        agent_version: str | None = None
        role: str | None = None
        dimension: str | None = None
        model_provider: str | None = None
        model_name: str | None = None
        prompt_version: str | None = None
        governance_state: str | None = None
        legacy_agent_id: str | None = None
        metadata: dict[str, Any] = field(default_factory=dict)

        @property
        def id(self) -> str:
            return self.legacy_agent_id or self.agent_name

        @property
        def model(self) -> str | None:
            return self.model_name

        @property
        def model_id(self) -> str | None:
            return self.model_name

        @property
        def deployment_name(self) -> str | None:
            return self.model_name

    @dataclass(frozen=True)
    class _ImportSafeAgentAttachment:
        file_name: str
        content_type: str
        payload: bytes
        purpose: str = "assistants"
        tool_type: str = "vision"

    @dataclass(frozen=True)
    class _ImportSafeAgentInvocationRequest:
        agent: _ImportSafeAgentReference
        input: str
        context: dict[str, Any] = field(default_factory=dict)
        conversation_id: str | None = None
        previous_invocation_id: str | None = None
        attachments: tuple[_ImportSafeAgentAttachment, ...] = field(default_factory=tuple)
        store: bool = False
        stream: bool = False
        background: bool = False
        evidence_refs: tuple[str, ...] = field(default_factory=tuple)
        metadata: dict[str, Any] = field(default_factory=dict)

    @dataclass(frozen=True)
    class _ImportSafeAgentInvocationResult:
        output_text: str
        agent: _ImportSafeAgentReference
        store: bool = False

    class _ImportSafeFoundryAgentFacade:
        def __init__(self, *_args, **_kwargs) -> None:
            self.requests: list[_ImportSafeAgentInvocationRequest] = []

        async def invoke(self, request: _ImportSafeAgentInvocationRequest) -> _ImportSafeAgentInvocationResult:
            self.requests.append(request)
            return _ImportSafeAgentInvocationResult(
                output_text="stub response",
                agent=request.agent,
                store=request.store,
            )

        async def create_agent(self, **_kwargs):
            return _ImportSafeAgentReference(
                agent_name="agent-stub",
                legacy_agent_id="agent-stub-id",
                model_name=_kwargs.get("deployment"),
            )

        async def get_agent(self, agent_id: str):
            return _ImportSafeAgentReference(
                agent_name=agent_id,
                legacy_agent_id=agent_id,
                model_name="gpt-5-nano",
            )

        async def list_agents(self, *, limit: int | None = None):
            agents = [
                _ImportSafeAgentReference(
                    agent_name="agent-stub",
                    legacy_agent_id="agent-stub-id",
                    model_name="gpt-5-nano",
                )
            ]
            return agents[:limit] if limit else agents

    agents_module.AgentReference = _ImportSafeAgentReference
    agents_module.AgentAttachment = _ImportSafeAgentAttachment
    agents_module.AgentInvocationRequest = _ImportSafeAgentInvocationRequest
    agents_module.AgentInvocationResult = _ImportSafeAgentInvocationResult
    agents_module.FoundryAgentFacade = _ImportSafeFoundryAgentFacade
    agents_module.FoundryAgentService = _ImportSafeFoundryAgentFacade
    sys.modules["tutor_lib.agents"] = agents_module


def _install_document_intelligence_stub() -> None:
    """Provide azure.ai.documentintelligence when the SDK is unavailable locally."""

    module = types.ModuleType("azure.ai.documentintelligence")

    class _Poller:
        @staticmethod
        def result():
            return types.SimpleNamespace(content="", pages=[])

    class _DocumentIntelligenceClient:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def begin_analyze_document(self, **_kwargs):
            return _Poller()

    module.DocumentIntelligenceClient = _DocumentIntelligenceClient
    sys.modules["azure.ai.documentintelligence"] = module


@pytest.fixture
def essays_app_module_fixture(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-5-nano")
    monkeypatch.setenv("MODEL_REASONING_DEPLOYMENT", "gpt-5")

    repo_root = Path(__file__).resolve().parents[2]
    essays_root = repo_root / "apps" / "essays"
    essays_src = essays_root / "src"
    lib_src = repo_root / "lib" / "src"

    for entry in (str(essays_root), str(essays_src), str(lib_src)):
        if entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)

    # Clear cached app.* modules to avoid cross-service contamination
    for mod_name in list(sys.modules):
        if (
            mod_name == "app"
            or mod_name.startswith("app.")
            or mod_name == "tutor_lib.agents"
            or mod_name.startswith("tutor_lib.agents.")
            or mod_name == "azure.ai.documentintelligence"
            or mod_name.startswith("azure.ai.documentintelligence.")
        ):
            del sys.modules[mod_name]

    _install_tutor_lib_agents_stub()
    _install_document_intelligence_stub()

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
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-5-nano")
    monkeypatch.setenv("MODEL_REASONING_DEPLOYMENT", "gpt-5")

    repo_root = Path(__file__).resolve().parents[2]
    essays_src = repo_root / "apps" / "essays" / "src"
    lib_src = repo_root / "lib" / "src"

    for entry in (str(essays_src), str(lib_src)):
        if entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)

    for module_name in list(sys.modules):
        if (
            module_name == "app"
            or module_name.startswith("app.")
            or module_name == "tutor_lib.agents"
            or module_name.startswith("tutor_lib.agents.")
            or module_name == "azure.ai.documentintelligence"
            or module_name.startswith("azure.ai.documentintelligence.")
        ):
            sys.modules.pop(module_name, None)

    _install_tutor_lib_agents_stub()
    _install_document_intelligence_stub()

    main_module = importlib.import_module("app.main")
    importlib.reload(main_module)
    return main_module


DEFAULT_RESPONSE = "Overall verdict\n\nStrengths: Solid thesis\n\nImprovements: Tighten conclusion"


class _StubFoundryAgentFacade:
    response_text = DEFAULT_RESPONSE

    def __init__(self, *_args, **_kwargs):
        self.requests = []

    async def invoke(self, request):
        self.requests.append(request)
        return types.SimpleNamespace(output_text=self.response_text, agent=request.agent, store=request.store)


class _FakeCredential:  # noqa: D401 - simple stub credential
    pass


class _StubAssemblyRepository:
    def __init__(self, existing_ids, not_found):
        self._existing_ids = set(existing_ids)
        self._not_found = not_found

    async def get_by_id(self, assembly_id: str):
        if assembly_id not in self._existing_ids:
            raise self._not_found("missing")
        return {
            "id": assembly_id,
            "topic_name": "Topic",
            "essay_id": "essay-stub",
            "agents": [
                {
                    "agent_id": "agent-1",
                    "role": "default",
                    "deployment": "gpt-5-nano",
                }
            ],
        }


@pytest.mark.asyncio
async def test_orchestrator_uses_default_strategy(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    monkeypatch.setattr(module, "FoundryAgentFacade", _StubFoundryAgentFacade)
    _StubFoundryAgentFacade.response_text = DEFAULT_RESPONSE

    provisioned = module.AgentRef(
        agent_name="agent-default",
        agent_version="2026-05-01",
        legacy_agent_id="agent-default-id",
        role="default",
        deployment="gpt-5-nano",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Assembly(id=assembly_id, topic_name="Topic", essay_id="essay-1", agents=[provisioned])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_assembly", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-1", topic="History", content="Text")
    result = await orchestrator.invoke("assembly-1", essay, [])

    assert result.strategy is module.EssayStrategyType.DEFAULT
    assert result.strengths == ["Solid thesis"]
    assert result.improvements == ["Tighten conclusion"]


@pytest.mark.asyncio
async def test_orchestrator_uses_narrative_strategy(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    monkeypatch.setattr(module, "FoundryAgentFacade", _StubFoundryAgentFacade)
    _StubFoundryAgentFacade.response_text = (
        "Narrative verdict\n\nStrengths: Vivid imagery\n\nImprovements: Clarify ending"
    )

    narrative_agent = module.AgentRef(
        agent_name="agent-narrative",
        role="narrative",
        deployment="gpt-5-nano",
    )
    default_agent = module.AgentRef(
        agent_name="agent-default",
        role="default",
        deployment="gpt-5-nano",
    )

    async def _stub_load(_self, assembly_id, **kwargs):  # pragma: no cover - monkeypatched helper
        return module.Assembly(id=assembly_id, topic_name="Topic", essay_id="essay-2", agents=[default_agent, narrative_agent])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_assembly", _stub_load, raising=False)

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
    monkeypatch.setattr(module, "FoundryAgentFacade", _StubFoundryAgentFacade)
    _StubFoundryAgentFacade.response_text = (
        "Analytical verdict\n\nStrengths: Rigorous evidence\n\nImprovements: Expand counterpoints"
    )

    analytical_agent = module.AgentRef(
        agent_name="agent-analytical",
        role="analytical",
        deployment="gpt-5",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Assembly(id=assembly_id, topic_name="Topic", essay_id="essay-3", agents=[analytical_agent])

    monkeypatch.setattr(module.EssayOrchestrator, "_load_assembly", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-3", topic="Science", content="Analysis", theme="Analytical Essay")
    result = await orchestrator.invoke("assembly-3", essay, [])

    assert result.strategy is module.EssayStrategyType.ANALYTICAL
    assert result.strengths == ["Rigorous evidence"]


@pytest.mark.asyncio
async def test_orchestrator_uses_enem_strategy_and_routes_to_enem_role(
    monkeypatch, essays_app_module_fixture
):
    module = essays_app_module_fixture

    created: list[_StubFoundryAgentFacade] = []

    class _RecordingFacade(_StubFoundryAgentFacade):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)

    monkeypatch.setattr(module, "FoundryAgentFacade", _RecordingFacade)
    _StubFoundryAgentFacade.response_text = (
        "ENEM verdict\n\nStrengths: Competency coverage\n\n"
        "Improvements: Strengthen intervention proposal"
    )

    enem_agent = module.AgentRef(
        agent_name="agent-enem",
        role="enem",
        deployment="gpt-5",
    )
    default_agent = module.AgentRef(
        agent_name="agent-default",
        role="default",
        deployment="gpt-5-nano",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Assembly(
            id=assembly_id,
            topic_name="Topic",
            essay_id="essay-enem-theme",
            agents=[default_agent, enem_agent],
        )

    monkeypatch.setattr(module.EssayOrchestrator, "_load_assembly", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()
    essay = module.Essay(
        id="essay-enem-theme",
        topic="Citizenship",
        content="Essay",
        theme="ENEM competency matrix",
    )

    result = await orchestrator.invoke("assembly-enem", essay, [])

    assert result.strategy is module.EssayStrategyType.ENEM
    request = created[0].requests[0]
    assert isinstance(request, module.AgentInvocationRequest)
    assert request.agent.agent_name == "agent-enem"
    assert request.context["essay_id"] == "essay-enem-theme"
    assert request.context["role"] == "enem"
    assert request.context["strategy"] == "enem"
    assert request.store is False


@pytest.mark.asyncio
async def test_orchestrator_uses_enem_strategy_for_competency_objectives(
    monkeypatch, essays_app_module_fixture
):
    module = essays_app_module_fixture

    created: list[_StubFoundryAgentFacade] = []

    class _RecordingFacade(_StubFoundryAgentFacade):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)

    monkeypatch.setattr(module, "FoundryAgentFacade", _RecordingFacade)
    _StubFoundryAgentFacade.response_text = (
        "ENEM objective verdict\n\nStrengths: Clear argumentation\n\n"
        "Improvements: Improve cohesion"
    )

    enem_agent = module.AgentRef(
        agent_name="agent-enem",
        role="enem",
        deployment="gpt-5",
    )

    async def _stub_load(_self, assembly_id, **kwargs):
        return module.Assembly(
            id=assembly_id,
            topic_name="Topic",
            essay_id="essay-enem-objective",
            agents=[enem_agent],
        )

    monkeypatch.setattr(module.EssayOrchestrator, "_load_assembly", _stub_load, raising=False)

    orchestrator = module.EssayOrchestrator()

    essay = module.Essay(id="essay-enem-objective", topic="Education", content="Essay")
    resources = [
        module.Resource(
            id="res-enem",
            essay_id="essay-enem-objective",
            objective=["Competência 1", "Competência 2"],
        )
    ]
    result = await orchestrator.invoke("assembly-enem-objective", essay, resources)

    assert result.strategy is module.EssayStrategyType.ENEM
    request = created[0].requests[0]
    assert request.context["resource_ids"] == ["res-enem"]
    assert request.evidence_refs == ("res-enem",)


@pytest.mark.asyncio
async def test_hydrate_agents_accepts_legacy_shapes(essays_app_module_fixture):
    module = essays_app_module_fixture
    orchestrator = module.EssayOrchestrator()

    agents = await orchestrator._hydrate_agents(
        [
            {"agent_id": "legacy-agent", "role": "default", "deployment": "gpt-5-nano"},
            {"id": "legacy-id", "role": "narrative", "deployment": "gpt-5"},
            "legacy-string",
        ]
    )

    assert [agent.agent_name for agent in agents] == [
        "legacy-agent",
        "legacy-id",
        "legacy-string",
    ]
    assert [agent.legacy_agent_id for agent in agents] == [
        "legacy-agent",
        "legacy-id",
        "legacy-string",
    ]
    assert agents[2].role == "default"


@pytest.mark.asyncio
async def test_hydrate_agents_resolves_legacy_foundry_ids(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture

    class _ResolvingFacade(_StubFoundryAgentFacade):
        async def get_agent(self, agent_id: str):
            assert agent_id == "legacy-agent-id"
            return module.AgentReference(
                agent_name="narrative-grader",
                agent_version="2026-05-09",
                legacy_agent_id=agent_id,
                model_name="gpt-5",
            )

    monkeypatch.setattr(module, "FoundryAgentFacade", _ResolvingFacade)
    orchestrator = module.EssayOrchestrator()

    agents = await orchestrator._hydrate_agents(
        [
            {
                "agent_id": "legacy-agent-id",
                "role": "narrative",
                "deployment": "gpt-5",
            }
        ]
    )

    assert len(agents) == 1
    assert agents[0].agent_name == "narrative-grader"
    assert agents[0].agent_version == "2026-05-09"
    assert agents[0].legacy_agent_id == "legacy-agent-id"
    assert agents[0].role == "narrative"


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
                    "agent_id": "agent-1",
                    "role": "default",
                    "deployment": "gpt-5-nano",
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
async def test_load_assembly_raises_for_missing_assembly(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    not_found = type("NotFound", (Exception,), {})

    monkeypatch.setattr(module, "FoundryAgentFacade", _StubFoundryAgentFacade)
    monkeypatch.setattr(module.exceptions, "CosmosResourceNotFoundError", not_found)
    monkeypatch.setattr(
        module,
        "AssemblyRepository",
        lambda *_args, **_kwargs: _StubAssemblyRepository(existing_ids=set(), not_found=not_found),
    )

    orchestrator = module.EssayOrchestrator()
    essay = module.Essay(id="essay-missing", topic="History", content="Text")

    with pytest.raises(ValueError):
        await orchestrator.invoke("assembly-missing", essay, [])


@pytest.mark.asyncio
async def test_load_assembly_returns_agents(monkeypatch, essays_app_module_fixture):
    module = essays_app_module_fixture
    not_found = type("NotFound", (Exception,), {})

    created: list[_StubFoundryAgentFacade] = []

    class _RecordingFacade(_StubFoundryAgentFacade):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)

    monkeypatch.setattr(module, "FoundryAgentFacade", _RecordingFacade)
    _StubFoundryAgentFacade.response_text = DEFAULT_RESPONSE
    monkeypatch.setattr(module.exceptions, "CosmosResourceNotFoundError", not_found)
    monkeypatch.setattr(
        module,
        "AssemblyRepository",
        lambda *_args, **_kwargs: _StubAssemblyRepository(
            existing_ids={"assembly-present"},
            not_found=not_found,
        ),
    )

    orchestrator = module.EssayOrchestrator()
    essay = module.Essay(id="essay-present", topic="History", content="Text")

    await orchestrator.invoke("assembly-present", essay, [])
    assert created[0].requests[0].agent.agent_name == "agent-1"
    assert created[0].requests[0].agent.legacy_agent_id == "agent-1"


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


def test_prompt_composer_renders_essay_and_resource_details(essays_app_module_fixture):
    module = essays_app_module_fixture
    composer = module.PromptComposer(Path(module.__file__).parent / "prompts")
    essay = module.Essay(
        id="essay-render",
        topic="Citizenship",
        content="",
        theme="ENEM",
        file_url="https://example.test/essay.png",
    )
    resources = [
        module.Resource(
            id="rubric-1",
            essay_id="essay-render",
            objective=["Competência 1", "Competência 2"],
            content="Use formal register.",
            url="https://example.test/rubric",
            file_name="rubric.md",
            content_type="text/markdown",
            metadata={"source": "unit"},
        ),
        module.Resource(
            id="scan-1",
            essay_id="essay-render",
            objective=["Handwriting extraction"],
            file_name="essay.png",
            content_type="image/png",
        ),
    ]

    prompt = composer.render("correct.md", essay, resources)

    assert "Tema: ENEM" in prompt
    assert "URL do arquivo: https://example.test/essay.png" in prompt
    assert "Conteúdo: não fornecido em texto" in prompt
    assert "Objetivos: Competência 1, Competência 2" in prompt
    assert "Metadados: {'source': 'unit'}" in prompt
    assert "Detalhes: Use formal register." in prompt
    assert "arquivo essay.png" in prompt
    assert "{{" not in prompt
    assert "{%" not in prompt


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


@pytest.mark.asyncio
async def test_reprocess_endpoint_returns_fallback_when_orchestrator_runtime_error(
    monkeypatch, essays_main_module_fixture
):
    module = essays_main_module_fixture

    async def _stub_require_essay_document(_essay_id: str):
        return {
            "id": "essay-123",
            "topic": "Topic",
            "content": "Essay text",
            "assembly_id": "assembly-123",
        }

    async def _stub_resources_for_essay(_essay_id: str):
        return []

    class _FailingOrchestrator:
        async def invoke(self, _assembly_id, _essay, _resources):
            raise RuntimeError("Agent run finished with unexpected status RunStatus.FAILED.")

    monkeypatch.setattr(module, "_require_essay_document", _stub_require_essay_document)
    monkeypatch.setattr(module, "_resources_for_essay", _stub_resources_for_essay)
    monkeypatch.setattr(module, "orchestrator", _FailingOrchestrator())

    response = await module.reprocess_essay_evaluation("essay-123")
    body = json.loads(response.body)
    content = body["content"]

    assert response.status_code == 200
    assert body["title"] == "Essay Evaluated"
    assert body["message"] == "Essay evaluation completed"
    assert content["strategy"] == "default"
    assert content["verdict"].strip()
    assert content["strengths"]
    assert content["improvements"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("document", "runtime_error", "expected_substring"),
    [
        (
            {
                "id": "essay-no-assembly",
                "topic": "Topic",
                "content": "Essay text",
                "assembly_id": None,
            },
            None,
            "not associated with an assembly",
        ),
        (
            {
                "id": "essay-unresolvable",
                "topic": "Topic",
                "content": "Essay text",
                "assembly_id": "assembly-missing",
            },
            ValueError("Assembly not found: assembly-missing"),
            "could not be resolved",
        ),
    ],
)
async def test_reprocess_endpoint_returns_400_when_assembly_missing_or_unresolvable(
    monkeypatch,
    essays_main_module_fixture,
    document,
    runtime_error,
    expected_substring,
):
    module = essays_main_module_fixture

    async def _stub_require_essay_document(_essay_id: str):
        return document

    async def _stub_resources_for_essay(_essay_id: str):
        return []

    class _Orchestrator:
        async def invoke(self, _assembly_id, _essay, _resources):
            if runtime_error is not None:
                raise runtime_error
            return None

    monkeypatch.setattr(module, "_require_essay_document", _stub_require_essay_document)
    monkeypatch.setattr(module, "_resources_for_essay", _stub_resources_for_essay)
    monkeypatch.setattr(module, "orchestrator", _Orchestrator())

    with pytest.raises(module.HTTPException) as exc_info:
        await module.reprocess_essay_evaluation(document["id"])

    assert exc_info.value.status_code == 400
    assert expected_substring in str(exc_info.value.detail)