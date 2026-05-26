# app/models/user.py
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from .base import Base

class UserStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    DO_NOT_DISTURB = "dnd"

class User(Base):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=True)
    discriminator: Mapped[str] = mapped_column(String(4), nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.OFFLINE)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(back_populates="author", cascade="all, delete-orphan") # type: ignore
    reactions: Mapped[list["MessageReaction"]] = relationship(back_populates="user", cascade="all, delete-orphan") # type: ignore
    guild_memberships: Mapped[list["GuildMember"]] = relationship(back_populates="user", cascade="all, delete-orphan") # type: ignore
    owned_guilds: Mapped[list["Guild"]] = relationship(back_populates="owner") # type: ignore
    audit_entries: Mapped[list["AuditLog"]] = relationship(back_populates="user") # type: ignore
    permission_overrides: Mapped[list["PermissionOverride"]] = relationship(back_populates="user", cascade="all, delete-orphan") # type: ignore