"""Execution helpers for running agents."""

from __future__ import annotations

import asyncio
import agent_framework as _af
from typing import Any

_Agent = getattr(_af, "Agent", getattr(_af, "ChatAgent", None))

AgentType = Any


class AgentRunContext:
    """Wrapper around a ChatAgent to provide convenience methods."""

    def __init__(self, agent: AgentType) -> None:
        self._agent = agent

    async def run(self, message: str, **kwargs: Any) -> Any:
        """Execute the agent with a single message and return the response."""
        result = self._agent.run(message, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result
