"""Execution helpers for invoking Foundry-native agent commands."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from tutor_lib.agents import AgentInvocationRequest, AgentInvocationResult, FoundryAgentFacade


@dataclass(slots=True)
class AgentToolkit:
    """Bundle of tools shared across agent runs."""
    tools: Iterable[Any]


class AgentInvocationRunner:
    """Small adapter around the shared Foundry facade."""

    def __init__(self, facade: FoundryAgentFacade) -> None:
        self._facade = facade

    async def invoke(self, request: AgentInvocationRequest) -> AgentInvocationResult:
        """Invoke the shared facade with a Tutor command object."""

        return await self._facade.invoke(request)
