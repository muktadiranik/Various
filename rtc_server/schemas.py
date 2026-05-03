from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    SDP_OFFER = "sdp_offer"
    SDP_ANSWER = "sdp_answer"
    ICE_CANDIDATE = "ice_candidate"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    JOIN = "join"
    LEAVE = "leave"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoomOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    type: MessageType
    content: str


class MessageOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    type: MessageType
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class WebRTCSignaling(BaseModel):
    type: MessageType
    sdp: Optional[str] = None
    candidate: Optional[str] = None
    target_user_id: Optional[int] = None


class TypingEvent(BaseModel):
    typing: bool


class WSMessage(BaseModel):
    type: MessageType
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
