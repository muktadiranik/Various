# app/services/auth_service.py
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.validators import validate_username, validate_email
import random
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo
    
    async def register(self, user_data: UserCreate) -> UserResponse:
        # Validate input
        if not validate_username(user_data.username):
            raise ValueError("Invalid username. Must be 2-32 characters (letters, numbers, underscore)")
        
        if not validate_email(user_data.email):
            raise ValueError("Invalid email format")
        
        # Check existing user
        if await self.user_repo.get_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        if await self.user_repo.get_by_username(user_data.username):
            raise ValueError("Username already taken")
        
        # Generate discriminator
        discriminator = str(random.randint(1000, 9999))
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user = await self.user_repo.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            discriminator=discriminator
        )
        
        await self.session.commit()
        
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
    
    async def login(self, email: str, password: str) -> Optional[TokenResponse]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            raise ValueError("Account is disabled")
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        from app.core.security import verify_token
        
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = await self.user_repo.get(int(user_id))
        if not user or not user.is_active:
            return None
        
        access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )