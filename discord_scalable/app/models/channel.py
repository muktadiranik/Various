from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from enum import Enum as PyEnum
from typing import List


class ChannelType(PyEnum):
    TEXT = "text"
    VOICE = "voice"


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    type: Mapped[ChannelType] = mapped_column(
        SQLEnum(ChannelType), default=ChannelType.TEXT)

    server: Mapped["Server"] = relationship(back_populates="channels") # type: ignore
    messages: Mapped[List["Message"]] = relationship(back_populates="messages") # type: ignore
