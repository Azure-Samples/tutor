"""
A package that manages the response bodies.
"""
from dataclasses import dataclass

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

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
    HTTP_418_IM_A_TEAPOT
)


class BodyMessage(BaseModel):
    """
    The base message body for HTTP responses
    """

    success: bool
    type: Optional[str]
    title: Optional[str]
    detail: Optional[Union[Dict[str, Union[str, List]], List[Dict[str, Union[str, List]]]]]


@dataclass
class SuccessMessage:
    """
    The base message body for HTTP responses
    """

    title: Optional[str]
    message: Optional[str]
    content: Optional[Union[Dict[str, Union[str, List]], List[Dict[str, Union[str, List]]]]]


@dataclass
class ErrorMessage:
    """
    The base message body for HTTP responses
    """

    success: bool
    type: Optional[str]
    title: Optional[str]
    detail: Optional[Union[Dict[str, Union[str, List]], List[Dict[str, Union[str, List]]]]]


class Essay(BaseModel):
    id: str = Field(..., description="Essay ID")
    topic: str
    content: str
    explanation: Optional[str] = Field(None, description="Question Explanation")
    content_file_location: Optional[str] = Field(None, description="File Location of the Essay Content, if available")
    theme: Optional[str] = Field(
        None,
        description="Declared theme to ground the evaluation, if provided"
    )
    file_url: Optional[str] = Field(
        None,
        description="URL of original essay file (image or selectable text), if available"
    )
    assembly_id: Optional[str] = Field(
        None,
        description="Identifier of the assembly that should be used to evaluate this essay"
    )


class EssayPatch(BaseModel):
    """Partial update model — only explicitly provided fields are applied."""
    topic: Optional[str] = None
    content: Optional[str] = None
    explanation: Optional[str] = None
    content_file_location: Optional[str] = None
    theme: Optional[str] = None
    file_url: Optional[str] = None
    assembly_id: Optional[str] = None


class AgentDefinition(BaseModel):
    """Definition of an Azure AI Foundry agent used within a swarm."""

    id: Optional[str] = Field(None, description="Existing Azure AI Foundry agent ID")
    name: str = Field(..., description="Friendly agent name")
    instructions: str = Field(..., description="System instructions for the agent")
    deployment: str = Field(..., description="Model deployment name registered in Azure AI Foundry")
    temperature: Optional[float] = Field(
        default=None,
        description="Optional temperature override applied when the agent runs",
        ge=0.0,
        le=2.0,
    )


class Resource(BaseModel):
    id: str = Field(..., description="Evaluation criterion ID")
    url: Optional[str] = Field(None, description="Reference URL for the evaluation criterion (optional)")
    objective: List[str] = Field(..., description="Correction objectives (spelling, semantics, structure, argumentation, conceptual, etc.)")
    content: Optional[str] = Field(None, description="Detailed description of the evaluation criterion")
    essay_id: str = Field(..., description="ID of the essay to which this criterion applies")
    file_name: Optional[str] = Field(None, description="Original file name if the resource was uploaded")
    content_type: Optional[str] = Field(None, description="MIME type describing the uploaded resource")
    encoded_content: Optional[str] = Field(None, description="Base64 encoded payload for binary resources")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata derived from the uploaded resource")


class ChatResponse(BaseModel):
    """
    The response from the chatbot
    """
    case_id: str
    essay: Essay
    resources: list[Resource]


class AgentRef(AgentDefinition):
    """Reference to an agent provisioned in Azure AI Foundry."""

    id: str = Field(..., description="Azure AI Foundry agent ID")


class Assembly(BaseModel):
    """Represents an assembly stored in Cosmos DB with its agent references."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    agents: List[AgentRef] = Field(..., description="Agent references provisioned in Foundry")
    essay_id: str = Field(..., description="Essay identifier evaluated by this assembly")


class AssemblyDefinition(BaseModel):
    """Payload used to create or update an assembly along with its agent definitions."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    essay_id: str = Field(..., description="Essay identifier evaluated by this assembly")
    agents: List[AgentDefinition] = Field(..., description="Agent definitions for Azure AI Foundry agents")


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
