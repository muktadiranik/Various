# app/schemas/message.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class MessageReactionSchema(BaseModel):
    emoji: str
    user_id: int
    user_username: str

class MessageResponse(BaseModel):
    id: int
    content: str
    author_id: int
    author_username: str
    author_avatar: Optional[str] = None
    channel_id: int
    is_edited: bool
    is_deleted: bool
    is_pinned: bool = False
    reply_to_id: Optional[int] = None
    reply_to_content: Optional[str] = None
    reply_to_author: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reactions: List[MessageReactionSchema] = []

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    reply_to_id: Optional[int] = None

class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageReactionAdd(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=50)

class MessageReactionRemove(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=50)

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool
    limit: int

class MessageSearchResponse(BaseModel):
    messages: List[MessageResponse]
    query: str
    total: int

class MessagePinResponse(BaseModel):
    message_id: int
    is_pinned: bool
    pinned_at: Optional[datetime] = None