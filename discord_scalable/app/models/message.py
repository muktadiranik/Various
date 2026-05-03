from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime
from typing import List


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relationships
    channel: Mapped["Channel"] = relationship(back_populates="messages") # type: ignore
    user: Mapped["User"] = relationship(back_populates="messages") # type: ignore
