"""Typed essays settings adapter backed by shared tutor settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from tutor_lib.config import get_settings as get_shared_settings


class CosmosConfig(BaseModel):
    endpoint: str
    database: str
    essay_container: str
    resources_container: str
    assembly_container: str


class AzureAIConfig(BaseModel):
    project_endpoint: str
    default_deployment: str
    reasoning_deployment: str


class TutorSettings(BaseSettings):
    cosmos: CosmosConfig
    azure_ai: AzureAIConfig
    cors_origins: Iterable[str] = Field(default_factory=lambda: ["*"])

    model_config = {
        "arbitrary_types_allowed": True,
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> TutorSettings:
    shared = get_shared_settings()
    return TutorSettings(
        cosmos=CosmosConfig(
            endpoint=shared.cosmos.endpoint,
            database=shared.cosmos.database,
            essay_container=shared.cosmos.essay_container,
            resources_container=shared.cosmos.resources_container,
            assembly_container=shared.cosmos.assembly_container,
        ),
        azure_ai=AzureAIConfig(
            project_endpoint=shared.azure_ai.project_endpoint,
            default_deployment=shared.azure_ai.default_deployment,
            reasoning_deployment=shared.azure_ai.reasoning_deployment,
        ),
        cors_origins=shared.cors_origins,
    )
