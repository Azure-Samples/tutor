"""
The configuration for the web api.
"""

import os

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from azure.identity import DefaultAzureCredential

from app.schemas import (
    RESPONSES,
    BodyMessage,
    Student,
    Professor,
    Course,
    Class,
    Group
)

from app.cosmos_crud import CosmosCRUD


load_dotenv(find_dotenv())

BLOB_CONN = os.getenv("BLOB_CONNECTION_STRING", "")
MODEL_URL: str = os.environ.get("GPT4O_URL", "")
MODEL_KEY: str = os.environ.get("GPT4O_KEY", "")
MONITOR: str = os.environ.get("AZ_CONNECTION_LOG", "")
DEFAULT_CREDENTIAL = DefaultAzureCredential()
GPT4_KEY = os.getenv("GPT4O_KEY", "")
GPT4_URL = os.getenv("GPT4O_URL", "")
MODEL_URL: str = os.environ.get("GPT4_URL", "")
MODEL_KEY: str = os.environ.get("GPT4_KEY", "")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


tags_metadata: list[dict] = [
    {
        "name": "Avatar",
        "description": """Endpoints de gerenciamento de dados do Avatar.""",
    },
    {
        "name": "Config",
        "description": """Endpoints de configuração e gerenciamento.""",
    },
]

description: str = """
    Uma API Web para gerenciar o avatar.
"""


app: FastAPI = FastAPI(
    title="Avatar",
    version="Alpha",
    description=description,
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError  # pylint: disable=unused-argument
) -> JSONResponse:
    """
    validation_exception_handler Exception handler for validations.

    Args:
        request (Request): the request from the api
        exc (RequestValidationError): the validation raised by the process

    Returns:
        JSONResponse: A json encoded response with the validation errors.
    """

    response_body: BodyMessage = BodyMessage(
        success=False,
        type="Validation Error",
        title="Your request parameters didn't validate.",
        detail={"invalid-params": list(exc.errors())},
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(response_body),
    )


# --- Session and Permission Validation Stubs ---
def get_current_user(request: Request):
    # Session validation stub
    user = request.headers.get("X-User-Id")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_professor(user=Depends(get_current_user)):
    # Permission check stub
    return user


# --- CRUD Endpoints ---
STUDENT_TABLE = "COSMOS_STUDENT_TABLE"
PROFESSOR_TABLE = "COSMOS_PROFESSOR_TABLE"
COURSE_TABLE = "COSMOS_COURSE_TABLE"
CLASS_TABLE = "COSMOS_CLASS_TABLE"
GROUP_TABLE = "COSMOS_GROUP_TABLE"

student_crud = CosmosCRUD(STUDENT_TABLE)
professor_crud = CosmosCRUD(PROFESSOR_TABLE)
course_crud = CosmosCRUD(COURSE_TABLE)
class_crud = CosmosCRUD(CLASS_TABLE)
group_crud = CosmosCRUD(GROUP_TABLE)

@app.post("/students", tags=["Config"], response_model=Student)
async def create_student(student: Student, user=Depends(require_professor)):
    await student_crud.create_item(student.model_dump())
    return student

@app.get("/students", tags=["Config"], response_model=list[Student])
async def list_students(user=Depends(require_professor)):
    items = await student_crud.list_items()
    return items

@app.post("/professors", tags=["Config"], response_model=Professor)
async def create_professor(professor: Professor, user=Depends(require_professor)):
    await professor_crud.create_item(professor.model_dump())
    return professor

@app.get("/professors", tags=["Config"], response_model=list[Professor])
async def list_professors(user=Depends(require_professor)):
    items = await professor_crud.list_items()
    return items

@app.post("/courses", tags=["Config"], response_model=Course)
async def create_course(course: Course, user=Depends(require_professor)):
    await course_crud.create_item(course.model_dump())
    return course

@app.get("/courses", tags=["Config"], response_model=list[Course])
async def list_courses(user=Depends(require_professor)):
    items = await course_crud.list_items()
    return items

@app.post("/classes", tags=["Config"], response_model=Class)
async def create_class(class_: Class, user=Depends(require_professor)):
    await class_crud.create_item(class_.model_dump())
    return class_

@app.get("/classes", tags=["Config"], response_model=list[Class])
async def list_classes(user=Depends(require_professor)):
    items = await class_crud.list_items()
    return items

@app.post("/groups", tags=["Config"], response_model=Group)
async def create_group(group: Group, user=Depends(require_professor)):
    await group_crud.create_item(group.model_dump())
    return group

@app.get("/groups", tags=["Config"], response_model=list[Group])
async def list_groups(user=Depends(require_professor)):
    items = await group_crud.list_items()
    return items

@app.post("/groups/{group_id}/assign-cases", tags=["Config"])
async def assign_cases_to_group(group_id: str, case_ids: list[str], user=Depends(require_professor)):
    group = await group_crud.read_item(group_id)
    if group is None:
        raise HTTPException(status_code=404, detail=f"Group with id {group_id} not found")
    group["assigned_case_ids"] = case_ids
    await group_crud.update_item(group_id, group)
    return {"group_id": group_id, "assigned_case_ids": case_ids}
