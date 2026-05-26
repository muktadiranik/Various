# app/models/permission.py
from sqlalchemy import Integer, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
import enum

class PermissionOverrideType(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"

class PermissionOverride(Base):
    __tablename__ = "permission_overrides"
    
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    allow: Mapped[int] = mapped_column(Integer, default=0)
    deny: Mapped[int] = mapped_column(Integer, default=0)
    override_type: Mapped[PermissionOverrideType] = mapped_column(SQLEnum(PermissionOverrideType), nullable=False)
    
    # Relationships
    channel: Mapped["Channel"] = relationship(back_populates="permission_overrides") # type: ignore
    role: Mapped["Role"] = relationship(back_populates="permission_overrides") # type: ignore
    user: Mapped["User"] = relationship(back_populates="permission_overrides") # type: ignore
    
    __table_args__ = (
        Index("ix_permission_overrides_channel_id", "channel_id"),
        Index("ix_permission_overrides_role_id", "role_id"),
        Index("ix_permission_overrides_user_id", "user_id"),
        UniqueConstraint("channel_id", "role_id", "user_id", name="uq_permission_override"),
    )