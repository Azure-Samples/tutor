"""Centralized configuration management for Tutor services."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from pydantic import Field
from pydantic_settings import BaseSettings


class CosmosConfig(BaseSettings):
    endpoint: str = Field(alias="COSMOS_ENDPOINT")
    database: str = Field(alias="COSMOS_DATABASE", default="tutor")
    essay_container: str = Field(alias="COSMOS_ESSAY_TABLE", default="essays")
    question_container: str = Field(alias="COSMOS_QUESTION_TABLE", default="questions")
    answer_container: str = Field(alias="COSMOS_ANSWER_TABLE", default="answers")
    configuration_container: str = Field(alias="COSMOS_CONFIGURATION_TABLE", default="configuration")
    resources_container: str = Field(alias="COSMOS_RESOURCE_TABLE", default="resources")
    grader_container: str = Field(alias="COSMOS_GRADER_TABLE", default="graders")
    assembly_container: str = Field(alias="COSMOS_ASSEMBLY_TABLE", default="assemblies")
    student_container: str = Field(alias="COSMOS_STUDENT_TABLE", default="students")
    professor_container: str = Field(alias="COSMOS_PROFESSOR_TABLE", default="professors")
    course_container: str = Field(alias="COSMOS_COURSE_TABLE", default="courses")
    class_container: str = Field(alias="COSMOS_CLASS_TABLE", default="classes")
    group_container: str = Field(alias="COSMOS_GROUP_TABLE", default="groups")
    avatar_case_container: str = Field(alias="COSMOS_AVATAR_CASE_TABLE", default="avatar_case")
    upskilling_container: str = Field(alias="COSMOS_UPSKILLING_TABLE", default="upskilling_plans")


class AzureAIConfig(BaseSettings):
    project_endpoint: str = Field(alias="PROJECT_ENDPOINT")
    default_deployment: str = Field(alias="MODEL_DEPLOYMENT_NAME", default="gpt-4o")
    reasoning_deployment: str = Field(alias="MODEL_REASONING_DEPLOYMENT", default="o3-mini")


class StorageConfig(BaseSettings):
    blob_connection: str = Field(alias="BLOB_CONNECTION_STRING")
    container_name: str = Field(alias="BLOB_CONTAINER_NAME", default="uploads")


class AuthConfig(BaseSettings):
    enabled: bool = Field(alias="ENTRA_AUTH_ENABLED", default=False)
    tenant_id: str = Field(alias="ENTRA_TENANT_ID", default="")
    api_client_id: str = Field(alias="ENTRA_API_CLIENT_ID", default="")
    token_audience: str = Field(alias="ENTRA_TOKEN_AUDIENCE", default="")
    token_issuer: str = Field(alias="ENTRA_TOKEN_ISSUER", default="")
    allowed_client_app_ids: str = Field(alias="ENTRA_ALLOWED_CLIENT_APP_IDS", default="")
    teacher_client_id: str = Field(alias="ENTRA_TEACHER_CLIENT_ID", default="")
    teacher_client_secret: str = Field(alias="ENTRA_TEACHER_CLIENT_SECRET", default="")
    student_secret_salt: str = Field(alias="STUDENT_SECRET_SALT", default="")


class TutorSettings(BaseSettings):
    cosmos: CosmosConfig = CosmosConfig()  # type: ignore[arg-type]
    azure_ai: AzureAIConfig = AzureAIConfig()  # type: ignore[arg-type]
    storage: StorageConfig | None = None
    auth: AuthConfig = AuthConfig()  # type: ignore[arg-type]
    cors_origins: Iterable[str] = Field(default_factory=lambda: ["*"])

    model_config = {
        "arbitrary_types_allowed": True,
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> TutorSettings:
    return TutorSettings()  # type: ignore[call-arg]
