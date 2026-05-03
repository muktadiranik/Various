from pydantic import BaseModel
from typing import Optional
from ..models.channel import Channel, ChannelType
from ..schemas.server import ServerOut
from pydantic.config import ConfigDict


class ChannelBase(BaseModel):
    name: str
    type: ChannelType = ChannelType.TEXT


class ChannelCreate(ChannelBase):
    server_id: int


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ChannelType] = None


class ChannelOut(ChannelBase):
    id: int
    server_id: int

    model_config = ConfigDict(from_attributes=True)
