import csv
from io import StringIO
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, UploadFile
from app.models.project import Project


def create_project(
        database: Session,
        user_id: int,
        title: str,
        description: str = None
):
    project = Project(
        title=title,
        description=description,
        owner_id=user_id
    )
    database.add(project)
    database.commit()
    database.refresh(project)
    return project


def get_projects(
        database: Session,
        user_id: int
):
    statement = select(Project).where(Project.owner_id == user_id)
    return database.execute(statement).scalars().all()


def get_project(
        database: Session,
        user_id: int,
        project_id: int
):
    project = database.get(Project, project_id)

    if not project or project.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


def update_project(
        database: Session,
        project: Project,
        title: str | None,
        description: str | None
):
    project.title = title
    project.description = description
    database.commit()
    database.refresh(project)
    return project


def delete_project(
        database: Session,
        project: Project
):
    database.delete(project)
    database.commit()


def import_projects(
        database: Session,
        file: UploadFile
):
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(contents))

    projects = []

    for row in reader:
        projects.append(
            Project(
                title=row["title"],
                description=row["description"],
                owner_id=row["owner_id"]
            )
        )

    database.bulk_save_objects(projects)
    database.commit()

    return {"message": "Projects imported successfully"}
