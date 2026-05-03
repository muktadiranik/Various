from pydantic import BaseModel
from datetime import datetime
from typing import List
from ..models.user import User
from .message import MessageOut


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
