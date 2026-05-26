# app/services/user_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse, UserUpdate
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo
    
    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        user = await self.user_repo.get(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            discriminator=user.discriminator,
            avatar_url=user.avatar_url,
            is_bot=user.is_bot,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        update_data = user_data.dict(exclude_unset=True)
        
        if "username" in update_data:
            existing = await self.user_repo.get_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise ValueError("Username already taken")
        
        if "email" in update_data:
            existing = await self.user_repo.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Email already registered")
        
        user = await self.user_repo.update(user_id, **update_data)
        await self.session.commit()
        
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            discriminator=user.discriminator,
            avatar_url=user.avatar_url,
            is_bot=user.is_bot,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def search_users(self, query: str, limit: int = 20) -> List[UserResponse]:
        users = await self.user_repo.search_users(query, limit)
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                discriminator=user.discriminator,
                avatar_url=user.avatar_url,
                is_bot=user.is_bot,
                created_at=user.created_at,
                updated_at=user.updated_at
            ) for user in users
        ]
    
    async def update_status(self, user_id: int, status: str) -> Optional[UserResponse]:
        user = await self.user_repo.update_status(user_id, status)
        await self.session.commit()
        
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            discriminator=user.discriminator,
            avatar_url=user.avatar_url,
            is_bot=user.is_bot,
            created_at=user.created_at,
            updated_at=user.updated_at
        )