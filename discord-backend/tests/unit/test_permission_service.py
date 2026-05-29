# tests/unit/test_permission_service.py
import pytest
from app.services.permission_service import PermissionService
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.channel_repo import ChannelRepository
from app.core.permissions import Permission, PermissionCalculator


class TestPermissionService:
    @pytest.fixture
    def permission_service(self, db_session):
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        channel_repo = ChannelRepository(db_session)
        return PermissionService(db_session, member_repo, role_repo, channel_repo)
    
    async def test_get_user_guild_permissions_owner(self, permission_service, test_user, db_session):
        """Test getting permissions for guild owner"""
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Owner Permissions Test")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        permissions = await permission_service.get_user_guild_permissions(test_user["id"], guild.id)
        
        # Owner should have administrator permission
        assert PermissionCalculator.has_permission(permissions, Permission.ADMINISTRATOR) is True
    
    async def test_get_user_guild_permissions_member(self, permission_service, db_session):
        """Test getting permissions for regular member"""
        from app.core.security import hash_password
        from app.repositories.user_repo import UserRepository
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        # Create owner and member users
        user_repo = UserRepository(db_session)
        owner = await user_repo.create(
            username="owner2",
            email="owner2@example.com",
            password_hash=hash_password("Password123!"),
            discriminator="1111"
        )
        member = await user_repo.create(
            username="member",
            email="member@example.com",
            password_hash=hash_password("Password123!"),
            discriminator="2222"
        )
        await db_session.commit()
        
        # Create guild
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Member Permissions Test")
        guild = await guild_service.create_guild(owner.id, guild_data)
        
        # Join as member
        await guild_service.join_guild(guild.id, member.id)
        
        permissions = await permission_service.get_user_guild_permissions(member.id, guild.id)
        
        # Member should have default permissions but not administrator
        assert PermissionCalculator.has_permission(permissions, Permission.ADMINISTRATOR) is False
        assert PermissionCalculator.has_permission(permissions, Permission.VIEW_CHANNEL) is True
    
    async def test_permission_calculator(self):
        """Test PermissionCalculator utility"""
        # Test combining permissions
        perms1 = Permission.SEND_MESSAGES | Permission.VIEW_CHANNEL
        perms2 = Permission.ADD_REACTIONS
        
        combined = perms1 | perms2
        assert PermissionCalculator.has_permission(combined, Permission.SEND_MESSAGES) is True
        assert PermissionCalculator.has_permission(combined, Permission.VIEW_CHANNEL) is True
        assert PermissionCalculator.has_permission(combined, Permission.ADD_REACTIONS) is True
        
        # Test removing permissions
        removed = PermissionCalculator.remove_permission(combined, Permission.SEND_MESSAGES)
        assert PermissionCalculator.has_permission(removed, Permission.SEND_MESSAGES) is False
        assert PermissionCalculator.has_permission(removed, Permission.VIEW_CHANNEL) is True