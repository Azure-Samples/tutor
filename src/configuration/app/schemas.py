"""
A package that manages the response bodies.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

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
    courses: List[str] = []

class Course(BaseModel):
    id: str
    name: str
    professor_id: str
    class_ids: List[str] = []

class Class(BaseModel):
    id: str
    name: str
    course_id: str
    student_ids: List[str] = []

class Group(BaseModel):
    id: str
    name: str
    class_id: str
    student_ids: List[str] = []
    assigned_case_ids: List[str] = []


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
