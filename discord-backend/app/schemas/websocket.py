# app/schemas/websocket.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from enum import Enum

class WSMessageType(str, Enum):
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    AUTHENTICATED = "authenticated"
    JOIN_GUILD = "join_guild"
    LEAVE_GUILD = "leave_guild"
    JOIN_CHANNEL = "join_channel"
    LEAVE_CHANNEL = "leave_channel"
    SEND_MESSAGE = "send_message"
    NEW_MESSAGE = "new_message"
    MESSAGE_SENT = "message_sent"
    MESSAGE_UPDATED = "message_updated"
    MESSAGE_DELETED = "message_deleted"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    USER_TYPING = "user_typing"
    PRESENCE_UPDATE = "presence_update"
    GET_ONLINE_MEMBERS = "get_online_members"
    ONLINE_MEMBERS = "online_members"
    GET_MESSAGE_HISTORY = "get_message_history"
    MESSAGE_HISTORY = "message_history"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
    ADD_REACTION = "add_reaction"
    REMOVE_REACTION = "remove_reaction"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"

class WSMessage(BaseModel):
    type: WSMessageType
    data: Optional[Any] = None
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    message_id: Optional[int] = None
    user_id: Optional[int] = None
    timestamp: Optional[datetime] = None

class WSJoinGuildData(BaseModel):
    guild_id: int

class WSJoinChannelData(BaseModel):
    channel_id: int

class WSSendMessageData(BaseModel):
    channel_id: int
    content: str
    reply_to_id: Optional[int] = None

class WSTypingData(BaseModel):
    channel_id: int
    guild_id: int

class WSGetOnlineMembersData(BaseModel):
    channel_id: int

class WSGetMessageHistoryData(BaseModel):
    channel_id: int
    limit: int = 50
    before: Optional[str] = None
    after: Optional[str] = None

class WSEditMessageData(BaseModel):
    message_id: int
    content: str
    channel_id: int

class WSDeleteMessageData(BaseModel):
    message_id: int
    channel_id: int

class WSReactionData(BaseModel):
    message_id: int
    emoji: str