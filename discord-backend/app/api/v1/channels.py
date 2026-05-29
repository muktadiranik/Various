# app/api/v1/channels.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_channel_service, get_db
from app.services.channel_service import ChannelService
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.core.permissions import Permission, PermissionCalculator
from app.repositories.guild_repo import GuildRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.services.permission_service import PermissionService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    guild_id: int,
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Create a new channel in a guild"""
    try:
        # First, check if the guild exists
        guild_repo = GuildRepository(db)
        guild = await guild_repo.get(guild_id)
        
        if not guild:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        
        # Check if user is the guild owner
        is_owner = guild.owner_id == current_user["id"]
        
        # Get user permissions
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], guild_id
        )
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)
        
        logger.info(f"User {current_user['id']} (username={current_user['username']}, is_owner={is_owner}, has_manage={has_manage}) attempting to create channel in guild {guild_id}")
        
        if not is_owner and not has_manage:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to manage channels in this guild"
            )
        
        # Create the channel
        channel = await channel_service.create_channel(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            channel_data=channel_data
        )
        
        return channel
        
    except HTTPException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating channel: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[ChannelResponse])
async def get_guild_channels(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Get all channels in a guild"""
    try:
        # First, check if the guild exists
        guild_repo = GuildRepository(db)
        guild = await guild_repo.get(guild_id)
        
        if not guild:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        
        # Get user permissions
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], guild_id
        )
        
        channels = await channel_service.get_guild_channels(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        
        return channels
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting guild channels: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Get channel by ID"""
    try:
        # Get channel to check guild
        channel = await channel_service.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        
        # Get user permissions for the guild
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], channel.guild_id
        )
        
        # Check if channel is private and user has view permission
        if channel.is_private:
            has_view = PermissionCalculator.has_permission(user_permissions, Permission.VIEW_CHANNEL)
            if not has_view:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this channel"
                )
        
        return channel
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Update a channel"""
    try:
        # Get channel to check guild
        channel = await channel_service.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        
        # Get user permissions
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], channel.guild_id
        )
        
        updated_channel = await channel_service.update_channel(
            channel_id=channel_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            channel_data=channel_data
        )
        
        if not updated_channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        
        return updated_channel
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating channel: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Delete a channel"""
    try:
        # Get channel to check guild
        channel = await channel_service.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        
        # Get user permissions
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], channel.guild_id
        )
        
        success = await channel_service.delete_channel(
            channel_id=channel_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reorder", response_model=dict)
async def reorder_channels(
    guild_id: int,
    channel_ids: List[int],
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    db: AsyncSession = Depends(get_db)
):
    """Reorder channels in a guild"""
    try:
        # Check if guild exists
        guild_repo = GuildRepository(db)
        guild = await guild_repo.get(guild_id)
        
        if not guild:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        
        # Get user permissions
        member_repo = MemberRepository(db)
        role_repo = RoleRepository(db)
        permission_service = PermissionService(db, member_repo, role_repo, None)
        
        user_permissions = await permission_service.get_user_guild_permissions(
            current_user["id"], guild_id
        )
        
        success = await channel_service.reorder_channels(
            guild_id=guild_id,
            channel_ids=channel_ids,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to reorder channels")
        
        return {"message": "Channels reordered successfully"}
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering channels: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))