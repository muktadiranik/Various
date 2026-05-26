# app/models/guild.py
from sqlalchemy import String, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Guild(Base):
    __tablename__ = "guilds"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(String(512), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_guilds") # type: ignore
    channels: Mapped[list["Channel"]] = relationship(back_populates="guild", cascade="all, delete-orphan") # type: ignore
    members: Mapped[list["GuildMember"]] = relationship(back_populates="guild", cascade="all, delete-orphan") # type: ignore
    roles: Mapped[list["Role"]] = relationship(back_populates="guild", cascade="all, delete-orphan") # type: ignore
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="guild") # type: ignore
    
    __table_args__ = (
        Index("ix_guilds_owner_id", "owner_id"),
    )