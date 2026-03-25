import hashlib

from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return password_context.hash(hashlib.sha256(password.encode()).hexdigest())


def verify_password(password: str, hashed: str):
    return password_context.verify(hashlib.sha256(password.encode()).hexdigest(), hashed)


def create_access_token(user_id: int):
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access_token"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int):
    expire = datetime.now() + timedelta(days=7)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh_token"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
