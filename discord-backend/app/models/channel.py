# app/models/channel.py
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from .base import Base

class ChannelType(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"

class Channel(Base):
    __tablename__ = "channels"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ChannelType] = mapped_column(SQLEnum(ChannelType), nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    position: Mapped[int] = mapped_column(default=0)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    topic: Mapped[str] = mapped_column(String(1024), nullable=True)
    bitrate: Mapped[int] = mapped_column(nullable=True)
    user_limit: Mapped[int] = mapped_column(nullable=True)
    
    # Relationships - FIX THIS LINE
    guild: Mapped["Guild"] = relationship(back_populates="channels") # type: ignore
    parent: Mapped["Channel"] = relationship(remote_side="Channel.id", backref="children")  
    messages: Mapped[list["Message"]] = relationship(back_populates="channel", cascade="all, delete-orphan") # type: ignore
    permission_overrides: Mapped[list["PermissionOverride"]] = relationship(back_populates="channel", cascade="all, delete-orphan") # type: ignore
    
    __table_args__ = (
        Index("ix_channels_guild_id", "guild_id"),
        Index("ix_channels_parent_id", "parent_id"),
        UniqueConstraint("guild_id", "name", name="uq_channel_guild_name"),
    )