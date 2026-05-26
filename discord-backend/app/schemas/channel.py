# app/schemas/channel.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ChannelType(str, Enum):
    TEXT = "text"
    VOICE = "voice"

class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: ChannelType = ChannelType.TEXT
    parent_id: Optional[int] = None
    topic: Optional[str] = Field(None, max_length=1024)
    is_private: bool = False
    bitrate: Optional[int] = Field(None, ge=8000, le=384000)
    user_limit: Optional[int] = Field(None, ge=0, le=99)

class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    topic: Optional[str] = Field(None, max_length=1024)
    position: Optional[int] = Field(None, ge=0)
    is_private: Optional[bool] = None
    bitrate: Optional[int] = Field(None, ge=8000, le=384000)
    user_limit: Optional[int] = Field(None, ge=0, le=99)

class ChannelResponse(BaseModel):
    id: int
    name: str
    type: ChannelType
    guild_id: int
    parent_id: Optional[int] = None
    position: int
    is_private: bool
    topic: Optional[str] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime