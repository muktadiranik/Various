from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.user import UserOut, UserUpdate
from ..models.user import User
from ..database import get_db
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user is None:
        raise HTTPException(status_code=401)
    user = db.query(User).filter(User.username == current_user).first()
    if user is None:
        raise HTTPException(status_code=404)
    return UserOut.model_validate(user)


@router.put("/me", response_model=UserOut)
def update_users_me(
    user_update: UserUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user is None:
        raise HTTPException(status_code=401)
    user = db.query(User).filter(User.username == current_user).first()
    if user is None:
        raise HTTPException(status_code=404)
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    return UserOut.model_validate(user)
