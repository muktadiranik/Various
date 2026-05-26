# app/schemas/role.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    permissions: int = 0
    position: int = 0
    is_mentionable: bool = False
    is_hoisted: bool = False

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    permissions: Optional[int] = None
    position: Optional[int] = Field(None, ge=0)
    is_mentionable: Optional[bool] = None
    is_hoisted: Optional[bool] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    guild_id: int
    permissions: int
    position: int
    is_mentionable: bool
    is_hoisted: bool
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

class RoleAssign(BaseModel):
    user_id: int
    role_id: int

class RoleRemove(BaseModel):
    user_id: int
    role_id: int