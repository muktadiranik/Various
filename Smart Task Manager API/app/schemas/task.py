from pydantic import BaseModel
from datetime import datetime


class TaskCreateUpdateRequest(BaseModel):
    title: str
    description: str | None = None
    priority: str | None = None
    deadline: datetime | None = None
    status: str | None = None
    is_deleted: bool | None = None
    project_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str | None = None
    priority: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True
