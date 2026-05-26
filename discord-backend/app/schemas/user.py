# app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=32, pattern=r'^[a-zA-Z0-9_]+$')
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=512)
    password: Optional[str] = Field(None, min_length=6, max_length=128)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    discriminator: str
    avatar_url: Optional[str] = None
    is_bot: bool
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"