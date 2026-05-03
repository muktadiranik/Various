from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(back_populates="user") # type: ignore
