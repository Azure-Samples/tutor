"""FastAPI surface for the configuration service."""

from __future__ import annotations

from functools import lru_cache
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cosmos import CosmosCRUD
from app.schemas import (
    BulkRosterSyncRequest,
    RESPONSES,
    BodyMessage,
    Class,
    Course,
    ErrorMessage,
    Group,
    GroupCaseAssignment,
    Professor,
    Student,
    SuccessMessage,
    ThemeInput,
)
from tutor_lib.config import get_settings
from tutor_lib.middleware import configure_entra_auth, require_roles


settings = get_settings()

app = FastAPI(
    title="Configuration",
    version="2.0.0",
    description="Roster management and case assignment service",
    openapi_tags=[
        {"name": "Students", "description": "Student roster management"},
        {"name": "Professors", "description": "Faculty roster management"},
        {"name": "Courses", "description": "Course catalog"},
        {"name": "Classes", "description": "Class sections"},
        {"name": "Groups", "description": "Study group and case assignment"},
        {"name": "Themes", "description": "Essay theme and rubric configuration"},
    ],
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore[arg-type]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=r"https://.*\.azurestaticapps\.net",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
configure_entra_auth(app)


@app.get("/health", tags=["Students"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["Students"])
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@lru_cache(maxsize=8)
def _crud(container: str) -> CosmosCRUD:
    return CosmosCRUD(container, settings.cosmos)


def _success(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    body = BodyMessage(
        success=False,
        type="validation",
        title="Invalid request payload",
        detail={"invalid-params": list(exc.errors())},
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder(body))


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    body = ErrorMessage(
        success=False,
        type="internal",
        title="Unexpected error",
        detail={"message": str(exc)},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(body))


require_professor = require_roles("professor", "admin")
THEME_KIND = "theme"


async def _bulk_create(container: str, items: list[dict[str, Any]]) -> int:
    crud = _crud(container)
    for item in items:
        await crud.create_item(item)
    return len(items)


def _theme_document(payload: ThemeInput, theme_id: str) -> dict[str, Any]:
    return {
        "id": theme_id,
        "kind": THEME_KIND,
        "name": payload.name,
        "objective": payload.objective,
        "description": payload.description,
        "criteria": payload.criteria,
    }


@app.post("/students", tags=["Students"])
async def create_student(student: Student, _: str = Depends(require_professor)) -> JSONResponse:
    await _crud(settings.cosmos.student_container).create_item(student.model_dump())
    return _success("Student Created", "Student stored", student.model_dump())


@app.get("/students", tags=["Students"])
async def list_students(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.student_container).list_items()
    return _success("Students Retrieved", "Students fetched", items)


@app.post("/professors", tags=["Professors"])
async def create_professor(professor: Professor, _: str = Depends(require_professor)) -> JSONResponse:
    await _crud(settings.cosmos.professor_container).create_item(professor.model_dump())
    return _success("Professor Created", "Professor stored", professor.model_dump())


@app.get("/professors", tags=["Professors"])
async def list_professors(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.professor_container).list_items()
    return _success("Professors Retrieved", "Professors fetched", items)


@app.post("/courses", tags=["Courses"])
async def create_course(course: Course, _: str = Depends(require_professor)) -> JSONResponse:
    await _crud(settings.cosmos.course_container).create_item(course.model_dump())
    return _success("Course Created", "Course stored", course.model_dump())


@app.get("/courses", tags=["Courses"])
async def list_courses(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.course_container).list_items()
    return _success("Courses Retrieved", "Courses fetched", items)


@app.post("/classes", tags=["Classes"])
async def create_class(class_: Class, _: str = Depends(require_professor)) -> JSONResponse:
    await _crud(settings.cosmos.class_container).create_item(class_.model_dump())
    return _success("Class Created", "Class stored", class_.model_dump())


@app.get("/classes", tags=["Classes"])
async def list_classes(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.class_container).list_items()
    return _success("Classes Retrieved", "Classes fetched", items)


@app.post("/groups", tags=["Groups"])
async def create_group(group: Group, _: str = Depends(require_professor)) -> JSONResponse:
    await _crud(settings.cosmos.group_container).create_item(group.model_dump())
    return _success("Group Created", "Group stored", group.model_dump())


@app.get("/groups", tags=["Groups"])
async def list_groups(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.group_container).list_items()
    return _success("Groups Retrieved", "Groups fetched", items)


@app.get("/themes", tags=["Themes"])
async def list_themes(_: str = Depends(require_professor)) -> JSONResponse:
    items = await _crud(settings.cosmos.configuration_container).list_items()
    themes = [item for item in items if item.get("kind") == THEME_KIND]
    return _success("Themes Retrieved", "Themes fetched", themes)


@app.post("/themes", tags=["Themes"])
async def create_theme(theme: ThemeInput, _: str = Depends(require_professor)) -> JSONResponse:
    theme_id = theme.id or str(uuid4())
    payload = _theme_document(theme, theme_id)
    await _crud(settings.cosmos.configuration_container).create_item(payload)
    return _success("Theme Created", "Theme stored", payload)


@app.get("/themes/{theme_id}", tags=["Themes"])
async def get_theme(theme_id: str, _: str = Depends(require_professor)) -> JSONResponse:
    try:
        item = await _crud(settings.cosmos.configuration_container).read_item(theme_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found") from exc

    if item.get("kind") != THEME_KIND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")

    return _success("Theme Retrieved", "Theme fetched", item)


@app.put("/themes/{theme_id}", tags=["Themes"])
async def update_theme(theme_id: str, theme: ThemeInput, _: str = Depends(require_professor)) -> JSONResponse:
    crud = _crud(settings.cosmos.configuration_container)
    try:
        existing = await crud.read_item(theme_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found") from exc

    if existing.get("kind") != THEME_KIND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")

    payload = {**existing, **_theme_document(theme, theme_id)}
    await crud.update_item(theme_id, payload)
    return _success("Theme Updated", "Theme modified", payload)


@app.delete("/themes/{theme_id}", tags=["Themes"])
async def delete_theme(theme_id: str, _: str = Depends(require_professor)) -> JSONResponse:
    crud = _crud(settings.cosmos.configuration_container)
    try:
        existing = await crud.read_item(theme_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found") from exc

    if existing.get("kind") != THEME_KIND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")

    await crud.delete_item(theme_id)
    return _success("Theme Deleted", "Theme removed", {"theme_id": theme_id})


@app.post("/groups/{group_id}/assign-cases", tags=["Groups"])
async def assign_cases_to_group(
    group_id: str,
    assignment: GroupCaseAssignment,
    _: str = Depends(require_professor),
) -> JSONResponse:
    crud = _crud(settings.cosmos.group_container)
    try:
        group = await crud.read_item(group_id)
    except Exception as exc:  # noqa: BLE001 - surface 404 for missing groups
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found") from exc

    group["assigned_case_ids"] = assignment.case_ids
    await crud.update_item(group_id, group)
    return _success("Group Updated", "Cases assigned", group)


@app.post("/lms/bulk-sync", tags=["Groups", "Students", "Professors", "Courses", "Classes"])
async def bulk_sync_roster(
    payload: BulkRosterSyncRequest,
    _: str = Depends(require_professor),
) -> JSONResponse:
    students = [item.model_dump() for item in payload.students]
    professors = [item.model_dump() for item in payload.professors]
    courses = [item.model_dump() for item in payload.courses]
    classes = [item.model_dump() for item in payload.classes]
    groups = [item.model_dump() for item in payload.groups]

    counts = {
        "students": await _bulk_create(settings.cosmos.student_container, students),
        "professors": await _bulk_create(settings.cosmos.professor_container, professors),
        "courses": await _bulk_create(settings.cosmos.course_container, courses),
        "classes": await _bulk_create(settings.cosmos.class_container, classes),
        "groups": await _bulk_create(settings.cosmos.group_container, groups),
    }

    return _success("Bulk Sync Completed", "Roster synchronized", counts)
