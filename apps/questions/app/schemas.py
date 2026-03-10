"""
A package that manages the response bodies.
"""
from dataclasses import dataclass

from typing import Dict, List, Optional, Union
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
    HTTP_418_IM_A_TEAPOT,
    HTTP_422_UNPROCESSABLE_ENTITY,
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


class Question(BaseModel):
    id: str = Field(..., description="Question ID")
    topic: str
    question: str
    explanation: Optional[str] = Field(..., description="Question Explanation")


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


class Grader(BaseModel):
    agent_id: str = Field(..., description="Azure AI Foundry agent ID")
    dimension: str = Field(..., description="Evaluation dimension handled by this agent")
    deployment: str = Field(..., description="Azure AI Foundry model deployment")


class GraderDefinition(BaseModel):
    """Payload for creating or referencing a Foundry grader agent."""

    agent_id: Optional[str] = Field(None, description="Existing Foundry agent ID (omit to create new)")
    name: str = Field(..., description="Evaluator name", max_length=32)
    instructions: str = Field(..., description="System prompt for the evaluator")
    deployment: str = Field(..., description="Azure AI Foundry model deployment")
    dimension: str = Field(..., description="Evaluation dimension handled by this agent")


class Assembly(BaseModel):
    """
    Represents an Assemble with an id, list of judges, and roles.

    Attributes:
        id (int): The unique identifier for the assemble.
        judges (List[Judge]): A list of Judge objects.
        roles (List[str]): A list of roles.
    """

    id: str = Field(..., description="Assembly ID")
    agents: List[Grader] = Field(..., description="Judges Assemblies")
    topic_name: str = Field(..., description="Topic to Answer")


class AssemblyDefinition(BaseModel):
    """Payload for creating or updating assemblies with full grader definitions."""

    id: str = Field(..., description="Assembly ID")
    topic_name: str = Field(..., description="Topic to Answer")
    agents: List[GraderDefinition] = Field(..., description="Grader agent definitions")


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
