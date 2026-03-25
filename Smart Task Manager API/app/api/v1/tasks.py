from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreateUpdateRequest
from app.services.task_service import (
    create_task,
    update_task,
    delete_task,
    get_tasks,
    get_project_tasks,
    get_task
)
from app.api.deps import get_current_user


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


def get_database():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@router.get("/")
async def get_tasks_api(database: Session = Depends(get_database), user: User = Depends(get_current_user)):
    return get_tasks(database, user.id)


@router.get("/{task_id}")
async def get_task_api(
    task_id: int,
    database: Session = Depends(get_database),
    user: User = Depends(get_current_user),
):
    return get_task(database, task_id, user.id)


@router.get("/project/{project_id}")
async def get_project_tasks_api(project_id: int, database: Session = Depends(get_database)):
    return get_project_tasks(database, project_id)


@router.post("/")
async def create_task_api(
    data: TaskCreateUpdateRequest,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_database)
):
    return create_task(database, data.project_id, user.id, data)


@router.put("/{task_id}")
async def update_task_api(
    task_id: int,
    data: TaskCreateUpdateRequest,
    database: Session = Depends(get_database),
    user: User = Depends(get_current_user),
):
    return update_task(database, task_id, user.id, data)


@router.delete("/{task_id}")
async def delete_task_api(task_id: int, database: Session = Depends(get_database), user: User = Depends(get_current_user)):
    return delete_task(database, task_id, user.id)
