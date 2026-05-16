from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserRead] = None


class LogoutResponse(BaseModel):
    detail: str
