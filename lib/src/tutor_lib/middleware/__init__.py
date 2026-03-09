"""Shared middleware package exports."""

from .auth import (
	AuthenticatedUser,
	configure_entra_auth,
	get_agent_identity,
	get_authenticated_user,
	require_roles,
)

__all__ = [
	"AuthenticatedUser",
	"configure_entra_auth",
	"get_agent_identity",
	"get_authenticated_user",
	"require_roles",
]
