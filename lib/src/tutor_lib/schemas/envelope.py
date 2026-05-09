from __future__ import annotations

from pydantic import BaseModel


class ApiEnvelope[T](BaseModel):
    success: bool = True
    data: T
    message: str | None = None
