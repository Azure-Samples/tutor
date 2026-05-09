"""
A package that manages the response bodies.
"""
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, model_validator
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_301_MOVED_PERMANENTLY,
    HTTP_302_FOUND,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_418_IM_A_TEAPOT,
)
from tutor_lib.agents import AgentReference


class BodyMessage(BaseModel):
    """
    The base message body for HTTP responses
    """

    success: bool
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None


@dataclass
class SuccessMessage:
    """
    The base message body for HTTP responses
    """

    title: str | None
    message: str | None
    content: dict[str, str | list] | list[dict[str, str | list]] | None


@dataclass
class ErrorMessage:
    """
    The base message body for HTTP responses
    """

    success: bool
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None


class Essay(BaseModel):
    id: str = Field(..., description="Essay ID")
    topic: str
    content: str
    explanation: str | None = Field(None, description="Question Explanation")
    content_file_location: str | None = Field(None, description="File Location of the Essay Content, if available")
    theme: str | None = Field(
        None,
        description="Declared theme to ground the evaluation, if provided"
    )
    file_url: str | None = Field(
        None,
        description="URL of original essay file (image or selectable text), if available"
    )
    assembly_id: str | None = Field(
        None,
        description="Identifier of the assembly that should be used to evaluate this essay"
    )


class EssayPatch(BaseModel):
    """Partial update model — only explicitly provided fields are applied."""
    topic: str | None = None
    content: str | None = None
    explanation: str | None = None
    content_file_location: str | None = None
    theme: str | None = None
    file_url: str | None = None
    assembly_id: str | None = None


def _native_agent_payload(value: Any, *, role_field: str) -> Any:
    if isinstance(value, str):
        return {
            "agent_name": value,
            "legacy_agent_id": value,
            role_field: "default",
            "deployment": "",
        }
    if not isinstance(value, dict):
        return value

    payload = dict(value)
    legacy_agent_id = payload.get("legacy_agent_id") or payload.get("agent_id") or payload.get("id")
    agent_name = payload.get("agent_name") or legacy_agent_id
    if agent_name is not None:
        payload["agent_name"] = str(agent_name)
    if legacy_agent_id is not None and not payload.get("legacy_agent_id"):
        payload["legacy_agent_id"] = str(legacy_agent_id)
    if not payload.get(role_field):
        payload[role_field] = payload.get("role") or payload.get("dimension") or "default"
    if payload.get("deployment") is None:
        payload["deployment"] = ""
    return payload


class AgentDefinition(BaseModel):
    """Definition used to create or reference an Azure AI Foundry agent."""

    agent_name: str | None = Field(None, description="Existing Azure AI Foundry agent name (omit to create new)")
    agent_version: str | None = Field(None, description="Existing Azure AI Foundry agent version")
    legacy_agent_id: str | None = Field(None, description="Existing legacy Azure AI Foundry agent ID")
    name: str = Field(..., description="Friendly agent name")
    instructions: str = Field(..., description="System instructions for the agent")
    deployment: str = Field(..., description="Model deployment name registered in Azure AI Foundry")
    role: str = Field(..., description="Agent role in the assembly (e.g. analytical, narrative, default)")
    temperature: float | None = Field(
        default=None,
        description="Optional temperature override applied when the agent runs",
        ge=0.0,
        le=2.0,
    )

    @model_validator(mode="before")
    @classmethod
    def hydrate_legacy_reference(cls, value: Any) -> Any:
        return _native_agent_payload(value, role_field="role")

    @property
    def agent_id(self) -> str | None:
        """Compatibility alias for legacy read-only callers."""

        return self.legacy_agent_id or self.agent_name

    def to_agent_ref(self) -> "AgentRef":
        return AgentRef(
            agent_name=self.agent_name or self.name,
            agent_version=self.agent_version,
            legacy_agent_id=self.legacy_agent_id,
            role=self.role,
            deployment=self.deployment,
        )


class Resource(BaseModel):
    id: str = Field(..., description="Evaluation criterion ID")
    url: str | None = Field(None, description="Reference URL for the evaluation criterion (optional)")
    objective: list[str] = Field(..., description="Correction objectives (spelling, semantics, structure, argumentation, conceptual, etc.)")
    content: str | None = Field(None, description="Detailed description of the evaluation criterion")
    essay_id: str = Field(..., description="ID of the essay to which this criterion applies")
    file_name: str | None = Field(None, description="Original file name if the resource was uploaded")
    content_type: str | None = Field(None, description="MIME type describing the uploaded resource")
    encoded_content: str | None = Field(None, description="Base64 encoded payload for binary resources")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata derived from the uploaded resource")


class ChatResponse(BaseModel):
    """
    The response from the chatbot
    """
    case_id: str
    essay: Essay
    resources: list[Resource]


class AgentRef(BaseModel):
    """Lightweight reference to an agent registered in Azure AI Foundry."""

    agent_name: str = Field(..., description="Azure AI Foundry agent name")
    agent_version: str | None = Field(None, description="Azure AI Foundry agent version")
    legacy_agent_id: str | None = Field(None, description="Legacy Azure AI Foundry agent ID")
    role: str = Field(..., description="Agent role in the assembly (e.g. analytical, narrative, default)")
    deployment: str = Field(..., description="Model deployment name")

    @model_validator(mode="before")
    @classmethod
    def hydrate_legacy_reference(cls, value: Any) -> Any:
        return _native_agent_payload(value, role_field="role")

    @property
    def agent_id(self) -> str:
        """Compatibility alias for legacy read-only callers."""

        return self.legacy_agent_id or self.agent_name

    @property
    def id(self) -> str:
        """Compatibility alias for legacy assembly documents."""

        return self.agent_id

    def to_agent_reference(self) -> AgentReference:
        return AgentReference(
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            role=self.role,
            model_name=self.deployment or None,
            legacy_agent_id=self.legacy_agent_id,
            metadata={"deployment": self.deployment} if self.deployment else {},
        )


class Assembly(BaseModel):
    """Represents an assembly stored in Cosmos DB with its agent references."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    agents: list[AgentRef] = Field(..., description="Agent references provisioned in Foundry")
    essay_id: str = Field(..., description="Essay identifier evaluated by this assembly")


class AssemblyDefinition(BaseModel):
    """Payload used to create or update an assembly along with its agent definitions."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    essay_id: str = Field(..., description="Essay identifier evaluated by this assembly")
    agents: list[AgentDefinition] = Field(..., description="Agent definitions for Azure AI Foundry agents")


RESPONSES = {
    HTTP_200_OK: {"model": BodyMessage},
    HTTP_201_CREATED: {"model": BodyMessage},
    HTTP_202_ACCEPTED: {"model": BodyMessage},
    HTTP_302_FOUND: {"model": BodyMessage},
    HTTP_301_MOVED_PERMANENTLY: {"model": BodyMessage},
    HTTP_307_TEMPORARY_REDIRECT: {"model": BodyMessage},
    HTTP_400_BAD_REQUEST: {"model": BodyMessage},
    HTTP_401_UNAUTHORIZED: {"model": BodyMessage},
    HTTP_403_FORBIDDEN: {"model": BodyMessage},
    HTTP_418_IM_A_TEAPOT: {"model": BodyMessage},
}
