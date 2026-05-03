from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.server import ServerCreate, ServerUpdate, ServerOut
from ..models.server import Server, ServerMember
from ..models.user import User
from ..database import get_db
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user

router = APIRouter()


def get_current_user_obj(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401)
    user = db.query(User).filter(User.username == current_user).first()
    if user is None:
        raise HTTPException(status_code=404)
    return user


@router.post("/", response_model=ServerOut)
def create_server(server: ServerCreate, current_user=Depends(get_current_user_obj), db: Session = Depends(get_db)):
    db_server = Server(name=server.name, owner_id=current_user.id)
    db.add(db_server)
    db.flush()
    # Add owner as member
    member = ServerMember(server_id=db_server.id, user_id=current_user.id)
    db.add(member)
    db.commit()
    db.refresh(db_server)
    return ServerOut.model_validate(db_server)


@router.get("/", response_model=List[ServerOut])
def read_servers(current_user=Depends(get_current_user_obj), db: Session = Depends(get_db)):
    servers = db.query(Server).join(ServerMember).filter(
        ServerMember.user_id == current_user.id).all()
    return [ServerOut.model_validate(s) for s in servers]
