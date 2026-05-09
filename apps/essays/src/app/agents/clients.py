"""Compatibility wrapper that delegates to shared tutor_lib agent contracts."""

from tutor_lib.agents import (
    AgentAttachment,
    AgentInvocationRequest,
    AgentInvocationResult,
    AgentReference,
    FoundryAgentFacade,
)

__all__ = [
    "AgentAttachment",
    "AgentInvocationRequest",
    "AgentInvocationResult",
    "AgentReference",
    "FoundryAgentFacade",
]
