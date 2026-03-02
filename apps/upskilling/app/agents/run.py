"""Execution helpers for running agents."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class AgentToolkit:
    """Bundle of tools shared across agent runs."""
    tools: Iterable[Any]


class AgentRunContext:
    """Wrapper around a chat agent to provide convenience methods."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent
        self._session = self._create_session(agent)

    @staticmethod
    def _create_session(agent: Any) -> Any:
        if hasattr(agent, "create_session"):
            return agent.create_session()
        if hasattr(agent, "get_new_thread"):
            return agent.get_new_thread()
        return None

    async def run(self, message: str, **options: Any) -> Any:
        """Execute the agent with a single message and return the response."""

        try:
            if self._session is not None:
                return await self._agent.run(message, session=self._session, **options)
            return await self._agent.run(message, **options)
        except TypeError:
            if self._session is not None:
                return await self._agent.run(message, thread=self._session, **options)
            raise

    async def stream(self, message: str, **options: Any) -> AsyncIterator[str]:
        """Yield streaming text results from the agent."""

        try:
            if self._session is not None:
                stream = self._agent.run(message, stream=True, session=self._session, **options)
            else:
                stream = self._agent.run(message, stream=True, **options)

            async for update in stream:
                if getattr(update, "text", None):
                    yield update.text
            return
        except (TypeError, AttributeError):
            pass

        thread_kwargs = {"thread": self._session} if self._session is not None else {}
        async for update in self._agent.run_stream(message, **thread_kwargs, **options):
            if getattr(update, "text", None):
                yield update.text
