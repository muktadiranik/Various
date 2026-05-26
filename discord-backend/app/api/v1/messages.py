# app/api/v1/messages.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime
from app.dependencies import get_current_user, get_message_service, get_current_user_permissions
from app.services.message_service import MessageService
from app.schemas.message import (
    MessageCreate, MessageUpdate, MessageResponse,
    MessageListResponse, MessageReactionAdd
)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{channel_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    channel_id: int,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Create a new message in a channel"""
    try:
        message = await message_service.create_message(
            channel_id=channel_id,
            author_id=current_user["id"],
            message_data=message_data,
            user_permissions=user_permissions
        )
        return message
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{channel_id}", response_model=MessageListResponse)
async def get_channel_messages(
    channel_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get messages from a channel with pagination"""
    try:
        messages = await message_service.get_channel_messages(
            channel_id=channel_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            limit=limit,
            offset=offset,
            before=before,
            after=after
        )
        return messages
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/single/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get a single message by ID"""
    try:
        message = await message_service.get_message_by_id(
            message_id=message_id,
            user_permissions=user_permissions
        )
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Update a message"""
    try:
        message = await message_service.update_message(
            message_id=message_id,
            user_id=current_user["id"],
            message_data=message_data,
            user_permissions=user_permissions
        )
        return message
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Delete a message (soft delete)"""
    try:
        success = await message_service.delete_message(
            message_id=message_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{message_id}/reactions", response_model=dict)
async def add_reaction(
    message_id: int,
    reaction: MessageReactionAdd,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Add a reaction to a message"""
    try:
        success = await message_service.add_reaction(
            message_id=message_id,
            user_id=current_user["id"],
            emoji=reaction.emoji,
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reaction already exists")
        return {"message": "Reaction added successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{message_id}/reactions", response_model=dict)
async def remove_reaction(
    message_id: int,
    emoji: str,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Remove a reaction from a message"""
    try:
        success = await message_service.remove_reaction(
            message_id=message_id,
            user_id=current_user["id"],
            emoji=emoji,
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found")
        return {"message": "Reaction removed successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{message_id}/pin", response_model=MessageResponse)
async def pin_message(
    message_id: int,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Pin a message"""
    try:
        message = await message_service.pin_message(
            message_id=message_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        return message
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{message_id}/pin", response_model=MessageResponse)
async def unpin_message(
    message_id: int,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Unpin a message"""
    try:
        message = await message_service.unpin_message(
            message_id=message_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        return message
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{channel_id}/pinned", response_model=List[MessageResponse])
async def get_pinned_messages(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get all pinned messages in a channel"""
    try:
        messages = await message_service.get_pinned_messages(
            channel_id=channel_id,
            user_permissions=user_permissions
        )
        return messages
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{channel_id}/search", response_model=dict)
async def search_messages(
    channel_id: int,
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Search messages in a channel"""
    try:
        messages = await message_service.search_messages(
            channel_id=channel_id,
            query=q,
            user_permissions=user_permissions,
            limit=limit
        )
        return {"query": q, "messages": messages, "total": len(messages)}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))