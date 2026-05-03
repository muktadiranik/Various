from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime
from .user import User
# from .room import Room  # Avoid circular


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="messages")
    room: Mapped["Room"] = relationship(back_populates="messages") # type: ignore
