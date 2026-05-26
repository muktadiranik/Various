# app/repositories/message_repo.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload
from app.models.message import Message
from app.models.reaction import MessageReaction
from app.repositories.base import BaseRepository

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session):
        super().__init__(Message, session)
    
    async def get_channel_messages(
        self, 
        channel_id: int, 
        skip: int = 0, 
        limit: int = 50,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages in a channel with pagination"""
        query = select(Message).where(
            Message.channel_id == channel_id,
            Message.is_deleted == False
        )
        
        if before:
            query = query.where(Message.created_at < before)
        if after:
            query = query.where(Message.created_at > after)
        
        query = query.order_by(Message.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(
            query.options(
                selectinload(Message.author),
                selectinload(Message.reactions),
                selectinload(Message.reply_to).selectinload(Message.author)
            )
        )
        return result.scalars().all()
    
    async def get_message_with_details(self, message_id: int) -> Optional[Message]:
        """Get message with author and reactions"""
        result = await self.session.execute(
            select(Message)
            .where(Message.id == message_id, Message.is_deleted == False)
            .options(
                selectinload(Message.author),
                selectinload(Message.reactions).selectinload(MessageReaction.user),
                selectinload(Message.reply_to).selectinload(Message.author),
                selectinload(Message.channel)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_messages_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
        """Get messages by a user"""
        result = await self.session.execute(
            select(Message)
            .where(Message.author_id == user_id, Message.is_deleted == False)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Message.channel),
                selectinload(Message.reactions)
            )
        )
        return result.scalars().all()
    
    async def get_thread_messages(self, parent_message_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
        """Get messages in a thread"""
        result = await self.session.execute(
            select(Message)
            .where(Message.reply_to_id == parent_message_id, Message.is_deleted == False)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Message.author),
                selectinload(Message.reactions)
            )
        )
        return result.scalars().all()
    
    async def soft_delete(self, message_id: int) -> Optional[Message]:
        """Soft delete a message"""
        return await self.update(message_id, is_deleted=True)
    
    async def edit_message(self, message_id: int, new_content: str) -> Optional[Message]:
        """Edit a message"""
        return await self.update(message_id, content=new_content, is_edited=True)
    
    async def bulk_create(self, messages: List[Dict[str, Any]]) -> List[Message]:
        """Bulk create messages"""
        instances = [self.model(**msg) for msg in messages]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances
    
    async def get_message_count_in_channel(self, channel_id: int) -> int:
        """Get total message count in a channel"""
        result = await self.session.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.channel_id == channel_id, Message.is_deleted == False)
        )
        return result.scalar()
    
    async def delete_channel_messages(self, channel_id: int) -> int:
        """Soft delete all messages in a channel"""
        result = await self.session.execute(
            update(Message)
            .where(Message.channel_id == channel_id)
            .values(is_deleted=True)
        )
        await self.session.flush()
        return result.rowcount
    
    async def search_messages(self, channel_id: int, query: str, limit: int = 50) -> List[Message]:
        """Search messages by content"""
        result = await self.session.execute(
            select(Message)
            .where(
                Message.channel_id == channel_id,
                Message.is_deleted == False,
                Message.content.ilike(f"%{query}%")
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .options(
                selectinload(Message.author),
                selectinload(Message.reactions)
            )
        )
        return result.scalars().all()
    
    async def pin_message(self, message_id: int) -> Optional[Message]:
        """Pin a message"""
        return await self.update(message_id, is_pinned=True, pinned_at=datetime.utcnow())
    
    async def unpin_message(self, message_id: int) -> Optional[Message]:
        """Unpin a message"""
        return await self.update(message_id, is_pinned=False, pinned_at=None)
    
    async def get_pinned_messages(self, channel_id: int) -> List[Message]:
        """Get all pinned messages in a channel"""
        result = await self.session.execute(
            select(Message)
            .where(
                Message.channel_id == channel_id,
                Message.is_deleted == False,
                Message.is_pinned == True
            )
            .order_by(Message.pinned_at.desc())
            .options(
                selectinload(Message.author),
                selectinload(Message.reactions)
            )
        )
        return result.scalars().all()
    
    async def add_reaction(self, message_id: int, user_id: int, emoji: str) -> MessageReaction:
        """Add a reaction to a message"""
        reaction = MessageReaction(
            message_id=message_id,
            user_id=user_id,
            emoji=emoji
        )
        self.session.add(reaction)
        await self.session.flush()
        await self.session.refresh(reaction)
        return reaction
    
    async def remove_reaction(self, message_id: int, user_id: int, emoji: str) -> bool:
        """Remove a reaction from a message"""
        result = await self.session.execute(
            delete(MessageReaction)
            .where(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id,
                MessageReaction.emoji == emoji
            )
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_reactions(self, message_id: int, emoji: Optional[str] = None) -> List[MessageReaction]:
        """Get reactions for a message"""
        query = select(MessageReaction).where(MessageReaction.message_id == message_id)
        if emoji:
            query = query.where(MessageReaction.emoji == emoji)
        
        result = await self.session.execute(
            query.options(selectinload(MessageReaction.user))
        )
        return result.scalars().all()