from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import List


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id]) # type: ignore

    members: Mapped[List["ServerMember"]] = relationship(
        "ServerMember", back_populates="server")


class ServerMember(Base):
    __tablename__ = "server_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    server: Mapped["Server"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="servers") # type: ignore
