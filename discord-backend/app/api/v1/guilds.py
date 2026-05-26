# app/api/v1/guilds.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.dependencies import get_current_user, get_guild_service, get_current_user_permissions
from app.services.guild_service import GuildService
from app.schemas.guild import GuildCreate, GuildUpdate, GuildResponse, GuildDetailResponse, GuildMemberResponse

router = APIRouter(prefix="/guilds", tags=["guilds"])


@router.post("/", response_model=GuildResponse, status_code=status.HTTP_201_CREATED)
async def create_guild(
    guild_data: GuildCreate,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service)
):
    """Create a new guild"""
    try:
        guild = await guild_service.create_guild(
            owner_id=current_user["id"],
            guild_data=guild_data
        )
        return guild
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[GuildResponse])
async def get_user_guilds(
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service)
):
    """Get all guilds for current user"""
    guilds = await guild_service.get_user_guilds(current_user["id"])
    return guilds


@router.get("/{guild_id}", response_model=GuildDetailResponse)
async def get_guild(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service)
):
    """Get guild details by ID"""
    try:
        guild = await guild_service.get_guild_detail(guild_id, current_user["id"])
        if not guild:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        return guild
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{guild_id}", response_model=GuildResponse)
async def update_guild(
    guild_id: int,
    guild_data: GuildUpdate,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Update guild information"""
    try:
        guild = await guild_service.update_guild(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            guild_data=guild_data
        )
        if not guild:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        return guild
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{guild_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guild(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Delete a guild"""
    try:
        success = await guild_service.delete_guild(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{guild_id}/join", response_model=dict)
async def join_guild(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service)
):
    """Join a public guild"""
    try:
        await guild_service.join_guild(guild_id, current_user["id"])
        return {"message": "Successfully joined guild", "guild_id": guild_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{guild_id}/leave", response_model=dict)
async def leave_guild(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service)
):
    """Leave a guild"""
    try:
        await guild_service.leave_guild(guild_id, current_user["id"])
        return {"message": "Successfully left guild", "guild_id": guild_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{guild_id}/members", response_model=List[GuildMemberResponse])
async def get_guild_members(
    guild_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get members of a guild"""
    try:
        members = await guild_service.get_guild_members(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            skip=skip,
            limit=limit
        )
        return members
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{guild_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def kick_member(
    guild_id: int,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Kick a member from guild"""
    try:
        success = await guild_service.kick_member(
            guild_id=guild_id,
            target_user_id=user_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{guild_id}/transfer/{new_owner_id}", response_model=dict)
async def transfer_ownership(
    guild_id: int,
    new_owner_id: int,
    current_user: dict = Depends(get_current_user),
    guild_service: GuildService = Depends(get_guild_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Transfer guild ownership"""
    try:
        success = await guild_service.transfer_ownership(
            guild_id=guild_id,
            new_owner_id=new_owner_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
        return {"message": "Ownership transferred successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))