from fastapi import APIRouter, Depends, HTTPException, UploadFile
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.services.user_service import create_user, import_users
from app.schemas.auth import LoginRequest, TokenResponse, SignupRequest, SignupResponse
from app.services.user_service import authenticate_user


router = APIRouter(prefix="/auth", tags=["auth"])


def get_database():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@router.post("/signup", response_model=SignupResponse)
def signup(
    data: SignupRequest,
    database: Session = Depends(get_database)
):
    return create_user(database, data.email, data.password)


@router.post("/import-users", response_model=dict)
def import_users_api(
    file: UploadFile,
    database: Session = Depends(get_database)
):
    return import_users(database, file)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    database: Session = Depends(get_database)
):
    user = authenticate_user(database, data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("type") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=401, detail="Could not validate credentials")

    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}
