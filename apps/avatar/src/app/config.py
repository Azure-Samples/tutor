"""Configuration objects dedicated to the avatar experience."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings


load_dotenv()


def _env(name: str, default: str | None = None) -> str:
    """Return environment variable value, falling back to default when provided."""

    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is required for avatar configuration")
    return value


class AvatarCosmosSettings(BaseSettings):
    """Connection details for the avatar case container."""

    endpoint: str = Field(default_factory=lambda: _env("COSMOS_ENDPOINT"), alias="COSMOS_ENDPOINT")
    database: str = Field(default_factory=lambda: _env("COSMOS_DATABASE", "tutor"), alias="COSMOS_DATABASE")
    case_container: str = Field(
        default_factory=lambda: _env("COSMOS_AVATAR_CASE_TABLE", "avatar_case"),
        alias="COSMOS_AVATAR_CASE_TABLE",
    )


class AvatarAISettings(BaseSettings):
    """Azure AI Projects configuration required to run the avatar agent."""

    project_endpoint: str = Field(default_factory=lambda: _env("PROJECT_ENDPOINT"), alias="PROJECT_ENDPOINT")
    default_deployment: str = Field(default_factory=lambda: _env("MODEL_DEPLOYMENT_NAME", "gpt-5-nano"), alias="MODEL_DEPLOYMENT_NAME")
    temperature: float = Field(default_factory=lambda: float(_env("AVATAR_TEMPERATURE", "0.6")), alias="AVATAR_TEMPERATURE")


class AvatarSpeechSettings(BaseSettings):
    """Azure Speech configuration for AAD-based browser session brokering."""

    resource_id: str = Field(default_factory=lambda: _env("SPEECH_RESOURCE_ID"), alias="SPEECH_RESOURCE_ID")
    region: str = Field(default_factory=lambda: _env("SPEECH_REGION"), alias="SPEECH_REGION")


class AvatarSettings(BaseSettings):
    """Service-scoped settings assembled from environment variables."""

    cosmos: AvatarCosmosSettings = Field(default_factory=AvatarCosmosSettings)  # type: ignore[arg-type]
    azure_ai: AvatarAISettings = Field(default_factory=AvatarAISettings)  # type: ignore[arg-type]
    speech: AvatarSpeechSettings = Field(default_factory=AvatarSpeechSettings)  # type: ignore[arg-type]
    cors_origins: Iterable[str] = Field(default_factory=lambda: ["*"])

    model_config = {
        "arbitrary_types_allowed": True,
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> AvatarSettings:
    """Return cached settings instance to avoid repeated environment parsing."""

    return AvatarSettings()  # type: ignore[call-arg]
