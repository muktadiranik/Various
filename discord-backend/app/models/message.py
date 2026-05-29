# app/models/message.py
from sqlalchemy import Text, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

class Message(Base):
    __tablename__ = "messages"
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_to_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    pinned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships 
    author: Mapped["User"] = relationship(back_populates="messages") # type: ignore
    channel: Mapped["Channel"] = relationship(back_populates="messages") # type: ignore
    reply_to: Mapped["Message"] = relationship(remote_side="Message.id", backref="replies")  
    reactions: Mapped[list["MessageReaction"]] = relationship(back_populates="message", cascade="all, delete-orphan") # type: ignore
    
    __table_args__ = (
        Index("ix_messages_channel_id_created_at", "channel_id", "created_at"),
        Index("ix_messages_author_id", "author_id"),
        Index("ix_messages_reply_to_id", "reply_to_id"),
        Index("ix_messages_is_pinned", "is_pinned"),
    )