# tests/unit/test_guild_service.py
import pytest
from app.services.guild_service import GuildService
from app.repositories.guild_repo import GuildRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.guild import GuildCreate


class TestGuildService:
    @pytest.fixture
    def guild_service(self, db_session):
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        return GuildService(db_session, guild_repo, member_repo, role_repo)
    
    async def test_create_guild(self, guild_service, test_user):
        """Test creating a guild"""
        guild_data = GuildCreate(
            name="Test Guild",
            description="A test guild",
            is_public=True
        )
        
        result = await guild_service.create_guild(test_user["id"], guild_data)
        
        assert result.id is not None
        assert result.name == "Test Guild"
        assert result.description == "A test guild"
        assert result.owner_id == test_user["id"]
        assert result.is_public is True
    
    async def test_get_guild(self, guild_service, test_user):
        """Test getting a guild by ID"""
        # Create guild first
        guild_data = GuildCreate(name="Get Test Guild")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        # Retrieve guild
        result = await guild_service.get_guild(guild.id)
        
        assert result is not None
        assert result.id == guild.id
        assert result.name == "Get Test Guild"
    
    async def test_update_guild(self, guild_service, test_user):
        """Test updating a guild"""
        guild_data = GuildCreate(name="Original Name")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        # Get user permissions
        from app.core.permissions import Permission
        user_permissions = Permission.ADMINISTRATOR
        
        # Update guild
        from app.schemas.guild import GuildUpdate
        update_data = GuildUpdate(name="Updated Name")
        result = await guild_service.update_guild(
            guild.id, test_user["id"], user_permissions, update_data
        )
        
        assert result is not None
        assert result.name == "Updated Name"
    
    async def test_join_guild(self, guild_service, test_user, db_session):
        """Test joining a public guild"""
        # Create guild with another user as owner
        from app.repositories.user_repo import UserRepository
        from app.core.security import hash_password
        
        user_repo = UserRepository(db_session)
        owner = await user_repo.create(
            username="owner",
            email="owner@example.com",
            password_hash=hash_password("Password123!"),
            discriminator="5678"
        )
        await db_session.commit()
        
        guild_data = GuildCreate(name="Public Guild", is_public=True)
        guild = await guild_service.create_guild(owner.id, guild_data)
        
        # Another user joins
        result = await guild_service.join_guild(guild.id, test_user["id"])
        
        assert result is True
    
    async def test_join_private_guild(self, guild_service, test_user, db_session):
        """Test joining a private guild (should fail)"""
        guild_data = GuildCreate(name="Private Guild", is_public=False)
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        # Create another user
        from app.repositories.user_repo import UserRepository
        from app.core.security import hash_password
        
        other_user = await UserRepository(db_session).create(
            username="other",
            email="other@example.com",
            password_hash=hash_password("Password123!"),
            discriminator="9999"
        )
        
        with pytest.raises(PermissionError, match="Cannot join private guild"):
            await guild_service.join_guild(guild.id, other_user.id)