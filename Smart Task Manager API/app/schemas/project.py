from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: int
    title: str | None
    description: str | None

    class Config:
        from_attributes = True


class ProjectCreateUpdateRequest(BaseModel):
    title: str
    description: str
