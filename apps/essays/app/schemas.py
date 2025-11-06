"""
A package that manages the response bodies.
"""
import json
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


class Essay(BaseModel):
    id: str = Field(..., description="Question ID")
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


class Resource(BaseModel):
    id: str = Field(..., description="Evaluation criterion ID")
    url: Optional[str] = Field(None, description="Reference URL for the evaluation criterion (optional)")
    objective: List[str] = Field(..., description="Correction objectives (spelling, semantics, structure, argumentation, conceptual, etc.)")
    content: Optional[str] = Field(None, description="Detailed description of the evaluation criterion")
    essay_id: str = Field(..., description="ID of the essay to which this criterion applies")


class ChatResponse(BaseModel):
    """
    The response from the chatbot
    """
    case_id: str
    essay: Essay
    resources: list[Resource]


class Evaluator(BaseModel):
    id: str = Field(..., description="Evaluator ID")
    name: str = Field(..., description="Evaluator name", max_length=32)
    deployment: str = Field(..., description="Azure AI Foundry model deployment to use")
    instructions: str = Field(..., description="System prompt for the evaluator")
    description: Optional[str] = Field(None, description="Optional human readable description")


class Swarm(BaseModel):
    """
    Represents an Assemble with an id, list of judges, and roles.

    Attributes:
        id (int): The unique identifier for the assemble.
        judges (List[Judge]): A list of Judge objects.
        roles (List[str]): A list of roles.
    """

    id: str = Field(..., description="Assembly ID")
    agents: List[Evaluator] = Field(..., description="Judges Assemblies")
    topic_name: str = Field(..., description="Topic to Answer")


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
