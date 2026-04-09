"""Shared middleware package exports."""

from .auth import (
	AccessContext,
	AccessGrant,
	AuthenticatedUser,
	RelationshipScope,
	configure_entra_auth,
	get_agent_identity,
	get_authenticated_user,
	list_access_contexts,
	require_roles,
	resolve_access_context,
)

__all__ = [
	"AccessContext",
	"AccessGrant",
	"AuthenticatedUser",
	"RelationshipScope",
	"configure_entra_auth",
	"get_agent_identity",
	"get_authenticated_user",
	"list_access_contexts",
	"require_roles",
	"resolve_access_context",
]
