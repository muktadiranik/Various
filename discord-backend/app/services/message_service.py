# app/services/message_service.py
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.message_repo import MessageRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.user_repo import UserRepository
from app.core.permissions import Permission, PermissionCalculator, PermissionValidator
from app.schemas.message import (
    MessageCreate, MessageUpdate, MessageResponse, 
    MessageReactionSchema, MessageListResponse
)
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(
        self,
        session: AsyncSession,
        message_repo: MessageRepository,
        channel_repo: ChannelRepository,
        user_repo: UserRepository
    ):
        self.session = session
        self.message_repo = message_repo
        self.channel_repo = channel_repo
        self.user_repo = user_repo
    
    async def create_message(
        self,
        channel_id: int,
        author_id: int,
        message_data: MessageCreate,
        user_permissions: int
    ) -> MessageResponse:
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            raise ValueError("Channel not found")
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.SEND_MESSAGES,
            "You don't have permission to send messages in this channel"
        )
        
        reply_to_id = None
        reply_to_content = None
        reply_to_author = None
        
        if message_data.reply_to_id:
            reply_msg = await self.message_repo.get_message_with_details(message_data.reply_to_id)
            if reply_msg and not reply_msg.is_deleted:
                reply_to_id = reply_msg.id
                reply_to_content = reply_msg.content[:100] if reply_msg.content else None
                reply_to_author = reply_msg.author.username if reply_msg.author else None
        
        message = await self.message_repo.create(
            channel_id=channel_id,
            author_id=author_id,
            content=message_data.content,
            reply_to_id=reply_to_id
        )
        
        await self.session.commit()
        
        author = await self.user_repo.get(author_id)
        
        response = MessageResponse(
            id=message.id,
            content=message.content,
            author_id=author.id,
            author_username=author.username,
            author_avatar=author.avatar_url,
            channel_id=message.channel_id,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            is_pinned=False,
            reply_to_id=message.reply_to_id,
            reply_to_content=reply_to_content,
            reply_to_author=reply_to_author,
            created_at=message.created_at,
            updated_at=message.updated_at,
            reactions=[]
        )
        
        await redis_service.publish_message_created(channel_id, response.dict())
        
        return response
    
    async def get_channel_messages(
        self,
        channel_id: int,
        user_id: int,
        user_permissions: int,
        limit: int = 50,
        offset: int = 0,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None
    ) -> MessageListResponse:
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.VIEW_CHANNEL,
            "You don't have permission to view this channel"
        )
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.READ_MESSAGE_HISTORY,
            "You don't have permission to read message history"
        )
        
        total = await self.message_repo.get_message_count_in_channel(channel_id)
        
        messages = await self.message_repo.get_channel_messages(
            channel_id=channel_id,
            skip=offset,
            limit=limit,
            before=before,
            after=after
        )
        
        message_responses = []
        for msg in messages:
            reactions = []
            for reaction in msg.reactions:
                user = await self.user_repo.get(reaction.user_id)
                reactions.append(MessageReactionSchema(
                    emoji=reaction.emoji,
                    user_id=reaction.user_id,
                    user_username=user.username if user else "Unknown"
                ))
            
            reply_to_content = None
            reply_to_author = None
            if msg.reply_to:
                reply_to_content = msg.reply_to.content[:100] if msg.reply_to.content else None
                reply_to_author = msg.reply_to.author.username if msg.reply_to.author else None
            
            message_responses.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                author_id=msg.author.id,
                author_username=msg.author.username,
                author_avatar=msg.author.avatar_url,
                channel_id=msg.channel_id,
                is_edited=msg.is_edited,
                is_deleted=msg.is_deleted,
                is_pinned=getattr(msg, 'is_pinned', False),
                reply_to_id=msg.reply_to_id,
                reply_to_content=reply_to_content,
                reply_to_author=reply_to_author,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                reactions=reactions
            ))
        
        has_more = len(messages) >= limit and total > (offset + limit)
        
        return MessageListResponse(
            messages=message_responses,
            total=total,
            has_more=has_more,
            limit=limit
        )
    
    async def get_message_by_id(self, message_id: int, user_permissions: int) -> MessageResponse:
        message = await self.message_repo.get_message_with_details(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.VIEW_CHANNEL,
            "You don't have permission to view this channel"
        )
        
        reactions = []
        for reaction in message.reactions:
            user = await self.user_repo.get(reaction.user_id)
            reactions.append(MessageReactionSchema(
                emoji=reaction.emoji,
                user_id=reaction.user_id,
                user_username=user.username if user else "Unknown"
            ))
        
        reply_to_content = None
        reply_to_author = None
        if message.reply_to:
            reply_to_content = message.reply_to.content[:100] if message.reply_to.content else None
            reply_to_author = message.reply_to.author.username if message.reply_to.author else None
        
        return MessageResponse(
            id=message.id,
            content=message.content,
            author_id=message.author.id,
            author_username=message.author.username,
            author_avatar=message.author.avatar_url,
            channel_id=message.channel_id,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            is_pinned=getattr(message, 'is_pinned', False),
            reply_to_id=message.reply_to_id,
            reply_to_content=reply_to_content,
            reply_to_author=reply_to_author,
            created_at=message.created_at,
            updated_at=message.updated_at,
            reactions=reactions
        )
    
    async def update_message(
        self,
        message_id: int,
        user_id: int,
        message_data: MessageUpdate,
        user_permissions: int
    ) -> MessageResponse:
        message = await self.message_repo.get_message_with_details(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        is_author = message.author_id == user_id
        has_manage_permission = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_MESSAGES)
        
        if not is_author and not has_manage_permission:
            raise PermissionError("You don't have permission to edit this message")
        
        updated = await self.message_repo.edit_message(message_id, message_data.content)
        await self.session.commit()
        
        if not updated:
            raise ValueError("Failed to update message")
        
        response = await self.get_message_by_id(message_id, user_permissions)
        
        await redis_service.publish_message_updated(
            channel_id=message.channel_id,
            message_id=message_id,
            message_data=response.dict()
        )
        
        return response
    
    async def delete_message(self, message_id: int, user_id: int, user_permissions: int) -> bool:
        message = await self.message_repo.get(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        is_author = message.author_id == user_id
        has_manage_permission = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_MESSAGES)
        
        if not is_author and not has_manage_permission:
            raise PermissionError("You don't have permission to delete this message")
        
        result = await self.message_repo.soft_delete(message_id)
        await self.session.commit()
        
        if result:
            await redis_service.publish_message_deleted(message.channel_id, message_id)
        
        return result
    
    async def add_reaction(
        self,
        message_id: int,
        user_id: int,
        emoji: str,
        user_permissions: int
    ) -> bool:
        message = await self.message_repo.get(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.ADD_REACTIONS,
            "You don't have permission to add reactions"
        )
        
        reactions = await self.message_repo.get_reactions(message_id, emoji)
        if any(r.user_id == user_id for r in reactions):
            return False
        
        await self.message_repo.add_reaction(message_id, user_id, emoji)
        await self.session.commit()
        
        await redis_service.publish_reaction_added(
            channel_id=message.channel_id,
            message_id=message_id,
            reaction_data={"emoji": emoji, "user_id": user_id}
        )
        
        return True
    
    async def remove_reaction(
        self,
        message_id: int,
        user_id: int,
        emoji: str,
        user_permissions: int
    ) -> bool:
        message = await self.message_repo.get(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_MESSAGES)
        
        if not has_manage:
            reactions = await self.message_repo.get_reactions(message_id, emoji)
            if not any(r.user_id == user_id for r in reactions):
                raise PermissionError("You can only remove your own reactions")
        
        result = await self.message_repo.remove_reaction(message_id, user_id, emoji)
        await self.session.commit()
        
        if result:
            await redis_service.publish_reaction_removed(
                channel_id=message.channel_id,
                message_id=message_id,
                reaction_data={"emoji": emoji, "user_id": user_id}
            )
        
        return result
    
    async def search_messages(
        self,
        channel_id: int,
        query: str,
        user_permissions: int,
        limit: int = 50
    ) -> List[MessageResponse]:
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.VIEW_CHANNEL,
            "You don't have permission to view this channel"
        )
        
        messages = await self.message_repo.search_messages(channel_id, query, limit)
        
        message_responses = []
        for msg in messages:
            reactions = []
            for reaction in msg.reactions:
                user = await self.user_repo.get(reaction.user_id)
                reactions.append(MessageReactionSchema(
                    emoji=reaction.emoji,
                    user_id=reaction.user_id,
                    user_username=user.username if user else "Unknown"
                ))
            
            message_responses.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                author_id=msg.author.id,
                author_username=msg.author.username,
                author_avatar=msg.author.avatar_url,
                channel_id=msg.channel_id,
                is_edited=msg.is_edited,
                is_deleted=msg.is_deleted,
                is_pinned=getattr(msg, 'is_pinned', False),
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                reactions=reactions
            ))
        
        return message_responses
    
    async def pin_message(self, message_id: int, user_id: int, user_permissions: int) -> MessageResponse:
        message = await self.message_repo.get_message_with_details(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.MANAGE_MESSAGES,
            "You don't have permission to pin messages"
        )
        
        await self.message_repo.pin_message(message_id)
        await self.session.commit()
        
        response = await self.get_message_by_id(message_id, user_permissions)
        
        await redis_service.publish_message_updated(
            channel_id=message.channel_id,
            message_id=message_id,
            message_data=response.dict()
        )
        
        return response
    
    async def unpin_message(self, message_id: int, user_id: int, user_permissions: int) -> MessageResponse:
        message = await self.message_repo.get_message_with_details(message_id)
        if not message or message.is_deleted:
            raise ValueError("Message not found")
        
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.MANAGE_MESSAGES,
            "You don't have permission to unpin messages"
        )
        
        await self.message_repo.unpin_message(message_id)
        await self.session.commit()
        
        response = await self.get_message_by_id(message_id, user_permissions)
        
        await redis_service.publish_message_updated(
            channel_id=message.channel_id,
            message_id=message_id,
            message_data=response.dict()
        )
        
        return response
    
    async def get_pinned_messages(self, channel_id: int, user_permissions: int) -> List[MessageResponse]:
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.VIEW_CHANNEL,
            "You don't have permission to view this channel"
        )
        
        messages = await self.message_repo.get_pinned_messages(channel_id)
        
        message_responses = []
        for msg in messages:
            reactions = []
            for reaction in msg.reactions:
                user = await self.user_repo.get(reaction.user_id)
                reactions.append(MessageReactionSchema(
                    emoji=reaction.emoji,
                    user_id=reaction.user_id,
                    user_username=user.username if user else "Unknown"
                ))
            
            message_responses.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                author_id=msg.author.id,
                author_username=msg.author.username,
                author_avatar=msg.author.avatar_url,
                channel_id=msg.channel_id,
                is_edited=msg.is_edited,
                is_deleted=msg.is_deleted,
                is_pinned=True,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                reactions=reactions
            ))
        
        return message_responses
    
    async def bulk_delete_messages(
        self,
        channel_id: int,
        message_ids: List[int],
        user_id: int,
        user_permissions: int
    ) -> int:
        PermissionValidator.validate_channel_permission(
            user_permissions,
            Permission.MANAGE_MESSAGES,
            "You don't have permission to bulk delete messages"
        )
        
        deleted_count = 0
        deleted_message_ids = []
        channel_id_for_publish = None
        
        for message_id in message_ids:
            message = await self.message_repo.get(message_id)
            if message and message.channel_id == channel_id and not message.is_deleted:
                await self.message_repo.soft_delete(message_id)
                deleted_count += 1
                deleted_message_ids.append(message_id)
                channel_id_for_publish = message.channel_id
        
        await self.session.commit()
        
        if channel_id_for_publish:
            for msg_id in deleted_message_ids:
                await redis_service.publish_message_deleted(channel_id_for_publish, msg_id)
        
        return deleted_count