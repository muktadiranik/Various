# app/schemas/member.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.role import RoleResponse

class MemberResponse(BaseModel):
    id: int
    user_id: int
    guild_id: int
    nickname: Optional[str] = None
    joined_at: datetime
    user_username: str
    user_discriminator: str
    user_avatar: Optional[str] = None

class MemberRoleResponse(BaseModel):
    member_id: int
    user_id: int
    guild_id: int
    roles: List[RoleResponse] = []