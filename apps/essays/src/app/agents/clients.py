"""Compatibility wrapper that delegates to shared tutor_lib agent clients."""

from tutor_lib.agents.clients import (
    AgentAttachment,
    AgentRegistry,
    AgentRunContext,
    AgentSpec,
    FoundryAgentService,
)

__all__ = [
    "AgentAttachment",
    "AgentRegistry",
    "AgentRunContext",
    "AgentSpec",
    "FoundryAgentService",
]
