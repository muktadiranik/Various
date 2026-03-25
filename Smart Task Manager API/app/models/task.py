from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None]
    priority: Mapped[str]
    status: Mapped[str]
    deadline: Mapped[datetime | None]
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"Task(id={self.id!r}, title={self.title!r}, description={self.description!r}, priority={self.priority!r}, status={self.status!r}, deadline={self.deadline!r}, is_deleted={self.is_deleted!r})"
