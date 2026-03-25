from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.project import Project
from sqlalchemy import select


def create_task(database: Session, project_id: int, user_id: int, data: dict):
    project = database.get(Project, project_id)

    if not project or not project.owner_id == user_id:
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(**data.model_dump())
    database.add(task)
    database.commit()
    database.refresh(task)
    return task


def update_task(database: Session, task_id: int, user_id: int, data: dict):
    task = database.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.project.owner_id == user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in data.model_dump().items():
        setattr(task, key, value)

    database.commit()
    database.refresh(task)
    return task


def get_tasks(
    database: Session,
    user_id: int,
    status=None,
    priority=None,
    limit=10,
    offset=0
):
    statement = select(Task).join(Project).where(
        Task.is_deleted == False).where(Project.owner_id == user_id)

    if status:
        statement = statement.where(Task.status == status)

    if priority:
        statement = statement.where(Task.priority == priority)

    if limit:
        statement = statement.limit(limit)

    if offset:
        statement = statement.offset(offset)

    return database.execute(statement).scalars().all()


def get_task(
        database: Session,
        task_id: int,
        user_id: int
):
    statement = select(Task).join(Project).where(
        Task.id == task_id,
        Project.owner_id == user_id,
        Task.is_deleted == False
    )

    task = database.execute(statement).scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def get_project_tasks(
        database: Session,
        project_id: int,
        user_id: int
):
    project = database.get(Project, project_id)

    if not project or not project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")

    statement = select(Task).where(
        Task.project_id == project_id,
        Task.is_deleted == False
    )

    return database.execute(statement).scalars().all()


def delete_task(
        database: Session,
        task_id: int,
        user_id: int
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.project.owner_id == user_id
    )

    task = database.execute(statement).scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    database.commit()
    database.refresh(task)
    return task
