from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.project import ProjectCreateUpdateRequest, ProjectResponse
from app.services.project_service import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project, 
    import_projects
)
from app.api.deps import get_current_user


def get_database():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.get("/", response_model=list[ProjectResponse])
async def get_projects_api(
        user: User = Depends(get_current_user),
        database: Session = Depends(get_database),
):
    return get_projects(database, user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_api(
    project_id: int,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_database)
):
    return get_project(database, user.id, project_id)


@router.post("/", response_model=ProjectResponse)
async def create_project_api(
    data: ProjectCreateUpdateRequest,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_database)
):
    return create_project(database, user.id, data.title, data.description)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_api(
    project_id: int,
    data: ProjectCreateUpdateRequest,
    database: Session = Depends(get_database)
):
    return update_project(database, project_id, data.title, data.description)


@router.delete("/{project_id}")
async def delete_project_api(
    project_id: int,
    database: Session = Depends(get_database)
):
    return delete_project(database, project_id)


@router.post("/import", response_model=dict)
async def import_projects_api(
    file: UploadFile,
    database: Session = Depends(get_database)
):
    return import_projects(database, file)
