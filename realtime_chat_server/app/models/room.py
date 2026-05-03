from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from app.database import Base
from datetime import datetime
# from .message import Message  # Avoid circular
from .user import User


class RoomType(PyEnum):
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[RoomType] = mapped_column(
        Enum(RoomType), default=RoomType.TEXT)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(back_populates="messages") # type: ignore
