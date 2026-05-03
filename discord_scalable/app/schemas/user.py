from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic.config import ConfigDict


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
