"""Foundry-native agent compatibility exports for the essays service."""

from .clients import (
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
