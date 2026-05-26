# app/models/audit_log.py
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
import enum

class AuditAction(str, enum.Enum):
    GUILD_CREATE = "guild_create"
    GUILD_UPDATE = "guild_update"
    GUILD_DELETE = "guild_delete"
    CHANNEL_CREATE = "channel_create"
    CHANNEL_UPDATE = "channel_update"
    CHANNEL_DELETE = "channel_delete"
    ROLE_CREATE = "role_create"
    ROLE_UPDATE = "role_update"
    ROLE_DELETE = "role_delete"
    MEMBER_JOIN = "member_join"
    MEMBER_LEAVE = "member_leave"
    MEMBER_KICK = "member_kick"
    MEMBER_BAN = "member_ban"
    MESSAGE_DELETE = "message_delete"
    MESSAGE_EDIT = "message_edit"
    PERMISSION_OVERRIDE_CREATE = "permission_override_create"
    PERMISSION_OVERRIDE_UPDATE = "permission_override_update"
    PERMISSION_OVERRIDE_DELETE = "permission_override_delete"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[AuditAction] = mapped_column(SQLEnum(AuditAction), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=True)
    changes: Mapped[str] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(String(512), nullable=True)
    
    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="audit_logs") # type: ignore
    user: Mapped["User"] = relationship(back_populates="audit_entries") # type: ignore
    
    __table_args__ = (
        Index("ix_audit_logs_guild_id_created_at", "guild_id", "created_at"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
    )