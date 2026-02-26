"""Configuration for LMS Gateway provider integrations."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class LMSGatewaySettings(BaseSettings):
    moodle_base_url: str = Field(default="", alias="LMS_MOODLE_BASE_URL")
    moodle_token: str = Field(default="", alias="LMS_MOODLE_TOKEN")
    canvas_base_url: str = Field(default="", alias="LMS_CANVAS_BASE_URL")
    canvas_token: str = Field(default="", alias="LMS_CANVAS_TOKEN")


@lru_cache(maxsize=1)
def get_lms_settings() -> LMSGatewaySettings:
    return LMSGatewaySettings()  # type: ignore[call-arg]
