"""Pydantic schemas and response envelopes for the avatar service."""

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
    HTTP_422_UNPROCESSABLE_ENTITY,
)


class BodyMessage(BaseModel):
    """Baseline message payload for error responses."""

    success: bool
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None


@dataclass
class SuccessMessage:
    """Standard envelope for successful responses."""

    title: str | None
    message: str | None
    content: Any | None


@dataclass
class ErrorMessage:
    """Standard envelope for error responses."""

    success: bool
    type: str | None
    title: str | None
    detail: dict[str, str | list] | list[dict[str, str | list]] | None


class ChatResponse(BaseModel):
    """Request payload for avatar chat interactions."""

    case_id: str
    prompt: str
    chat_history: str | list[dict[str, str]] | None = None


class Case(BaseModel):
    id: str | None = None
    name: str
    role: str
    steps: list[Any] = Field(default_factory=list)
    profile: dict[str, Any] = Field(default_factory=dict)
    history: list[Any] = Field(default_factory=list)


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
