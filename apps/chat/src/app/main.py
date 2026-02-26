"""FastAPI surface for the guided tutoring chat service."""

from __future__ import annotations

from pydantic import BaseModel
from tutor_lib.config import create_app

app = create_app(
    title="Chat",
    version="0.1.0",
    description="Guided tutoring chat service for writing support.",
)


class GuidanceRequest(BaseModel):
    student_id: str
    course_id: str
    prompt: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat/guide")
async def guide(payload: GuidanceRequest) -> dict[str, str]:
    return {
        "student_id": payload.student_id,
        "course_id": payload.course_id,
        "guidance": "Draft your main argument first, then add evidence from your notes.",
    }
