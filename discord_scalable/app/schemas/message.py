from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic.config import ConfigDict


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    channel_id: int


class MessageUpdate(BaseModel):
    content: Optional[str] = None


class MessageOut(MessageBase):
    id: int
    channel_id: int
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
