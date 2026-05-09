from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
LIB_SRC = ROOT / "lib" / "src"

if str(LIB_SRC) not in sys.path:
    sys.path.insert(0, str(LIB_SRC))


def _clear_tutor_lib_agents_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "tutor_lib.agents" or module_name.startswith("tutor_lib.agents."):
            sys.modules.pop(module_name, None)

    tutor_lib_module = sys.modules.get("tutor_lib")
    if tutor_lib_module is not None and hasattr(tutor_lib_module, "agents"):
        delattr(tutor_lib_module, "agents")


@pytest.fixture(autouse=True)
def _isolate_agent_facade_imports() -> Iterator[None]:
    _clear_tutor_lib_agents_modules()
    yield
    _clear_tutor_lib_agents_modules()


async def _no_sleep(_: float) -> None:
    return None


class _RetryableError(Exception):
    status_code = 429


class _Responses:
    def __init__(
        self,
        *,
        fail_once: bool = False,
        response: dict[str, Any] | None = None,
    ) -> None:
        self.fail_once = fail_once
        self.response = response
        self.payloads: list[dict[str, Any]] = []

    async def create(self, **payload: Any) -> dict[str, Any]:
        self.payloads.append(payload)
        if self.fail_once:
            self.fail_once = False
            raise _RetryableError("retry later")
        if self.response is not None:
            return self.response
        return {
            "id": "resp-1",
            "status": "completed",
            "output_text": "normalized response",
            "usage": {"total_tokens": 7},
        }


class _OpenAIClient:
    def __init__(self, responses: _Responses) -> None:
        self.responses = responses


class _PromptAgentDefinition:
    def __init__(self, **payload: Any) -> None:
        self.payload = payload
        self.model = payload.get("model")
        self.instructions = payload.get("instructions")
        self.temperature = payload.get("temperature")


class _AgentsClient:
    def __init__(self) -> None:
        self.create_version_payloads: list[dict[str, Any]] = []

    async def create_version(self, agent_name: str, *, definition: Any) -> dict[str, Any]:
        self.create_version_payloads.append(
            {
                "agent_name": agent_name,
                "definition": definition,
            }
        )
        return {
            "id": "agent-version-internal-id",
            "object": "agent.version",
            "name": agent_name,
            "version": "2026-05-09",
            "definition": definition,
        }


def _install_prompt_agent_definition_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    azure_module = ModuleType("azure")
    ai_module = ModuleType("azure.ai")
    projects_module = ModuleType("azure.ai.projects")
    models_module = ModuleType("azure.ai.projects.models")
    models_module.PromptAgentDefinition = _PromptAgentDefinition

    monkeypatch.setitem(sys.modules, "azure", azure_module)
    monkeypatch.setitem(sys.modules, "azure.ai", ai_module)
    monkeypatch.setitem(sys.modules, "azure.ai.projects", projects_module)
    monkeypatch.setitem(sys.modules, "azure.ai.projects.models", models_module)


def test_import_does_not_load_agent_framework_modules() -> None:
    for module_name in (
        "agent_framework",
        "agent_framework_azure_ai",
        "azure.ai.agents.models",
        "azure.ai.projects.models",
    ):
        sys.modules.pop(module_name, None)

    agents = importlib.import_module("tutor_lib.agents")

    assert agents.AgentReference(agent_name="coach", agent_version="current")
    assert "agent_framework" not in sys.modules
    assert "agent_framework_azure_ai" not in sys.modules
    assert "azure.ai.agents.models" not in sys.modules
    assert "azure.ai.projects.models" not in sys.modules


def test_legacy_compatibility_types_are_not_public_exports() -> None:
    agents = importlib.import_module("tutor_lib.agents")

    for symbol_name in ("AgentRegistry", "AgentRunContext", "AgentSpec"):
        assert symbol_name not in agents.__all__
        assert not hasattr(agents, symbol_name)


@pytest.mark.asyncio
async def test_invoke_defaults_to_application_controlled_retention() -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses()
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    result = await facade.invoke(
        AgentInvocationRequest(
            agent=AgentReference(
                agent_name="guidance-coach",
                agent_version="current",
                model_name="model-neutral-deployment",
            ),
            input="Review this plan.",
        )
    )

    assert result.output_text == "normalized response"
    assert result.model_name == "model-neutral-deployment"
    assert "model" not in responses.payloads[0]
    assert responses.payloads[0]["extra_body"] == {
        "agent_reference": {
            "type": "agent_reference",
            "name": "guidance-coach",
        }
    }
    assert result.store is False
    assert responses.payloads[0]["store"] is False
    assert responses.payloads[0]["metadata"]["retention_policy"] == "application_controlled"
    assert responses.payloads[0]["metadata"]["agent_name"] == "guidance-coach"
    assert responses.payloads[0]["metadata"]["agent_version"] == "current"
    assert responses.payloads[0]["metadata"]["model_name"] == "model-neutral-deployment"


@pytest.mark.asyncio
async def test_invoke_propagates_conversation_id_to_responses_create() -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses()
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    result = await facade.invoke(
        AgentInvocationRequest(
            agent=AgentReference(agent_name="guidance-coach", agent_version="current"),
            input="Continue this conversation.",
            conversation_id="conv-123",
        )
    )

    assert result.conversation_id == "conv-123"
    assert responses.payloads[0]["conversation"] == "conv-123"
    assert responses.payloads[0]["metadata"]["conversation_id"] == "conv-123"


@pytest.mark.asyncio
async def test_create_agent_uses_foundry_create_version_definition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tutor_lib.agents import FoundryAgentFacade

    _install_prompt_agent_definition_fake(monkeypatch)
    agents_client = _AgentsClient()
    facade = FoundryAgentFacade(
        "https://example.test/project",
        credential_factory=object,
        project_client_factory=lambda _endpoint, _credential: SimpleNamespace(
            agents=agents_client
        ),
        retry_sleep=_no_sleep,
    )

    reference = await facade.create_agent(
        name="guidance-coach",
        instructions="Coach the learner with concise feedback.",
        deployment="gpt-5-mini",
        temperature=0.2,
    )

    assert len(agents_client.create_version_payloads) == 1
    payload = agents_client.create_version_payloads[0]
    assert payload["agent_name"] == "guidance-coach"
    assert "model" not in payload
    definition = payload["definition"]
    assert isinstance(definition, _PromptAgentDefinition)
    assert definition.model == "gpt-5-mini"
    assert definition.instructions == "Coach the learner with concise feedback."
    assert definition.temperature == 0.2
    assert reference.agent_name == "guidance-coach"
    assert reference.agent_version == "2026-05-09"
    assert reference.model_name == "gpt-5-mini"


@pytest.mark.asyncio
async def test_legacy_run_agent_routes_through_invoke() -> None:
    from tutor_lib.agents import FoundryAgentService

    responses = _Responses()
    service = FoundryAgentService(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    text = await service.run_agent("legacy-agent-id", "Grade this answer.")

    assert text == "normalized response"
    assert "model" not in responses.payloads[0]
    assert responses.payloads[0]["extra_body"] == {
        "agent_reference": {
            "type": "agent_reference",
            "name": "legacy-agent-id",
        }
    }
    assert responses.payloads[0]["store"] is False
    assert responses.payloads[0]["metadata"]["legacy_agent_id"] == "legacy-agent-id"


@pytest.mark.asyncio
async def test_background_requires_stored_mode_before_sdk_call() -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses()
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    with pytest.raises(ValueError, match="background responses require store=True"):
        await facade.invoke(
            AgentInvocationRequest(
                agent=AgentReference(agent_name="coach", agent_version="current"),
                input="Run this in the background.",
                background=True,
            )
        )

    assert responses.payloads == []


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["failed", "cancelled", "canceled"])
async def test_failed_terminal_response_states_raise(status: str) -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses(
        response={
            "id": "resp-failed",
            "status": status,
            "error": {"message": "agent execution did not complete"},
        }
    )
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    with pytest.raises(RuntimeError, match="agent execution did not complete"):
        await facade.invoke(
            AgentInvocationRequest(
                agent=AgentReference(agent_name="coach", agent_version="current"),
                input="Handle this safely.",
            )
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["incomplete", "queued", "in_progress", "unknown"])
async def test_incomplete_and_uncertain_response_states_require_review(status: str) -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses(
        response={
            "id": "resp-incomplete",
            "status": status,
            "output_text": "partial response",
            "incomplete_details": {"reason": "max_output_tokens"},
        }
    )
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    result = await facade.invoke(
        AgentInvocationRequest(
            agent=AgentReference(agent_name="coach", agent_version="current"),
            input="Summarize safely.",
        )
    )

    assert result.output_text == "partial response"
    assert result.requires_review is True
    assert result.degraded_state == f"response_{status}"
    assert result.metadata["response_status"] == status
    assert result.metadata["response_incomplete_details"] == {
        "reason": "max_output_tokens"
    }


@pytest.mark.asyncio
async def test_retryable_response_errors_are_retried() -> None:
    from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

    responses = _Responses(fail_once=True)
    facade = FoundryAgentFacade(
        "https://example.test/project",
        openai_client_factory=lambda: _OpenAIClient(responses),
        retry_sleep=_no_sleep,
    )

    result = await facade.invoke(
        AgentInvocationRequest(
            agent=AgentReference(agent_name="coach", agent_version="current"),
            input="Retry this.",
        )
    )

    assert result.output_text == "normalized response"
    assert len(responses.payloads) == 2