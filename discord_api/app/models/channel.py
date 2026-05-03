from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
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
    type: Mapped[ChannelType] = mapped_column(default=ChannelType.TEXT)
