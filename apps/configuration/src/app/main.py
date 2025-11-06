"""FastAPI surface for the configuration service."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cosmos_crud import CosmosCRUD
from app.schemas import (
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
)
from common.config import get_settings


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
    ],
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore[arg-type]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def get_current_user(request: Request) -> str:
    user = request.headers.get("X-User-Id")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_professor(user: str = Depends(get_current_user)) -> str:
    return user


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
