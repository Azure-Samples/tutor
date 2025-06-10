"""
A package that manages the response bodies.
"""
import json
from dataclasses import dataclass

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, field_validator, Field

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
    """
    Represents a Grader with an id, model, url, and metaprompt.

    Attributes:
        id (str): The unique identifier for the judge.
        model (HttpUrl): The model name of the judge.
        metaprompt (str): The metaprompt for the judge.
    """

    id: str = Field(..., description="Judge ID")
    name: str = Field(..., description="Judge Name", max_length=16)
    model_id: str = Field(..., description="Model ID")
    metaprompt: str = Field(..., description="Grader System Prompt Parameters")
    description: Optional[str] = Field(None, description="Description of the Grader, if available")

    @classmethod
    @field_validator("model")
    def model_must_be_azure_url(cls, v):
        if not v.startswith("https://"):
            raise ValueError("model must be a URL from Azure Open AI")
        return v

    @classmethod
    @field_validator("metaprompt")
    def metaprompt_must_be_json_serializable(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as jexc:
            raise ValueError("metaprompt must be JSON serializable") from jexc
        if not ("text" in v and "json" in v):
            raise ValueError("metaprompt must contain the format (text, json)")
        return v


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
