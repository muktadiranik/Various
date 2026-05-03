from pydantic import BaseModel
from typing import List, Optional
from ..models.server import Server
from ..schemas.user import UserOut
from pydantic.config import ConfigDict


class ServerBase(BaseModel):
    name: str


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = None


class ServerMemberOut(BaseModel):
    user_id: int
    server_id: int


class ServerOut(ServerBase):
    id: int
    owner_id: int
    owner: UserOut
    members: List[ServerMemberOut] = []

    model_config = ConfigDict(from_attributes=True)
