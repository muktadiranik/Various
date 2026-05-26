# app/api/v1/presence.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_current_user, get_db, get_presence_service
from app.services.presence_service import PresenceService
from app.repositories.member_repo import MemberRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/presence", tags=["presence"])


@router.post("/guilds/{guild_id}/online")
async def set_online(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    presence_service: PresenceService = Depends(get_presence_service)
):
    """Mark user as online in a guild"""
    member_repo = MemberRepository(db)
    is_member = await member_repo.is_member(guild_id, current_user["id"])
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    await presence_service.set_user_online(current_user["id"], guild_id, "online")
    return {"status": "online", "guild_id": guild_id}


@router.post("/guilds/{guild_id}/offline")
async def set_offline(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    presence_service: PresenceService = Depends(get_presence_service)
):
    """Mark user as offline in a guild"""
    await presence_service.set_user_offline(current_user["id"], guild_id)
    return {"status": "offline", "guild_id": guild_id}


@router.get("/guilds/{guild_id}/online")
async def get_guild_online_users(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    presence_service: PresenceService = Depends(get_presence_service)
):
    """Get all online users in a guild"""
    member_repo = MemberRepository(db)
    is_member = await member_repo.is_member(guild_id, current_user["id"])
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    online_users = await presence_service.get_guild_online_users(guild_id)
    return {
        "guild_id": guild_id,
        "online_count": len(online_users),
        "online_users": list(online_users)
    }


@router.post("/channels/{channel_id}/typing")
async def start_typing(
    channel_id: int,
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    presence_service: PresenceService = Depends(get_presence_service)
):
    """Send typing indicator in a channel"""
    await presence_service.start_typing(current_user["id"], current_user["username"], channel_id, guild_id)
    return {"status": "typing"}


@router.delete("/channels/{channel_id}/typing")
async def stop_typing(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    presence_service: PresenceService = Depends(get_presence_service)
):
    """Stop typing indicator in a channel"""
    await presence_service.stop_typing(current_user["id"], channel_id)
    return {"status": "stopped"}