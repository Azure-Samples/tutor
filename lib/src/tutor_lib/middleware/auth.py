"""Microsoft Entra ID authentication middleware and helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Iterable

import jwt
from fastapi import Depends, HTTPException, Request, status
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


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal extracted from a JWT access token."""

    subject: str
    tenant_id: str
    object_id: str
    roles: tuple[str, ...]
    claims: dict[str, Any]

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "AuthenticatedUser":
        raw_roles = claims.get("roles") or []
        if isinstance(raw_roles, str):
            roles = tuple(role.strip() for role in raw_roles.split(" ") if role.strip())
        elif isinstance(raw_roles, list):
            roles = tuple(str(role) for role in raw_roles)
        else:
            roles = tuple()

        return cls(
            subject=str(claims.get("sub", "")),
            tenant_id=str(claims.get("tid", "")),
            object_id=str(claims.get("oid", "")),
            roles=roles,
            claims=claims,
        )


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
        request.state.agent_identity = {
            "subject": user.subject,
            "tenant_id": user.tenant_id,
            "object_id": user.object_id,
            "roles": list(user.roles),
        }
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
            legacy_user_id = request.headers.get("X-User-Id", "").strip()
            if legacy_user_id:
                legacy_roles = tuple(
                    role.strip()
                    for role in request.headers.get("X-User-Roles", "professor").split(",")
                    if role.strip()
                )
                return AuthenticatedUser(
                    subject=legacy_user_id,
                    tenant_id="local-dev",
                    object_id=legacy_user_id,
                    roles=legacy_roles,
                    claims={"sub": legacy_user_id, "oid": legacy_user_id, "tid": "local-dev", "roles": list(legacy_roles)},
                )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def get_agent_identity(request: Request) -> dict[str, Any]:
    """Return a stateless identity payload that can be passed to agent runs."""

    identity = getattr(request.state, "agent_identity", None)
    if identity is None:
        user = get_authenticated_user(request)
        identity = {
            "subject": user.subject,
            "tenant_id": user.tenant_id,
            "object_id": user.object_id,
            "roles": list(user.roles),
        }
    return identity


def require_roles(*allowed_roles: str) -> Callable[..., AuthenticatedUser]:
    """FastAPI dependency factory to enforce app roles from Entra claims."""

    def dependency(request: Request) -> AuthenticatedUser:
        user = get_authenticated_user(request)
        if allowed_roles and not any(role in user.roles for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
