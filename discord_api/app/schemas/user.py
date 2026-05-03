from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.user import User
from pydantic.config import ConfigDict


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserOut):
    hashed_password: str
