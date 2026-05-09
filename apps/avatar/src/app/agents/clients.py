"""Compatibility wrapper that delegates to shared tutor_lib agent contracts."""

from tutor_lib.agents import (
	AgentInvocationRequest,
	AgentInvocationResult,
	AgentReference,
	FoundryAgentFacade,
)

__all__ = [
	"AgentInvocationRequest",
	"AgentInvocationResult",
	"AgentReference",
	"FoundryAgentFacade",
]
