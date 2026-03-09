"""FastAPI surface for the guided tutoring chat service."""

from __future__ import annotations

from fastapi import HTTPException
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
    prompt: str | None = None
    message: str | None = None


def _resolve_prompt(payload: GuidanceRequest) -> str:
    text = (payload.prompt or payload.message or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Either 'prompt' or 'message' is required")
    return text


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/guide")
@app.post("/chat/guide")
async def guide(payload: GuidanceRequest) -> dict[str, str]:
    prompt = _resolve_prompt(payload)
    return {
        "student_id": payload.student_id,
        "course_id": payload.course_id,
        "prompt": prompt,
        "guidance": "Draft your main argument first, then add evidence from your notes.",
    }
