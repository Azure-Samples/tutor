"""Pydantic schemas and response envelopes for the configuration service."""

from dataclasses import dataclass
from typing import Any

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
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None


@dataclass
class SuccessMessage:
    """Standard success payload envelope."""

    title: str | None
    message: str | None
    content: Any | None


@dataclass
class ErrorMessage:
    """Standard error payload envelope."""

    success: bool
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None

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
    id: str | None = None
    steps: list | None = None
    profile: dict | None = None
    history: list | None = None


class Student(BaseModel):
    id: str
    name: str
    email: str
    class_id: str

class Professor(BaseModel):
    id: str
    name: str
    email: str
    courses: list[str] = Field(default_factory=list)

class Course(BaseModel):
    id: str
    name: str
    professor_id: str
    class_ids: list[str] = Field(default_factory=list)

class Class(BaseModel):
    id: str
    name: str
    course_id: str
    student_ids: list[str] = Field(default_factory=list)

class Group(BaseModel):
    id: str
    name: str
    class_id: str
    student_ids: list[str] = Field(default_factory=list)
    assigned_case_ids: list[str] = Field(default_factory=list)


class GroupCaseAssignment(BaseModel):
    case_ids: list[str] = Field(default_factory=list)


class ThemeInput(BaseModel):
    id: str | None = None
    name: str
    objective: str
    description: str
    criteria: list[str] = Field(default_factory=list)


class AccessScope(BaseModel):
    institution_ids: list[str] = Field(default_factory=list)
    school_ids: list[str] = Field(default_factory=list)
    program_ids: list[str] = Field(default_factory=list)
    course_ids: list[str] = Field(default_factory=list)
    class_ids: list[str] = Field(default_factory=list)
    learner_ids: list[str] = Field(default_factory=list)
    staff_ids: list[str] = Field(default_factory=list)


class AccessGrantItem(BaseModel):
    role: str
    relationship: str
    scope: AccessScope


class AccessContextItem(BaseModel):
    context_id: str
    role: str
    context_type: str
    relationship: str
    label: str
    scope: AccessScope
    workspace_path: str


class AccessRoleContext(BaseModel):
    role: str
    grants: list[AccessGrantItem] = Field(default_factory=list)
    contexts: list[AccessContextItem] = Field(default_factory=list)
    default_context_id: str | None = None


class AccessActor(BaseModel):
    subject: str
    tenant_id: str
    object_id: str
    display_name: str | None = None
    email: str | None = None


class AccessContextPayload(BaseModel):
    actor: AccessActor
    available_roles: list[str] = Field(default_factory=list)
    default_role: str | None = None
    default_context: AccessContextItem | None = None
    roles: list[AccessRoleContext] = Field(default_factory=list)
    feature_flags: list[str] = Field(default_factory=list)


class BulkRosterSyncRequest(BaseModel):
    students: list[Student] = Field(default_factory=list)
    professors: list[Professor] = Field(default_factory=list)
    courses: list[Course] = Field(default_factory=list)
    classes: list[Class] = Field(default_factory=list)
    groups: list[Group] = Field(default_factory=list)


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
