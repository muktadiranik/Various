# app/models/member.py
from sqlalchemy import ForeignKey, Table, Column, Integer, DateTime, func, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

# Association table for many-to-many relationship between GuildMember and Role
member_roles = Table(
    "member_roles",
    Base.metadata,
    Column("member_id", ForeignKey("guild_members.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_member_roles_member_id", "member_id"),
    Index("ix_member_roles_role_id", "role_id"),
)

class GuildMember(Base):
    __tablename__ = "guild_members"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    nickname: Mapped[str] = mapped_column(String(32), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="guild_memberships") # type: ignore
    guild: Mapped["Guild"] = relationship(back_populates="members") # type: ignore
    roles: Mapped[list["Role"]] = relationship(secondary=member_roles, back_populates="members") # type: ignore
    
    __table_args__ = (
        UniqueConstraint("user_id", "guild_id", name="uq_member_guild"),
        Index("ix_guild_members_guild_id", "guild_id"),
        Index("ix_guild_members_user_id", "user_id"),
    )