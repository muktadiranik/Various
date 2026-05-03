from pydantic import BaseModel
from datetime import datetime
from typing import List
from ..models.message import Message


class MessageCreate(BaseModel):
    content: str
    room_id: int


class MessageOut(BaseModel):
    id: int
    content: str
    user_id: int
    room_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class MessageList(BaseModel):
    messages: List[MessageOut]
