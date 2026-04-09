"""Microsoft Entra ID authentication middleware and helpers."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError, PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware

_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "/health",
    "/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/openapi.json",
)

_SCOPE_FIELDS: tuple[str, ...] = (
    "institution_ids",
    "school_ids",
    "program_ids",
    "course_ids",
    "class_ids",
    "learner_ids",
    "staff_ids",
)

_SCOPE_CLAIM_ALIASES: dict[str, tuple[str, ...]] = {
    "institution_ids": ("institution_ids", "institutionIds", "tenant_ids", "tenantIds"),
    "school_ids": ("school_ids", "schoolIds"),
    "program_ids": ("program_ids", "programIds"),
    "course_ids": ("course_ids", "courseIds"),
    "class_ids": ("class_ids", "classIds"),
    "learner_ids": ("learner_ids", "learnerIds", "student_ids", "studentIds"),
    "staff_ids": ("staff_ids", "staffIds", "professor_ids", "professorIds"),
}

_SCOPE_HEADER_ALIASES: dict[str, str] = {
    "institution_ids": "X-Institution-Ids",
    "school_ids": "X-School-Ids",
    "program_ids": "X-Program-Ids",
    "course_ids": "X-Course-Ids",
    "class_ids": "X-Class-Ids",
    "learner_ids": "X-Learner-Ids",
    "staff_ids": "X-Staff-Ids",
}

_ROLE_RELATIONSHIPS: dict[str, str] = {
    "student": "self",
    "alumni": "alumni",
    "professor": "teaching",
    "principal": "school-leadership",
    "supervisor": "school-supervision",
    "admin": "tenant-admin",
}

_ROLE_CONTEXT_PRIORITY: dict[str, tuple[tuple[str, str], ...]] = {
    "student": (
        ("learner_ids", "learner"),
        ("class_ids", "class"),
        ("program_ids", "program"),
        ("school_ids", "school"),
        ("institution_ids", "institution"),
    ),
    "alumni": (
        ("learner_ids", "learner"),
        ("program_ids", "program"),
        ("school_ids", "school"),
        ("institution_ids", "institution"),
    ),
    "professor": (
        ("class_ids", "class"),
        ("course_ids", "course"),
        ("program_ids", "program"),
        ("school_ids", "school"),
        ("institution_ids", "institution"),
    ),
    "principal": (
        ("school_ids", "school"),
        ("program_ids", "program"),
        ("institution_ids", "institution"),
    ),
    "supervisor": (
        ("school_ids", "school"),
        ("institution_ids", "institution"),
    ),
    "admin": (("institution_ids", "institution"),),
}

_DEFAULT_CONTEXT_TYPES: dict[str, str] = {
    "student": "learner",
    "alumni": "learner",
    "professor": "workspace",
    "principal": "workspace",
    "supervisor": "workspace",
    "admin": "tenant",
}


def _ordered_values(raw_values: Any, *, separators: tuple[str, ...] = (",",)) -> tuple[str, ...]:
    if raw_values is None:
        return tuple()

    if isinstance(raw_values, str):
        pieces = [raw_values]
        for separator in separators:
            next_pieces: list[str] = []
            for piece in pieces:
                next_pieces.extend(piece.split(separator))
            pieces = next_pieces
        return _deduplicate_strings(pieces)

    if isinstance(raw_values, (list, tuple, set, frozenset)):
        return _deduplicate_strings(str(item) for item in raw_values)

    return _deduplicate_strings([str(raw_values)])


def _ordered_roles(raw_roles: Any) -> tuple[str, ...]:
    if raw_roles is None:
        return tuple()
    if isinstance(raw_roles, str):
        return _deduplicate_strings(raw_roles.replace(",", " ").split())
    if isinstance(raw_roles, (list, tuple, set, frozenset)):
        return _deduplicate_strings(str(role) for role in raw_roles)
    return _deduplicate_strings([str(raw_roles)])


def _deduplicate_strings(values: Iterable[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        value = str(raw_value).strip()
        if not value or value in seen:
            continue
        ordered.append(value)
        seen.add(value)
    return tuple(ordered)


def _scope_values_from_mapping(values: Mapping[str, Any], aliases: Iterable[str]) -> tuple[str, ...]:
    for alias in aliases:
        if alias in values:
            return _ordered_values(values[alias])
    return tuple()


def _merge_scope_values(scopes: Iterable[RelationshipScope], field_name: str) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for scope in scopes:
        for value in getattr(scope, field_name):
            if value in seen:
                continue
            merged.append(value)
            seen.add(value)
    return tuple(merged)


def _humanize_identifier(identifier: str) -> str:
    cleaned = identifier.replace("_", " ").replace("-", " ").strip()
    if not cleaned:
        return "Unscoped"
    return " ".join(part.capitalize() for part in cleaned.split())


@dataclass(frozen=True)
class RelationshipScope:
    """Normalized relationship scope extracted from claims or local-dev headers."""

    institution_ids: tuple[str, ...] = tuple()
    school_ids: tuple[str, ...] = tuple()
    program_ids: tuple[str, ...] = tuple()
    course_ids: tuple[str, ...] = tuple()
    class_ids: tuple[str, ...] = tuple()
    learner_ids: tuple[str, ...] = tuple()
    staff_ids: tuple[str, ...] = tuple()

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> RelationshipScope:
        return cls(
            institution_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["institution_ids"]),
            school_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["school_ids"]),
            program_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["program_ids"]),
            course_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["course_ids"]),
            class_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["class_ids"]),
            learner_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["learner_ids"]),
            staff_ids=_scope_values_from_mapping(values, _SCOPE_CLAIM_ALIASES["staff_ids"]),
        )

    @classmethod
    def merge(cls, scopes: Iterable[RelationshipScope]) -> RelationshipScope:
        scope_list = tuple(scopes)
        if not scope_list:
            return cls()

        return cls(
            institution_ids=_merge_scope_values(scope_list, "institution_ids"),
            school_ids=_merge_scope_values(scope_list, "school_ids"),
            program_ids=_merge_scope_values(scope_list, "program_ids"),
            course_ids=_merge_scope_values(scope_list, "course_ids"),
            class_ids=_merge_scope_values(scope_list, "class_ids"),
            learner_ids=_merge_scope_values(scope_list, "learner_ids"),
            staff_ids=_merge_scope_values(scope_list, "staff_ids"),
        )

    def narrowed(self, field_name: str, value: str) -> RelationshipScope:
        return replace(self, **{field_name: (value,)})

    def as_dict(self) -> dict[str, list[str]]:
        return {field_name: list(getattr(self, field_name)) for field_name in _SCOPE_FIELDS}


@dataclass(frozen=True)
class AccessGrant:
    """Role plus relationship scope resolved for a caller."""

    role: str
    relationship: str
    scope: RelationshipScope = field(default_factory=RelationshipScope)

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "relationship": self.relationship,
            "scope": self.scope.as_dict(),
        }


@dataclass(frozen=True)
class AccessContext:
    """Stable context identifier derived from a normalized grant."""

    context_id: str
    role: str
    context_type: str
    relationship: str
    label: str
    scope: RelationshipScope = field(default_factory=RelationshipScope)

    def as_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "role": self.role,
            "context_type": self.context_type,
            "relationship": self.relationship,
            "label": self.label,
            "scope": self.scope.as_dict(),
        }


def _relationship_for_role(role: str) -> str:
    return _ROLE_RELATIONSHIPS.get(role, role)


def _scoped_grant(role: str, base_scope: RelationshipScope, *, subject: str) -> AccessGrant:
    scoped = base_scope
    if role in {"student", "alumni"} and not scoped.learner_ids and subject:
        scoped = replace(scoped, learner_ids=(subject,))
    if role in {"professor", "principal", "supervisor", "admin"} and not scoped.staff_ids and subject:
        scoped = replace(scoped, staff_ids=(subject,))

    return AccessGrant(role=role, relationship=_relationship_for_role(role), scope=scoped)


def _parse_grants_from_claims(
    claims: Mapping[str, Any],
    *,
    base_scope: RelationshipScope,
    subject: str,
) -> tuple[AccessGrant, ...]:
    raw_grants = claims.get("grants")
    if not isinstance(raw_grants, list):
        return tuple()

    grants: list[AccessGrant] = []
    for raw_grant in raw_grants:
        if not isinstance(raw_grant, Mapping):
            continue
        role = str(raw_grant.get("role", "")).strip()
        if not role:
            continue
        relationship = str(raw_grant.get("relationship") or _relationship_for_role(role)).strip()
        raw_scope = raw_grant.get("scope") if isinstance(raw_grant.get("scope"), Mapping) else raw_grant
        scope = RelationshipScope.from_mapping(raw_scope)
        if scope == RelationshipScope():
            scope = _scoped_grant(role, base_scope, subject=subject).scope
        grants.append(AccessGrant(role=role, relationship=relationship, scope=scope))

    return tuple(grants)


# Builder pattern: derive frontend-stable contexts from normalized grants so all services validate the same scope contract.
def _build_contexts_for_grant(*, subject: str, tenant_id: str, grant: AccessGrant) -> tuple[AccessContext, ...]:
    priorities = _ROLE_CONTEXT_PRIORITY.get(grant.role, tuple())
    for field_name, context_type in priorities:
        values = getattr(grant.scope, field_name)
        if not values:
            continue
        return tuple(
            AccessContext(
                context_id=f"{grant.role}:{context_type}:{value}",
                role=grant.role,
                context_type=context_type,
                relationship=grant.relationship,
                label=_humanize_identifier(value),
                scope=grant.scope.narrowed(field_name, value),
            )
            for value in values
        )

    fallback_context_type = _DEFAULT_CONTEXT_TYPES.get(grant.role, "workspace")
    fallback_value = subject or tenant_id or "default"
    fallback_label = _humanize_identifier(fallback_value) if fallback_context_type != "workspace" else f"{grant.role.title()} workspace"
    return (
        AccessContext(
            context_id=f"{grant.role}:{fallback_context_type}:{fallback_value}",
            role=grant.role,
            context_type=fallback_context_type,
            relationship=grant.relationship,
            label=fallback_label,
            scope=grant.scope,
        ),
    )


def _derive_access_contexts(*, subject: str, tenant_id: str, grants: Iterable[AccessGrant]) -> tuple[AccessContext, ...]:
    contexts: list[AccessContext] = []
    seen: set[str] = set()
    for grant in grants:
        for context in _build_contexts_for_grant(subject=subject, tenant_id=tenant_id, grant=grant):
            if context.context_id in seen:
                continue
            contexts.append(context)
            seen.add(context.context_id)
    return tuple(contexts)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal extracted from a JWT access token."""

    subject: str
    tenant_id: str
    object_id: str
    roles: tuple[str, ...]
    claims: dict[str, Any]
    scope: RelationshipScope = field(default_factory=RelationshipScope)
    grants: tuple[AccessGrant, ...] = field(default_factory=tuple)
    contexts: tuple[AccessContext, ...] = field(default_factory=tuple)
    feature_flags: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_claims(cls, claims: Mapping[str, Any]) -> AuthenticatedUser:
        normalized_claims = dict(claims)
        subject = str(normalized_claims.get("sub", ""))
        tenant_id = str(normalized_claims.get("tid", ""))
        object_id = str(normalized_claims.get("oid", ""))
        scope = RelationshipScope.from_mapping(normalized_claims)
        grants = _parse_grants_from_claims(normalized_claims, base_scope=scope, subject=subject)
        roles = _ordered_roles(normalized_claims.get("roles"))
        if not grants and roles:
            grants = tuple(_scoped_grant(role, scope, subject=subject) for role in roles)
        if not roles and grants:
            roles = _deduplicate_strings(grant.role for grant in grants)

        feature_flags = _scope_values_from_mapping(normalized_claims, ("feature_flags", "featureFlags"))
        merged_scope = RelationshipScope.merge(grant.scope for grant in grants) if grants else scope
        contexts = _derive_access_contexts(subject=subject, tenant_id=tenant_id, grants=grants)

        return cls(
            subject=subject,
            tenant_id=tenant_id,
            object_id=object_id,
            roles=roles,
            claims=normalized_claims,
            scope=merged_scope,
            grants=grants,
            contexts=contexts,
            feature_flags=feature_flags,
        )

    @classmethod
    def from_local_dev_headers(cls, headers: Mapping[str, str]) -> AuthenticatedUser | None:
        legacy_user_id = headers.get("X-User-Id", "").strip()
        if not legacy_user_id:
            return None

        roles = _ordered_roles(headers.get("X-User-Roles", "professor")) or ("professor",)
        claims: dict[str, Any] = {
            "sub": legacy_user_id,
            "oid": legacy_user_id,
            "tid": "local-dev",
            "roles": list(roles),
        }

        user_name = headers.get("X-User-Name", "").strip()
        if user_name:
            claims["name"] = user_name
        user_email = headers.get("X-User-Email", "").strip()
        if user_email:
            claims["preferred_username"] = user_email

        for field_name, header_name in _SCOPE_HEADER_ALIASES.items():
            values = _ordered_values(headers.get(header_name, ""))
            if values:
                claims[field_name] = list(values)

        if any(role in {"student", "alumni"} for role in roles) and "learner_ids" not in claims:
            claims["learner_ids"] = [legacy_user_id]
        if any(role in {"professor", "principal", "supervisor", "admin"} for role in roles) and "staff_ids" not in claims:
            claims["staff_ids"] = [legacy_user_id]

        feature_flags = _ordered_values(headers.get("X-Feature-Flags", ""))
        if feature_flags:
            claims["feature_flags"] = list(feature_flags)

        return cls.from_claims(claims)

    @property
    def default_role(self) -> str | None:
        return self.roles[0] if self.roles else None

    @property
    def display_name(self) -> str | None:
        for claim_name in ("name", "preferred_username", "email", "upn"):
            value = str(self.claims.get(claim_name, "")).strip()
            if value:
                return value
        return None

    @property
    def email(self) -> str | None:
        for claim_name in ("preferred_username", "email", "upn"):
            value = str(self.claims.get(claim_name, "")).strip()
            if value:
                return value
        return None

    def grants_for_role(self, role: str) -> tuple[AccessGrant, ...]:
        return tuple(grant for grant in self.grants if grant.role == role)

    def contexts_for_role(self, role: str) -> tuple[AccessContext, ...]:
        return tuple(context for context in self.contexts if context.role == role)


class EntraTokenValidator:
    """Validates Entra-issued JWT bearer tokens using JWKS."""

    def __init__(
        self,
        *,
        tenant_id: str,
        audience: str,
        issuer: str,
    ) -> None:
        self._audience = audience
        self._issuer = issuer
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self._jwk_client = PyJWKClient(jwks_url)

    def validate(self, token: str) -> dict[str, Any]:
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
            )
        except InvalidTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token") from exc


class EntraAuthMiddleware(BaseHTTPMiddleware):
    """Bearer-token authentication middleware for stateless APIs."""

    def __init__(
        self,
        app: Any,
        *,
        validator: EntraTokenValidator,
        allowed_client_app_ids: set[str] | None = None,
        excluded_path_prefixes: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._validator = validator
        self._allowed_client_app_ids = allowed_client_app_ids or set()
        self._excluded_path_prefixes = tuple(excluded_path_prefixes or _EXCLUDED_PREFIXES)

    def _is_excluded(self, path: str) -> bool:
        return any(path == prefix or path.startswith(f"{prefix}/") for prefix in self._excluded_path_prefixes)

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        if self._is_excluded(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Missing bearer token"})

        claims = self._validator.validate(authorization.removeprefix("Bearer ").strip())
        client_app_id = str(claims.get("azp") or claims.get("appid") or "")
        if self._allowed_client_app_ids and client_app_id not in self._allowed_client_app_ids:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Client application not allowed"})

        user = AuthenticatedUser.from_claims(claims)
        request.state.authenticated_user = user
        request.state.agent_identity = _agent_identity_from_user(user)
        return await call_next(request)


def configure_entra_auth(
    app: Any,
    *,
    enabled: bool | None = None,
    tenant_id: str | None = None,
    api_client_id: str | None = None,
    audience: str | None = None,
    issuer: str | None = None,
    allowed_client_app_ids: str | Iterable[str] | None = None,
) -> None:
    """Attach Entra authentication middleware when enabled by environment/settings."""

    is_enabled = enabled if enabled is not None else os.getenv("ENTRA_AUTH_ENABLED", "false").lower() == "true"
    if not is_enabled:
        return

    resolved_tenant_id = tenant_id or os.getenv("ENTRA_TENANT_ID", "")
    resolved_client_id = api_client_id or os.getenv("ENTRA_API_CLIENT_ID", "")
    resolved_audience = audience or os.getenv("ENTRA_TOKEN_AUDIENCE", "") or (
        f"api://{resolved_client_id}" if resolved_client_id else ""
    )
    resolved_issuer = issuer or os.getenv("ENTRA_TOKEN_ISSUER", "") or (
        f"https://login.microsoftonline.com/{resolved_tenant_id}/v2.0" if resolved_tenant_id else ""
    )

    if not resolved_tenant_id or not resolved_audience or not resolved_issuer:
        raise RuntimeError("ENTRA_AUTH_ENABLED=true requires ENTRA_TENANT_ID and ENTRA_API_CLIENT_ID (or ENTRA_TOKEN_AUDIENCE).")

    if isinstance(allowed_client_app_ids, str):
        allowed = {item.strip() for item in allowed_client_app_ids.split(",") if item.strip()}
    elif allowed_client_app_ids is None:
        allowed = {item.strip() for item in os.getenv("ENTRA_ALLOWED_CLIENT_APP_IDS", "").split(",") if item.strip()}
    else:
        allowed = {item.strip() for item in allowed_client_app_ids if item.strip()}

    app.add_middleware(
        EntraAuthMiddleware,
        validator=EntraTokenValidator(
            tenant_id=resolved_tenant_id,
            audience=resolved_audience,
            issuer=resolved_issuer,
        ),
        allowed_client_app_ids=allowed,
    )


def get_authenticated_user(request: Request) -> AuthenticatedUser:
    """Resolve the authenticated request principal."""

    user = getattr(request.state, "authenticated_user", None)
    if user is None:
        auth_enabled = os.getenv("ENTRA_AUTH_ENABLED", "false").lower() == "true"
        if not auth_enabled:
            local_dev_user = AuthenticatedUser.from_local_dev_headers(request.headers)
            if local_dev_user is not None:
                return local_dev_user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def _agent_identity_from_user(user: AuthenticatedUser) -> dict[str, Any]:
    return {
        "subject": user.subject,
        "tenant_id": user.tenant_id,
        "object_id": user.object_id,
        "roles": list(user.roles),
        "feature_flags": list(user.feature_flags),
        "scope": user.scope.as_dict(),
        "grants": [grant.as_dict() for grant in user.grants],
        "contexts": [context.as_dict() for context in user.contexts],
    }


def get_agent_identity(request: Request) -> dict[str, Any]:
    """Return a stateless identity payload that can be passed to agent runs."""

    identity = getattr(request.state, "agent_identity", None)
    if identity is None:
        user = get_authenticated_user(request)
        identity = _agent_identity_from_user(user)
    return identity


def list_access_contexts(user: AuthenticatedUser, *, role: str | None = None) -> tuple[AccessContext, ...]:
    """Return all known access contexts or the subset for a specific role."""

    if role is None:
        return user.contexts
    return user.contexts_for_role(role)


def resolve_access_context(user: AuthenticatedUser, *, role: str, context_id: str) -> AccessContext | None:
    """Resolve a role-specific context by its stable identifier."""

    for context in user.contexts_for_role(role):
        if context.context_id == context_id:
            return context
    return None


def require_roles(*allowed_roles: str) -> Callable[..., AuthenticatedUser]:
    """FastAPI dependency factory to enforce app roles from Entra claims."""

    def dependency(request: Request) -> AuthenticatedUser:
        user = get_authenticated_user(request)
        if allowed_roles and not any(role in user.roles for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
