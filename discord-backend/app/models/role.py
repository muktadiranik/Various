# app/models/role.py
from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Role(Base):
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    permissions: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(default=0)
    is_mentionable: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hoisted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="roles") # type: ignore
    members: Mapped[list["GuildMember"]] = relationship(secondary="member_roles", back_populates="roles") # type: ignore
    permission_overrides: Mapped[list["PermissionOverride"]] = relationship(back_populates="role", cascade="all, delete-orphan") # type: ignore
    
    __table_args__ = (
        UniqueConstraint("guild_id", "name", name="uq_role_guild_name"),
        Index("ix_roles_guild_id", "guild_id"),
        Index("ix_roles_position", "position"),
    )