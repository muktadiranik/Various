# app/schemas/guild.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.channel import ChannelResponse
from app.schemas.role import RoleResponse

class GuildCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = True

class GuildUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon_url: Optional[str] = Field(None, max_length=512)
    is_public: Optional[bool] = None

class GuildResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    owner_id: int
    owner_username: str
    is_public: bool
    member_count: int
    created_at: datetime
    updated_at: datetime

class GuildDetailResponse(GuildResponse):
    channels: List[ChannelResponse] = []
    roles: List[RoleResponse] = []

class GuildMemberResponse(BaseModel):
    user_id: int
    username: str
    discriminator: str
    avatar_url: Optional[str] = None
    nickname: Optional[str] = None
    joined_at: datetime
    roles: List[RoleResponse] = []

class GuildMemberAdd(BaseModel):
    user_id: int

class GuildMemberRemove(BaseModel):
    user_id: int

class GuildMemberUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=32)