"""Agent creation and execution wrappers for the Tutor platform."""

from __future__ import annotations

import asyncio
import inspect
import logging
import agent_framework as _af
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, AsyncIterator, Callable, Iterable, Sequence, cast

_Agent = getattr(_af, "Agent", getattr(_af, "ChatAgent", None))
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agents.models import Agent, ListSortOrder, RunStatus
from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core import exceptions as azure_exceptions
from azure.core.exceptions import AzureError
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from .tooling import ToolBuilder


logger = logging.getLogger(__name__)
AgentType = Any


@dataclass(slots=True)
class AgentSpec:
    """Specification for creating a Foundry-backed agent."""

    name: str
    instructions: str
    deployment: str
    tools: Iterable[Callable[..., Any]] = field(default_factory=tuple)
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass(slots=True)
class AgentAttachment:
    """Binary payload destined for Azure AI Agents message content."""

    file_name: str
    content_type: str
    payload: bytes
    purpose: str = "assistants"
    tool_type: str = "vision"


class AgentRegistry:
    """Factory that creates ChatAgent instances backed by Azure AI Foundry."""

    def __init__(self, project_endpoint: str, credential_factory: Callable[[], Any] | None = None) -> None:
        self._project_endpoint = project_endpoint
        self._credential_factory = credential_factory or AsyncDefaultAzureCredential
        self._tool_builder = ToolBuilder()

    def create(self, spec: AgentSpec) -> AgentType:
        """Create a ChatAgent wrapping an AzureAIAgentClient."""
        if _Agent is None:
            raise RuntimeError(
                "The installed agent-framework package does not export Agent/ChatAgent. "
                "Install a compatible agent-framework version."
            )
        client = AzureAIAgentClient(
            project_endpoint=self._project_endpoint,
            model_deployment_name=spec.deployment,
            async_credential=self._credential_factory(),
            agent_name=spec.name,
        )
        configured_tools = self._tool_builder.from_callbacks(spec.tools)
        return _Agent(
            chat_client=client,
            instructions=spec.instructions,
            name=spec.name,
            tools=configured_tools or None,
        )


class AgentRunContext:
    """Wrapper that executes a ChatAgent and returns the response."""

    def __init__(self, agent: AgentType) -> None:
        self._agent = agent

    async def run(self, prompt: str, **kwargs: Any) -> Any:
        """Run the agent with the given prompt."""
        result = self._agent.run(prompt, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result


class FoundryAgentService:
    """Manage Azure AI Foundry agents: create, delete, run, list."""

    def __init__(
        self,
        endpoint: str,
        credential_factory: Callable[[], AsyncTokenCredential] | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._credential_factory = credential_factory or AsyncDefaultAzureCredential

    @staticmethod
    def _is_retryable_azure_error(exc: AzureError) -> bool:
        if isinstance(exc, (azure_exceptions.ServiceRequestError, azure_exceptions.ServiceResponseError)):
            return True

        status_code = cast(int | None, getattr(exc, "status_code", None))
        if status_code is None:
            return False
        if status_code in {408, 429}:
            return True
        return status_code >= 500

    async def _with_retries(self, operation: str, callback: Callable[[], Any]) -> Any:
        delay_seconds = 0.5
        max_attempts = 3
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                return await callback()
            except AzureError as exc:
                if not self._is_retryable_azure_error(exc):
                    raise
                last_error = exc
                if attempt == max_attempts:
                    break
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"{operation} failed without an explicit exception")

    @asynccontextmanager
    async def _credential(self) -> AsyncIterator[AsyncTokenCredential]:
        credential = self._credential_factory()
        has_async_cm = all(
            callable(getattr(credential, attr, None)) for attr in ("__aenter__", "__aexit__")
        )
        if has_async_cm:
            token = await credential.__aenter__()
            try:
                yield token
            finally:
                await credential.__aexit__(None, None, None)
        else:
            try:
                yield credential
            finally:
                close_method = getattr(credential, "close", None)
                if callable(close_method):
                    result = close_method()
                    if inspect.isawaitable(result):
                        await result

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[Any]:
        async with self._credential() as credential:
            project_client = AIProjectClient(endpoint=self._endpoint, credential=credential)
            await project_client.__aenter__()
            try:
                yield project_client.agents
            finally:
                await project_client.__aexit__(None, None, None)

    async def create_agent(
        self,
        *,
        name: str,
        instructions: str,
        deployment: str,
        temperature: float | None = None,
    ) -> Agent:
        payload: dict[str, Any] = {
            "name": name,
            "instructions": instructions,
            "model": deployment,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        async def _execute() -> Agent:
            async with self._client() as client:
                create_method = getattr(client, "create_agent", None)
                if callable(create_method):
                    return await create_method(**payload)

                create_method = getattr(client, "create", None)
                if callable(create_method):
                    return await create_method(**payload)

                raise RuntimeError("AgentsClient does not expose create_agent/create operations.")

        try:
            return await self._with_retries("create_agent", _execute)
        except RuntimeError as exc:
            logger.error("Failed to create agent %s: %s", name, exc)
            raise

    async def delete_agent(self, agent_id: str) -> None:
        async def _execute() -> None:
            async with self._client() as client:
                delete_method = getattr(client, "delete_agent", None)
                if callable(delete_method):
                    await delete_method(agent_id=agent_id)
                    return

                delete_method = getattr(client, "delete", None)
                if callable(delete_method):
                    await delete_method(agent_id=agent_id)
                    return

                raise RuntimeError("AgentsClient does not expose delete_agent/delete operations.")

        await self._with_retries("delete_agent", _execute)

    async def run_agent(
        self,
        agent_id: str,
        prompt: str,
        *,
        attachments: Sequence[AgentAttachment] | None = None,
    ) -> str:
        async def _execute() -> str:
            async with self._client() as client:
                thread = await client.threads.create()
                uploaded_files: list[str] = []
                streams: list[BytesIO] = []
                content_blocks: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
                message_attachments: list[dict[str, Any]] = []

                try:
                    if attachments:
                        for attachment in attachments:
                            if not attachment.payload:
                                continue
                            stream = BytesIO(attachment.payload)
                            streams.append(stream)
                            file_name = attachment.file_name or "resource.bin"
                            content_type = attachment.content_type or "application/octet-stream"
                            purpose = attachment.purpose or "vision"
                            file_info = await client.files.upload(
                                file=(file_name, stream, content_type),
                                purpose=purpose,
                                filename=file_name,
                            )
                            file_id = getattr(file_info, "id", None)
                            if isinstance(file_id, str):
                                uploaded_files.append(file_id)
                                tool_type = attachment.tool_type or "vision"
                                message_attachments.append(
                                    {
                                        "file_id": file_id,
                                        "tools": [{"type": tool_type}],
                                    }
                                )

                    await client.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=cast(Any, content_blocks),
                        attachments=cast(Any, message_attachments) if message_attachments else None,
                    )

                    run = await client.runs.create(
                        thread_id=thread.id,
                        agent_id=agent_id,
                    )

                    transitional_statuses = {
                        RunStatus.QUEUED,
                        RunStatus.IN_PROGRESS,
                        RunStatus.CANCELLING,
                    }
                    starting_status = getattr(RunStatus, "STARTING", None)
                    if starting_status is not None:
                        transitional_statuses.add(starting_status)

                    while run.status in transitional_statuses:
                        await asyncio.sleep(0.5)
                        run = await client.runs.get(
                            thread_id=thread.id,
                            run_id=run.id,
                        )

                    if run.status == RunStatus.REQUIRES_ACTION:
                        raise RuntimeError("Agent run requires tool outputs, which is not supported in this flow.")
                    if run.status != RunStatus.COMPLETED:
                        raise RuntimeError(f"Agent run finished with unexpected status {run.status}.")

                    accumulated: list[str] = []
                    async for message in client.messages.list(
                        thread_id=thread.id,
                        order=ListSortOrder.DESCENDING,
                        limit=1,
                    ):
                        for content in getattr(message, "content", []) or []:
                            raw_text: Any = None
                            if isinstance(content, dict):
                                raw_text = content.get("text")
                            else:
                                raw_text = getattr(content, "text", None)

                            text_value: str | None = None
                            if isinstance(raw_text, str):
                                text_value = raw_text
                            elif raw_text is not None:
                                value_attr = getattr(raw_text, "value", None)
                                if isinstance(value_attr, str):
                                    text_value = value_attr
                                else:
                                    text_value = str(raw_text)

                            if text_value:
                                accumulated.append(text_value)
                        break

                    return "\n".join(accumulated).strip()
                finally:
                    for stream in streams:
                        stream.close()
                    for file_id in uploaded_files:
                        try:
                            await client.files.delete(file_id=file_id)
                        except AzureError as exc:
                            logger.warning("Failed to delete uploaded file %s: %s", file_id, exc)

        return await self._with_retries("run_agent", _execute)

    async def get_agent(self, agent_id: str) -> Agent:
        async def _execute() -> Agent:
            async with self._client() as client:
                get_method = getattr(client, "get_agent", None)
                if callable(get_method):
                    return await get_method(agent_id=agent_id)

                get_method = getattr(client, "get", None)
                if callable(get_method):
                    return await get_method(agent_id=agent_id)

                raise RuntimeError("AgentsClient does not expose get_agent/get operations.")

        return await self._with_retries("get_agent", _execute)

    async def list_agents(self, *, limit: int | None = None) -> list[Agent]:
        async def _execute() -> list[Agent]:
            async with self._client() as client:
                iterator: Callable[[], Any] | None = None
                candidate = getattr(client, "list_agents", None)
                if callable(candidate):
                    iterator = candidate
                else:
                    agents_attr = getattr(client, "agents", None)
                    list_attr = getattr(agents_attr, "list", None)
                    if callable(list_attr):
                        iterator = list_attr

                if iterator is None:
                    raise RuntimeError("AgentsClient does not expose a list_agents operation.")

                results: list[Agent] = []
                produced = iterator()
                if hasattr(produced, "__aiter__"):
                    async for agent in produced:
                        results.append(agent)
                        if limit is not None and len(results) >= limit:
                            break
                else:
                    values = await produced
                    for agent in values:
                        results.append(agent)
                        if limit is not None and len(results) >= limit:
                            break
                return results

        return await self._with_retries("list_agents", _execute)
