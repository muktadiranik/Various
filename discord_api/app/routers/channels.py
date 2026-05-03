from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.channel import ChannelCreate, ChannelUpdate, ChannelOut
from ..models.channel import Channel
from ..models.server import ServerMember
from ..models.user import User
from ..database import get_db
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user
from ..routers.servers import get_current_user_obj

router = APIRouter()


@router.post("/", response_model=ChannelOut)
def create_channel(channel: ChannelCreate, current_user=Depends(get_current_user_obj), db: Session = Depends(get_db)):
    # Check if user is member of server
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           channel.server_id, ServerMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a server member")
    db_channel = Channel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return ChannelOut.model_validate(db_channel)


@router.get("/{server_id}", response_model=List[ChannelOut])
def read_channels(server_id: int, current_user=Depends(get_current_user_obj), db: Session = Depends(get_db)):
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           server_id, ServerMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a server member")
    channels = db.query(Channel).filter(Channel.server_id == server_id).all()
    return [ChannelOut.model_validate(c) for c in channels]
