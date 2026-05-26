# app/models/reaction.py
from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class MessageReaction(Base):
    __tablename__ = "message_reactions"
    
    emoji: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="reactions") # type: ignore
    message: Mapped["Message"] = relationship(back_populates="reactions") # type: ignore
    
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "emoji", name="uq_reaction_user_emoji"),
        Index("ix_message_reactions_message_id", "message_id"),
        Index("ix_message_reactions_user_id", "user_id"),
    )