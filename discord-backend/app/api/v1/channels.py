# app/api/v1/channels.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_current_user, get_channel_service, get_current_user_permissions
from app.services.channel_service import ChannelService
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    guild_id: int,
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Create a new channel in a guild"""
    try:
        channel = await channel_service.create_channel(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            channel_data=channel_data
        )
        return channel
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[ChannelResponse])
async def get_guild_channels(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get all channels in a guild"""
    try:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Get channel by ID"""
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Update a channel"""
    try:
        channel = await channel_service.update_channel(
            channel_id=channel_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            channel_data=channel_data
        )
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        return channel
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Delete a channel"""
    try:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reorder", response_model=dict)
async def reorder_channels(
    guild_id: int,
    channel_ids: List[int],
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Reorder channels in a guild"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))