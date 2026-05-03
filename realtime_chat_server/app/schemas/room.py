from pydantic import BaseModel
from datetime import datetime
from typing import List
from ..models.room import Room
from .message import MessageOut


class RoomCreate(BaseModel):
    name: str
    type: str = "text"  # "text", "voice", "video"


class RoomOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoomList(BaseModel):
    rooms: List[RoomOut]
