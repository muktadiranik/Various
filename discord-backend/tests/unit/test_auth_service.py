# tests/unit/test_auth_service.py
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


class TestAuthService:
    @pytest.fixture
    def auth_service(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        return AuthService(db_session, user_repo)
    
    async def test_register_success(self, auth_service: AuthService):
        """Test successful user registration"""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="Password123!"
        )
        
        result = await auth_service.register(user_data)
        
        assert result.id is not None
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.discriminator is not None
    
    async def test_register_duplicate_email(self, auth_service: AuthService, test_user):
        """Test registration with existing email"""
        user_data = UserCreate(
            username="anotheruser",
            email="test@example.com",
            password="Password123!"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register(user_data)
    
    async def test_register_duplicate_username(self, auth_service: AuthService, test_user):
        """Test registration with existing username"""
        user_data = UserCreate(
            username="testuser",
            email="another@example.com",
            password="Password123!"
        )
        
        with pytest.raises(ValueError, match="Username already taken"):
            await auth_service.register(user_data)
    
    async def test_login_success(self, auth_service: AuthService):
        """Test successful login"""
        # First register a user
        user_data = UserCreate(
            username="loginuser",
            email="login@example.com",
            password="Password123!"
        )
        await auth_service.register(user_data)
        
        # Then login
        result = await auth_service.login("login@example.com", "Password123!")
        
        assert result is not None
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
    
    async def test_login_invalid_email(self, auth_service: AuthService):
        """Test login with invalid email"""
        result = await auth_service.login("nonexistent@example.com", "Password123!")
        assert result is None
    
    async def test_login_invalid_password(self, auth_service: AuthService, test_user):
        """Test login with invalid password"""
        result = await auth_service.login("test@example.com", "WrongPassword!")
        assert result is None