from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_database():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def get_current_user(
        token: str = Depends(oauth2_scheme),
        database: Session = Depends(get_database)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Could not validate credentials")

    user = database.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
