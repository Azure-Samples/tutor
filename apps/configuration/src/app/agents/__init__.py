"""Foundry-native agent compatibility exports for the configuration service."""

from .clients import (
    AgentAttachment,
    AgentInvocationRequest,
    AgentInvocationResult,
    AgentReference,
    FoundryAgentFacade,
)
from .run import AgentToolkit

__all__ = [
    "AgentAttachment",
    "AgentInvocationRequest",
    "AgentInvocationResult",
    "AgentReference",
    "AgentToolkit",
    "FoundryAgentFacade",
]
