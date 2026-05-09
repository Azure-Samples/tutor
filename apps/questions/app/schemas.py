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
    HTTP_422_UNPROCESSABLE_ENTITY,
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


class Question(BaseModel):
    id: str = Field(..., description="Question ID")
    topic: str
    question: str
    explanation: str | None = Field(..., description="Question Explanation")


class Answer(BaseModel):
    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Answer Text")
    question_id: str = Field(..., description="Question ID")
    respondent: str = Field(..., description="Respondent Name")


class ChatResponse(BaseModel):
    """
    The response from the chatbot
    """
    case_id: str
    question: Question
    answer: Answer


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


class Grader(BaseModel):
    agent_name: str = Field(..., description="Azure AI Foundry agent name")
    agent_version: str | None = Field(None, description="Azure AI Foundry agent version")
    legacy_agent_id: str | None = Field(None, description="Legacy Azure AI Foundry agent ID")
    dimension: str = Field(default="default", description="Evaluation dimension handled by this agent")
    deployment: str = Field(default="", description="Azure AI Foundry model deployment")

    @model_validator(mode="before")
    @classmethod
    def hydrate_legacy_reference(cls, value: Any) -> Any:
        return _native_agent_payload(value, role_field="dimension")

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
            dimension=self.dimension,
            model_name=self.deployment or None,
            legacy_agent_id=self.legacy_agent_id,
            metadata={"deployment": self.deployment} if self.deployment else {},
        )


class GraderDefinition(BaseModel):
    """Payload for creating or referencing a Foundry grader agent."""

    agent_name: str | None = Field(None, description="Existing Foundry agent name (omit to create new)")
    agent_version: str | None = Field(None, description="Existing Foundry agent version")
    legacy_agent_id: str | None = Field(None, description="Existing legacy Foundry agent ID")
    name: str = Field(..., description="Evaluator name", max_length=32)
    instructions: str = Field(..., description="System prompt for the evaluator")
    deployment: str = Field(..., description="Azure AI Foundry model deployment")
    dimension: str = Field(..., description="Evaluation dimension handled by this agent")

    @model_validator(mode="before")
    @classmethod
    def hydrate_legacy_reference(cls, value: Any) -> Any:
        return _native_agent_payload(value, role_field="dimension")

    @property
    def agent_id(self) -> str | None:
        """Compatibility alias for legacy read-only callers."""

        return self.legacy_agent_id or self.agent_name

    def to_grader(self) -> Grader:
        return Grader(
            agent_name=self.agent_name or self.name,
            agent_version=self.agent_version,
            legacy_agent_id=self.legacy_agent_id,
            dimension=self.dimension,
            deployment=self.deployment,
        )


class Assembly(BaseModel):
    """
    Represents an Assemble with an id, list of judges, and roles.

    Attributes:
        id (int): The unique identifier for the assemble.
        judges (List[Judge]): A list of Judge objects.
        roles (List[str]): A list of roles.
    """

    id: str = Field(..., description="Assembly ID")
    agents: list[Grader] = Field(..., description="Judges Assemblies")
    topic_name: str = Field(..., description="Topic to Answer")


class AssemblyDefinition(BaseModel):
    """Payload for creating or updating assemblies with full grader definitions."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    agents: list[GraderDefinition] = Field(..., description="Grader agent definitions")


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
    HTTP_422_UNPROCESSABLE_ENTITY: {"model": BodyMessage},
}
