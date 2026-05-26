# app/repositories/user_repo.py
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.models.user import User, UserStatus
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_discriminator(self, username: str, discriminator: str) -> Optional[User]:
        """Get user by username and discriminator"""
        result = await self.session.execute(
            select(User).where(
                User.username == username,
                User.discriminator == discriminator
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_guilds(self, user_id: int) -> Optional[User]:
        """Get user with their guild memberships"""
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.guild_memberships)
                .selectinload(User.guild_memberships.entities.guild)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_messages(self, user_id: int, limit: int = 50) -> Optional[User]:
        """Get user with their recent messages"""
        from app.models.message import Message
        
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.messages)
                .limit(limit)
                .order_by(Message.created_at.desc())
            )
        )
        return result.scalar_one_or_none()
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by username or email"""
        result = await self.session.execute(
            select(User)
            .where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%")
                )
            )
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """Update user status"""
        return await self.update(user_id, status=status)
    
    async def update_last_seen(self, user_id: int) -> Optional[User]:
        """Update user's last seen timestamp"""
        from datetime import datetime
        return await self.update(user_id, last_seen=datetime.utcnow())
    
    async def get_online_friends(self, user_id: int) -> List[User]:
        """Get online friends of a user"""
        from app.models.member import GuildMember
        
        result = await self.session.execute(
            select(User)
            .join(GuildMember, GuildMember.user_id == User.id)
            .where(
                GuildMember.guild_id.in_(
                    select(GuildMember.guild_id).where(GuildMember.user_id == user_id)
                ),
                User.id != user_id,
                User.status == UserStatus.ONLINE
            )
            .distinct()
        )
        return result.scalars().all()
    
    async def get_by_ids(self, user_ids: List[int]) -> List[User]:
        """Get multiple users by IDs"""
        result = await self.session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        return result.scalars().all()