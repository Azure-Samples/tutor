"""Pydantic schemas and response envelopes for the configuration service."""

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
    HTTP_418_IM_A_TEAPOT,
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
    """Standard success payload envelope."""

    title: Optional[str]
    message: Optional[str]
    content: Optional[Any]


@dataclass
class ErrorMessage:
    """Standard error payload envelope."""

    success: bool
    type: Optional[str]
    title: Optional[str]
    detail: Optional[Union[Dict[str, Union[str, List]], List[Dict[str, Union[str, List]]]]]

class ChatResponse(BaseModel):
    """
    The response from the chatbot
    """
    case_id: str
    prompt: str
    chat_history: str


class Case(BaseModel):
    name: str
    role: str
    id: Optional[str] = None
    steps: Optional[List] = None
    profile: Optional[Dict] = None
    history: Optional[List] = None


class Student(BaseModel):
    id: str
    name: str
    email: str
    class_id: str

class Professor(BaseModel):
    id: str
    name: str
    email: str
    courses: List[str] = Field(default_factory=list)

class Course(BaseModel):
    id: str
    name: str
    professor_id: str
    class_ids: List[str] = Field(default_factory=list)

class Class(BaseModel):
    id: str
    name: str
    course_id: str
    student_ids: List[str] = Field(default_factory=list)

class Group(BaseModel):
    id: str
    name: str
    class_id: str
    student_ids: List[str] = Field(default_factory=list)
    assigned_case_ids: List[str] = Field(default_factory=list)


class GroupCaseAssignment(BaseModel):
    case_ids: List[str] = Field(default_factory=list)


class ThemeInput(BaseModel):
    id: Optional[str] = None
    name: str
    objective: str
    description: str
    criteria: List[str] = Field(default_factory=list)


class BulkRosterSyncRequest(BaseModel):
    students: List[Student] = Field(default_factory=list)
    professors: List[Professor] = Field(default_factory=list)
    courses: List[Course] = Field(default_factory=list)
    classes: List[Class] = Field(default_factory=list)
    groups: List[Group] = Field(default_factory=list)


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
    422: {"model": BodyMessage},
}
