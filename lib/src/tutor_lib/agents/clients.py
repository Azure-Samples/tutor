"""Foundry-native agent facade and Tutor invocation contracts.

The app-facing contracts are PEP 557 dataclasses so service code can stay
data-oriented while SDK response shapes remain inside this module.
"""

from __future__ import annotations

import asyncio
import base64
import inspect
import json
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

CredentialFactory = Callable[[], Any]
OpenAIClientFactory = Callable[[], Any]
ProjectClientFactory = Callable[[str, Any], Any]
SleepCallback = Callable[[float], Awaitable[None]]

_DEFAULT_MAX_ATTEMPTS = 3
_DEFAULT_INITIAL_RETRY_DELAY_SECONDS = 0.5
_RETRYABLE_STATUS_CODES = {408, 429}
_FAILED_RESPONSE_STATUSES = {"failed", "cancelled", "canceled"}
_REVIEW_REQUIRED_RESPONSE_STATUSES = {"incomplete", "queued", "in_progress"}
_SUCCESS_RESPONSE_STATUSES = {"completed"}


@dataclass(frozen=True, slots=True)
class AgentReference:
    """Stable Tutor reference to a Foundry agent by name and version."""

    agent_name: str
    agent_version: str | None = None
    role: str | None = None
    dimension: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    governance_state: str | None = None
    legacy_agent_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Compatibility alias for read-only legacy ``agent_id`` callers."""

        return self.legacy_agent_id or self.agent_name

    @property
    def model(self) -> str | None:
        """Compatibility alias for older materialization helpers."""

        return self.model_name

    @property
    def model_id(self) -> str | None:
        """Compatibility alias for older materialization helpers."""

        return self.model_name

    @property
    def deployment_name(self) -> str | None:
        """Compatibility alias for older materialization helpers."""

        return self.model_name


@dataclass(frozen=True, slots=True)
class AgentAttachment:
    """Binary payload supplied to an agent invocation."""

    file_name: str
    content_type: str
    payload: bytes
    purpose: str = "assistants"
    tool_type: str = "vision"


@dataclass(frozen=True, slots=True)
class AgentInvocationRequest:
    """Command object for invoking a Tutor agent through Foundry."""

    agent: AgentReference
    input: str
    context: Mapping[str, Any] = field(default_factory=dict)
    conversation_id: str | None = None
    previous_invocation_id: str | None = None
    attachments: Sequence[AgentAttachment] = field(default_factory=tuple)
    store: bool = False
    stream: bool = False
    background: bool = False
    evidence_refs: Sequence[str] = field(default_factory=tuple)
    tenant_id: str | None = None
    user_id: str | None = None
    trace_correlation_id: str | None = None
    instructions: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentInvocationResult:
    """Normalized Tutor result returned by an agent invocation."""

    output_text: str
    agent: AgentReference
    invocation_id: str | None = None
    conversation_id: str | None = None
    tool_calls: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    usage: Mapping[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    safety_state: str = "not_evaluated"
    degraded_state: str | None = None
    requires_review: bool = False
    store: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentEvaluationReference:
    """Reference to a Foundry evaluation release gate for an agent version."""

    agent: AgentReference
    dataset_id: str
    evaluation_id: str | None = None
    status: str = "pending"
    thresholds: Mapping[str, float] = field(default_factory=dict)
    report_uri: str | None = None
    trace_id: str | None = None
    lineage: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentSpec:
    """Legacy creation spec routed through the Foundry-native facade."""

    name: str
    instructions: str
    deployment: str
    tools: Iterable[Callable[..., Any]] = field(default_factory=tuple)
    temperature: float | None = None
    max_tokens: int | None = None
    agent_version: str | None = None


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


@asynccontextmanager
async def _managed_resource(resource: Any) -> AsyncIterator[Any]:
    async_enter = getattr(resource, "__aenter__", None)
    async_exit = getattr(resource, "__aexit__", None)
    if callable(async_enter) and callable(async_exit):
        active_resource = await async_enter()
        try:
            yield active_resource
        finally:
            await async_exit(None, None, None)
        return

    sync_enter = getattr(resource, "__enter__", None)
    sync_exit = getattr(resource, "__exit__", None)
    if callable(sync_enter) and callable(sync_exit):
        active_resource = sync_enter()
        try:
            yield active_resource
        finally:
            sync_exit(None, None, None)
        return

    try:
        yield resource
    finally:
        close_method = getattr(resource, "aclose", None) or getattr(resource, "close", None)
        if callable(close_method):
            await _maybe_await(close_method())


def _default_credential() -> Any:
    from azure.identity.aio import DefaultAzureCredential

    return DefaultAzureCredential()


def _field_value(source: Any, name: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(name)
    return getattr(source, name, None)


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        trimmed_value = value.strip()
        return trimmed_value or None
    return str(value)


def _mapping_value(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, Mapping):
            return dict(dumped)
    return {}


def _sequence_value(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _get_status_code(exc: Exception) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        return status_code

    response = getattr(exc, "response", None)
    response_status_code = getattr(response, "status_code", None)
    if isinstance(response_status_code, int):
        return response_status_code
    return None


class FoundryAgentFacade:
    """Facade over Foundry OpenAI-compatible responses and agent management."""

    def __init__(
        self,
        endpoint: str,
        credential_factory: CredentialFactory | None = None,
        *,
        openai_client_factory: OpenAIClientFactory | None = None,
        project_client_factory: ProjectClientFactory | None = None,
        retry_sleep: SleepCallback = asyncio.sleep,
        max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
    ) -> None:
        self._endpoint = endpoint
        self._credential_factory = credential_factory or _default_credential
        self._openai_client_factory = openai_client_factory
        self._project_client_factory = project_client_factory
        self._retry_sleep = retry_sleep
        self._max_attempts = max_attempts

    async def invoke(self, request: AgentInvocationRequest) -> AgentInvocationResult:
        """Invoke an agent and return a normalized Tutor response."""

        payload = self._build_response_payload(request)

        async def _execute() -> AgentInvocationResult:
            async with self._openai_client() as client:
                responses = getattr(client, "responses", None)
                create_response = getattr(responses, "create", None)
                if not callable(create_response):
                    raise RuntimeError("OpenAI-compatible client does not expose responses.create.")

                response = await _maybe_await(create_response(**payload))
                return self._normalize_response(response, request)

        return await self._with_retries("invoke", _execute)

    async def create_agent(
        self,
        *,
        name: str,
        instructions: str,
        deployment: str,
        temperature: float | None = None,
    ) -> AgentReference:
        """Create a Foundry agent and normalize the returned reference."""

        definition = self._build_prompt_agent_definition(
            model=deployment,
            instructions=instructions,
            temperature=temperature,
        )

        async def _execute() -> AgentReference:
            async with self._agents_client() as client:
                create_method = getattr(client, "create_version", None)
                if not callable(create_method):
                    raise RuntimeError("Agents client does not expose create_version.")

                remote_agent = await _maybe_await(
                    create_method(agent_name=name, definition=definition)
                )
                return self._agent_reference_from_remote(
                    remote_agent,
                    fallback_name=name,
                    fallback_model=deployment,
                )

        return await self._with_retries("create_agent", _execute)

    @staticmethod
    def _build_prompt_agent_definition(
        *,
        model: str,
        instructions: str,
        temperature: float | None = None,
    ) -> Any:
        from azure.ai.projects.models import PromptAgentDefinition

        definition_payload: dict[str, Any] = {
            "model": model,
            "instructions": instructions,
        }
        if temperature is not None:
            definition_payload["temperature"] = temperature
        return PromptAgentDefinition(**definition_payload)

    async def delete_agent(self, agent_id: str) -> None:
        """Delete a Foundry agent by its legacy service identifier."""

        async def _execute() -> None:
            async with self._agents_client() as client:
                delete_method = getattr(client, "delete_agent", None)
                if callable(delete_method):
                    await _maybe_await(delete_method(agent_id=agent_id))
                    return

                delete_method = getattr(client, "delete", None)
                if callable(delete_method):
                    await _maybe_await(delete_method(agent_id=agent_id))
                    return

                raise RuntimeError("Agents client does not expose delete_agent/delete.")

        await self._with_retries("delete_agent", _execute)

    async def get_agent(self, agent_id: str) -> AgentReference:
        """Return a normalized read-only reference for an existing Foundry agent."""

        async def _execute() -> AgentReference:
            async with self._agents_client() as client:
                get_method = getattr(client, "get_agent", None)
                if callable(get_method):
                    remote_agent = await _maybe_await(get_method(agent_id=agent_id))
                    return self._agent_reference_from_remote(
                        remote_agent,
                        fallback_name=agent_id,
                    )

                get_method = getattr(client, "get", None)
                if callable(get_method):
                    remote_agent = await _maybe_await(get_method(agent_id=agent_id))
                    return self._agent_reference_from_remote(
                        remote_agent,
                        fallback_name=agent_id,
                    )

                raise RuntimeError("Agents client does not expose get_agent/get.")

        return await self._with_retries("get_agent", _execute)

    async def list_agents(self, *, limit: int | None = None) -> list[AgentReference]:
        """List Foundry agents as normalized Tutor references."""

        async def _execute() -> list[AgentReference]:
            async with self._agents_client() as client:
                list_method = getattr(client, "list_agents", None)
                if not callable(list_method):
                    list_method = getattr(client, "list", None)
                if not callable(list_method):
                    raise RuntimeError("Agents client does not expose list_agents/list.")

                produced = list_method()
                results: list[AgentReference] = []
                async for remote_agent in self._iterate_remote_agents(produced):
                    results.append(self._agent_reference_from_remote(remote_agent))
                    if limit is not None and len(results) >= limit:
                        break
                return results

        return await self._with_retries("list_agents", _execute)

    async def _iterate_remote_agents(self, produced: Any) -> AsyncIterator[Any]:
        resolved = await _maybe_await(produced)
        if hasattr(resolved, "__aiter__"):
            async for item in resolved:
                yield item
            return

        if isinstance(resolved, Mapping):
            values = (
                resolved.get("data")
                or resolved.get("value")
                or resolved.get("agents")
                or []
            )
        else:
            values = resolved

        if isinstance(values, Iterable) and not isinstance(values, (str, bytes)):
            for item in values:
                yield item

    @asynccontextmanager
    async def _credential(self) -> AsyncIterator[Any]:
        credential = self._credential_factory()
        async with _managed_resource(credential) as active_credential:
            yield active_credential

    @asynccontextmanager
    async def _project_client(self) -> AsyncIterator[Any]:
        async with self._credential() as credential:
            if self._project_client_factory is not None:
                project_client = self._project_client_factory(self._endpoint, credential)
            else:
                from azure.ai.projects.aio import AIProjectClient

                project_client = AIProjectClient(endpoint=self._endpoint, credential=credential)

            async with _managed_resource(project_client) as active_project_client:
                yield active_project_client

    @asynccontextmanager
    async def _openai_client(self) -> AsyncIterator[Any]:
        if self._openai_client_factory is not None:
            openai_client = self._openai_client_factory()
            async with _managed_resource(openai_client) as active_openai_client:
                yield active_openai_client
            return

        async with self._project_client() as project_client:
            get_openai_client = getattr(project_client, "get_openai_client", None)
            if not callable(get_openai_client):
                raise RuntimeError("AIProjectClient does not expose get_openai_client.")

            openai_client = await _maybe_await(get_openai_client())
            async with _managed_resource(openai_client) as active_openai_client:
                yield active_openai_client

    @asynccontextmanager
    async def _agents_client(self) -> AsyncIterator[Any]:
        async with self._project_client() as project_client:
            agents_client = getattr(project_client, "agents", None)
            if agents_client is None:
                get_agents_client = getattr(project_client, "get_agents_client", None)
                if callable(get_agents_client):
                    agents_client = await _maybe_await(get_agents_client())
            if agents_client is None:
                raise RuntimeError("AIProjectClient does not expose an agents client.")
            yield agents_client

    async def _with_retries(self, operation: str, callback: Callable[[], Awaitable[Any]]) -> Any:
        delay_seconds = _DEFAULT_INITIAL_RETRY_DELAY_SECONDS
        last_error: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                return await callback()
            # pylint: disable-next=broad-exception-caught
            except Exception as exc:  # noqa: BLE001
                if not self._is_retryable_error(exc):
                    raise
                last_error = exc
                if attempt == self._max_attempts:
                    break
                await self._retry_sleep(delay_seconds)
                delay_seconds *= 2

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"{operation} failed without an explicit exception")

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        try:
            from azure.core import exceptions as azure_exceptions
        except ModuleNotFoundError:
            azure_exceptions = None

        if azure_exceptions is not None:
            retryable_types = tuple(
                error_type
                for error_type in (
                    getattr(azure_exceptions, "ServiceRequestError", None),
                    getattr(azure_exceptions, "ServiceResponseError", None),
                )
                if isinstance(error_type, type)
            )
            if retryable_types and isinstance(exc, retryable_types):
                return True

        status_code = _get_status_code(exc)
        if status_code is None:
            return False
        if status_code in _RETRYABLE_STATUS_CODES:
            return True
        return status_code >= 500

    def _build_response_payload(self, request: AgentInvocationRequest) -> dict[str, Any]:
        self._validate_response_request(request)

        payload: dict[str, Any] = {
            "extra_body": self._build_agent_reference_body(request.agent),
            "input": self._build_input(request),
            "store": request.store,
            "metadata": self._build_metadata(request),
        }
        if request.instructions:
            payload["instructions"] = request.instructions
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            payload["max_output_tokens"] = request.max_output_tokens
        if request.previous_invocation_id:
            payload["previous_response_id"] = request.previous_invocation_id
        if request.conversation_id:
            payload["conversation"] = request.conversation_id
        if request.stream:
            payload["stream"] = True
        if request.background:
            payload["background"] = True
        return payload

    @staticmethod
    def _validate_response_request(request: AgentInvocationRequest) -> None:
        if request.background and not request.store:
            raise ValueError(
                "Foundry background responses require store=True; keep store=False "
                "unless durable conversation mode is explicitly enabled."
            )

    @staticmethod
    def _build_agent_reference_body(agent: AgentReference) -> dict[str, dict[str, str]]:
        return {
            "agent_reference": {
                "type": "agent_reference",
                "name": agent.agent_name,
            }
        }

    def _build_input(self, request: AgentInvocationRequest) -> list[dict[str, Any]]:
        content_blocks: list[dict[str, Any]] = [
            {"type": "input_text", "text": self._render_input_text(request)}
        ]
        content_blocks.extend(self._attachment_content_blocks(request.attachments))
        return [{"role": "user", "content": content_blocks}]

    @staticmethod
    def _render_input_text(request: AgentInvocationRequest) -> str:
        if not request.context:
            return request.input
        context_text = json.dumps(request.context, ensure_ascii=False, sort_keys=True, default=str)
        return f"{request.input}\n\nContext:\n{context_text}"

    @staticmethod
    def _attachment_content_blocks(
        attachments: Sequence[AgentAttachment],
    ) -> list[dict[str, Any]]:
        content_blocks: list[dict[str, Any]] = []
        for attachment in attachments:
            if not attachment.payload:
                continue
            content_type = attachment.content_type or "application/octet-stream"
            if content_type.lower().startswith("image/"):
                encoded = base64.b64encode(attachment.payload).decode("ascii")
                content_blocks.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:{content_type};base64,{encoded}",
                    }
                )
                continue

            content_blocks.append(
                {
                    "type": "input_text",
                    "text": (
                        f"Attachment available: {attachment.file_name} "
                        f"({content_type}, {len(attachment.payload)} bytes)."
                    ),
                }
            )
        return content_blocks

    @staticmethod
    def _build_metadata(request: AgentInvocationRequest) -> dict[str, str]:
        metadata: dict[str, str] = {
            "agent_name": request.agent.agent_name,
            "retention_policy": "foundry_stored" if request.store else "application_controlled",
            "store": str(request.store).lower(),
        }

        optional_values = {
            "agent_version": request.agent.agent_version,
            "role": request.agent.role,
            "dimension": request.agent.dimension,
            "model_provider": request.agent.model_provider,
            "model_name": request.agent.model_name,
            "prompt_version": request.agent.prompt_version,
            "governance_state": request.agent.governance_state,
            "legacy_agent_id": request.agent.legacy_agent_id,
            "conversation_id": request.conversation_id,
            "tenant_id": request.tenant_id,
            "user_id": request.user_id,
            "trace_correlation_id": request.trace_correlation_id,
        }
        for name, value in optional_values.items():
            text_value = _string_value(value)
            if text_value is not None:
                metadata[name] = text_value

        if request.evidence_refs:
            metadata["evidence_refs"] = ",".join(request.evidence_refs)

        for name, value in {**request.agent.metadata, **request.metadata}.items():
            text_value = _string_value(value)
            if text_value is not None:
                metadata[str(name)] = text_value
        return metadata

    def _normalize_response(
        self,
        response: Any,
        request: AgentInvocationRequest,
    ) -> AgentInvocationResult:
        response_id = _string_value(_field_value(response, "id"))
        response_metadata = self._response_metadata(response)
        response_status = _string_value(response_metadata.get("response_status"))
        self._raise_for_failed_response(response_id, response_status, response_metadata)

        conversation_id = (
            _string_value(_field_value(response, "conversation_id"))
            or request.conversation_id
        )
        model_name = _string_value(_field_value(response, "model")) or request.agent.model_name
        trace_id = (
            _string_value(_field_value(response, "trace_id"))
            or _string_value(response_metadata.get("trace_id"))
            or request.trace_correlation_id
        )
        degraded_state = _string_value(response_metadata.get("degraded_state"))
        requires_review = str(response_metadata.get("requires_review", "false")).lower() == "true"
        if self._response_requires_review(response_status):
            degraded_state = degraded_state or f"response_{response_status}"
            requires_review = True

        return AgentInvocationResult(
            output_text=self._extract_output_text(response),
            agent=request.agent,
            invocation_id=response_id,
            conversation_id=conversation_id,
            tool_calls=tuple(self._extract_tool_calls(response)),
            usage=_mapping_value(_field_value(response, "usage")),
            trace_id=trace_id,
            model_provider=request.agent.model_provider,
            model_name=model_name,
            safety_state=_string_value(response_metadata.get("safety_state")) or "not_evaluated",
            degraded_state=degraded_state,
            requires_review=requires_review,
            store=request.store,
            metadata=response_metadata,
        )

    @staticmethod
    def _response_metadata(response: Any) -> dict[str, Any]:
        response_metadata = _mapping_value(_field_value(response, "metadata"))
        response_status = _string_value(_field_value(response, "status"))
        response_error = FoundryAgentFacade._diagnostic_value(
            _field_value(response, "error")
        )
        incomplete_details = FoundryAgentFacade._diagnostic_value(
            _field_value(response, "incomplete_details")
        )

        if response_status is not None:
            response_metadata["response_status"] = response_status
        if response_error is not None:
            response_metadata["response_error"] = response_error
        if incomplete_details is not None:
            response_metadata["response_incomplete_details"] = incomplete_details
        return response_metadata

    @staticmethod
    def _diagnostic_value(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        mapped_value = _mapping_value(value)
        if mapped_value:
            return mapped_value
        return str(value)

    @staticmethod
    def _raise_for_failed_response(
        response_id: str | None,
        response_status: str | None,
        response_metadata: Mapping[str, Any],
    ) -> None:
        if response_status not in _FAILED_RESPONSE_STATUSES:
            return

        diagnostic = (
            response_metadata.get("response_error")
            or response_metadata.get("response_incomplete_details")
            or "no diagnostic payload"
        )
        if not isinstance(diagnostic, str):
            diagnostic = json.dumps(diagnostic, ensure_ascii=False, sort_keys=True, default=str)
        raise RuntimeError(
            f"Foundry response {response_id or '<unknown>'} ended with "
            f"status {response_status}: {diagnostic}"
        )

    @staticmethod
    def _response_requires_review(response_status: str | None) -> bool:
        if response_status is None or response_status in _SUCCESS_RESPONSE_STATUSES:
            return False
        if response_status in _REVIEW_REQUIRED_RESPONSE_STATUSES:
            return True
        return response_status not in _FAILED_RESPONSE_STATUSES

    def _extract_output_text(self, response: Any) -> str:
        for field_name in ("output_text", "text"):
            direct_text = _field_value(response, field_name)
            if isinstance(direct_text, str) and direct_text.strip():
                return direct_text.strip()

        output_items = _sequence_value(_field_value(response, "output"))
        accumulated: list[str] = []
        for item in output_items:
            item_text = self._text_from_block(item)
            if item_text:
                accumulated.append(item_text)

            for block in _sequence_value(_field_value(item, "content")):
                block_text = self._text_from_block(block)
                if block_text:
                    accumulated.append(block_text)

        return "\n".join(accumulated).strip()

    @staticmethod
    def _text_from_block(block: Any) -> str | None:
        for field_name in ("text", "content", "value"):
            value = _field_value(block, field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
            nested_value = _field_value(value, "value")
            if isinstance(nested_value, str) and nested_value.strip():
                return nested_value.strip()
        return None

    @staticmethod
    def _extract_tool_calls(response: Any) -> list[Mapping[str, Any]]:
        tool_calls: list[Mapping[str, Any]] = []
        for item in _sequence_value(_field_value(response, "output")):
            item_type = _string_value(_field_value(item, "type")) or ""
            if "tool" in item_type or "function_call" in item_type:
                tool_calls.append(_mapping_value(item))
        return tool_calls

    @staticmethod
    def _agent_reference_from_remote(
        remote_agent: Any,
        *,
        fallback_name: str | None = None,
        fallback_model: str | None = None,
    ) -> AgentReference:
        if isinstance(remote_agent, AgentReference):
            return remote_agent

        remote_id = _string_value(_field_value(remote_agent, "id"))
        object_type = _string_value(_field_value(remote_agent, "object"))
        legacy_agent_id = None if object_type == "agent.version" else remote_id
        definition = _field_value(remote_agent, "definition")
        agent_name = (
            _string_value(_field_value(remote_agent, "name"))
            or _string_value(_field_value(remote_agent, "agent_name"))
            or fallback_name
            or legacy_agent_id
            or "foundry-agent"
        )
        agent_version = (
            _string_value(_field_value(remote_agent, "version"))
            or _string_value(_field_value(remote_agent, "agent_version"))
            or _string_value(_field_value(remote_agent, "published_version"))
        )
        model_name = (
            _string_value(_field_value(remote_agent, "model"))
            or _string_value(_field_value(remote_agent, "model_id"))
            or _string_value(_field_value(remote_agent, "deployment_name"))
            or _string_value(_field_value(definition, "model"))
            or fallback_model
        )

        return AgentReference(
            agent_name=agent_name,
            agent_version=agent_version,
            model_name=model_name,
            legacy_agent_id=legacy_agent_id,
        )


class FoundryAgentService(FoundryAgentFacade):
    """Compatibility name for the Foundry-native facade."""

    async def run_agent(
        self,
        agent_id: str,
        prompt: str,
        *,
        attachments: Sequence[AgentAttachment] | None = None,
    ) -> str:
        """Legacy ``agent_id`` adapter routed through ``invoke``."""

        request = AgentInvocationRequest(
            agent=AgentReference(agent_name=agent_id, legacy_agent_id=agent_id),
            input=prompt,
            attachments=tuple(attachments or ()),
            store=False,
        )
        result = await self.invoke(request)
        return result.output_text


@dataclass(slots=True)
class _LegacyAgentCommand:
    facade: FoundryAgentFacade
    reference: AgentReference
    instructions: str
    temperature: float | None = None
    max_output_tokens: int | None = None

    async def run(self, prompt: str, **options: Any) -> str:
        request = AgentInvocationRequest(
            agent=self.reference,
            input=prompt,
            instructions=self.instructions,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            store=bool(options.pop("store", False)),
            conversation_id=options.pop("conversation_id", None),
            previous_invocation_id=options.pop("previous_invocation_id", None),
            metadata=options,
        )
        result = await self.facade.invoke(request)
        return result.output_text


class AgentRegistry:
    """Legacy factory that creates facade-backed invocation commands."""

    def __init__(
        self,
        project_endpoint: str,
        credential_factory: CredentialFactory | None = None,
        *,
        facade: FoundryAgentFacade | None = None,
    ) -> None:
        self._facade = facade or FoundryAgentFacade(
            project_endpoint,
            credential_factory=credential_factory,
        )

    def create(self, spec: AgentSpec) -> _LegacyAgentCommand:
        """Create a compatibility command without Agent Framework runtime."""

        reference = AgentReference(
            agent_name=spec.name,
            agent_version=spec.agent_version or "current",
            model_name=spec.deployment,
        )
        return _LegacyAgentCommand(
            facade=self._facade,
            reference=reference,
            instructions=spec.instructions,
            temperature=spec.temperature,
            max_output_tokens=spec.max_tokens,
        )


class AgentRunContext:
    """Legacy runner that awaits facade-backed command objects."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    async def run(self, prompt: str, **kwargs: Any) -> Any:
        run_method = getattr(self._agent, "run", None)
        if not callable(run_method):
            raise RuntimeError("Agent command does not expose run.")
        return await _maybe_await(run_method(prompt, **kwargs))
