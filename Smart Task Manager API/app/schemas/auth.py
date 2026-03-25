from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str


class SignupResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
