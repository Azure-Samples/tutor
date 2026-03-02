"""Centralised configuration management for Tutor services."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


def _env(name: str, default: str | None = None) -> str:
    """Return an environment variable or the provided default."""

    value = os.environ.get(name, default)
    if value is None:
        raise KeyError(f"Missing required environment variable: {name}")
    return value


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class CosmosConfig(BaseSettings):
    """Cosmos DB configuration shared across apps."""

    endpoint: str = Field(default_factory=lambda: _env("COSMOS_ENDPOINT"))
    key: str = Field(default_factory=lambda: _env("COSMOS_KEY"))
    database: str = Field(
        default_factory=lambda: _env("COSMOS_DATABASE", _env("COSMOS_ESSAYS_NAME", "essays"))
    )
    essay_container: str = Field(default_factory=lambda: _env("COSMOS_ESSAY_TABLE", "essays"))
    resources_container: str = Field(default_factory=lambda: _env("COSMOS_RESOURCE_TABLE", "resources"))
    assembly_container: str = Field(default_factory=lambda: _env("COSMOS_ASSEMBLY_TABLE", "assemblies"))


class AzureAIConfig(BaseSettings):
    """Azure AI Foundry configuration for agent execution."""

    project_endpoint: str = Field(default_factory=lambda: _env("PROJECT_ENDPOINT"))
    default_deployment: str = Field(default_factory=lambda: _env("MODEL_DEPLOYMENT_NAME", "gpt-4o"))
    reasoning_deployment: str = Field(default_factory=lambda: _env("MODEL_REASONING_DEPLOYMENT", "o3-mini"))
    model_key: str = Field(default_factory=lambda: _env("AZURE_MODEL_KEY", ""))
    model_url: str = Field(default_factory=lambda: _env("AZURE_MODEL_URL", ""))


class StorageConfig(BaseSettings):
    """Azure Storage configuration shared across apps."""

    connection_string: str = Field(default_factory=lambda: _env("BLOB_CONNECTION_STRING"))
    service_client: str = Field(default_factory=lambda: _env("BLOB_SERVICE_CLIENT"))


class CognitiveServicesConfig(BaseSettings):
    """Azure Cognitive Services configuration for speech and vision."""

    speech_url: str = Field(default_factory=lambda: _env("AI_SPEECH_URL"))
    speech_key: str = Field(default_factory=lambda: _env("AI_SPEECH_KEY"))
    vision_endpoint: str = Field(default_factory=lambda: _env("AZURE_VISION_ENDPOINT"))
    vision_key: str = Field(default_factory=lambda: _env("AZURE_VISION_KEY"))


class TutorSettings(BaseSettings):
    """Unified service configuration loaded from environment variables."""

    cosmos: CosmosConfig = Field(default_factory=CosmosConfig)
    azure_ai: AzureAIConfig = Field(default_factory=AzureAIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    cognitive: CognitiveServicesConfig = Field(default_factory=CognitiveServicesConfig)
    cors_origins: Iterable[str] = Field(default_factory=lambda: ["*"])

    model_config = {
        "arbitrary_types_allowed": True,
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> TutorSettings:
    """Return cached settings instance to avoid repeated environment parsing."""

    return TutorSettings()  # type: ignore[call-arg]
