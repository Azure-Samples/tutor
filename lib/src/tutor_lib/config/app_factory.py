"""Shared FastAPI app factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import get_settings
from tutor_lib.middleware import configure_entra_auth


def create_app(*, title: str, version: str, description: str, openapi_url: str = "/api/v1/openapi.json") -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=title, version=version, description=description, openapi_url=openapi_url)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_origin_regex=r"https://.*\.azurestaticapps\.net",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    configure_entra_auth(
        app,
        enabled=settings.auth.enabled,
        tenant_id=settings.auth.tenant_id,
        api_client_id=settings.auth.api_client_id,
        audience=settings.auth.token_audience,
        issuer=settings.auth.token_issuer,
        allowed_client_app_ids=settings.auth.allowed_client_app_ids,
    )
    return app
