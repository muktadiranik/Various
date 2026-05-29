# tests/unit/test_message_service.py
import pytest
from app.services.message_service import MessageService
from app.repositories.message_repo import MessageRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.user_repo import UserRepository
from app.schemas.message import MessageCreate
from app.core.permissions import Permission


class TestMessageService:
    @pytest.fixture
    def message_service(self, db_session):
        message_repo = MessageRepository(db_session)
        channel_repo = ChannelRepository(db_session)
        user_repo = UserRepository(db_session)
        return MessageService(db_session, message_repo, channel_repo, user_repo)
    
    async def test_create_message(self, message_service, test_user, db_session):
        """Test creating a message"""
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Message Test Guild")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        channel_repo = ChannelRepository(db_session)
        channels = await channel_repo.get_guild_channels(guild.id)
        channel = channels[0]
        
        message_data = MessageCreate(content="Test message content")
        result = await message_service.create_message(
            channel.id, test_user["id"], message_data, Permission.SEND_MESSAGES
        )
        
        assert result.id is not None
        assert result.content == "Test message content"
        assert result.author_id == test_user["id"]
        assert result.channel_id == channel.id
    
    async def test_get_channel_messages(self, message_service, test_user, db_session):
        """Test retrieving channel messages"""
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Messages Test Guild")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        channel_repo = ChannelRepository(db_session)
        channels = await channel_repo.get_guild_channels(guild.id)
        channel = channels[0]
        
        for i in range(5):
            msg_data = MessageCreate(content=f"Message {i}")
            await message_service.create_message(
                channel.id, test_user["id"], msg_data, Permission.SEND_MESSAGES
            )
        
        permissions = Permission.VIEW_CHANNEL | Permission.READ_MESSAGE_HISTORY
        result = await message_service.get_channel_messages(
            channel.id, test_user["id"], permissions, limit=10
        )
        
        assert result.total >= 5
        assert len(result.messages) >= 5
    
    async def test_update_message(self, message_service, test_user, db_session):
        """Test updating a message"""
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Update Test Guild")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        channel_repo = ChannelRepository(db_session)
        channels = await channel_repo.get_guild_channels(guild.id)
        assert len(channels) > 0, "No channels created"
        channel = channels[0]
        
        # Create message with SEND_MESSAGES permission
        msg_data = MessageCreate(content="Original content")
        message = await message_service.create_message(
            channel.id, test_user["id"], msg_data, Permission.SEND_MESSAGES
        )
        
        # Update message - author can update without MANAGE_MESSAGES
        from app.schemas.message import MessageUpdate
        update_data = MessageUpdate(content="Updated content")
        
        # Author should be able to update their own message even without MANAGE_MESSAGES
        # The permission check in update_message allows authors to edit
        result = await message_service.update_message(
            message.id, test_user["id"], update_data, Permission.SEND_MESSAGES  # Only SEND_MESSAGES, not MANAGE_MESSAGES
        )
        
        assert result.content == "Updated content"
        assert result.is_edited is True
    
    async def test_delete_message(self, message_service, test_user, db_session):
        """Test soft deleting a message"""
        from app.services.guild_service import GuildService
        from app.repositories.guild_repo import GuildRepository
        from app.repositories.member_repo import MemberRepository
        from app.repositories.role_repo import RoleRepository
        
        guild_repo = GuildRepository(db_session)
        member_repo = MemberRepository(db_session)
        role_repo = RoleRepository(db_session)
        guild_service = GuildService(db_session, guild_repo, member_repo, role_repo)
        
        from app.schemas.guild import GuildCreate
        guild_data = GuildCreate(name="Delete Test Guild")
        guild = await guild_service.create_guild(test_user["id"], guild_data)
        
        channel_repo = ChannelRepository(db_session)
        channels = await channel_repo.get_guild_channels(guild.id)
        assert len(channels) > 0, "No channels created"
        channel = channels[0]
        
        msg_data = MessageCreate(content="To be deleted")
        message = await message_service.create_message(
            channel.id, test_user["id"], msg_data, Permission.SEND_MESSAGES
        )
        
        result = await message_service.delete_message(
            message.id, test_user["id"], Permission.MANAGE_MESSAGES
        )
        
        assert result is True
        
        # Verify message is soft deleted
        with pytest.raises(ValueError, match="Message not found"):
            await message_service.get_message_by_id(message.id, Permission.VIEW_CHANNEL)