from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr
    role: str
    org: Optional[str] = None
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    organization_id: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., alias="refresh_token")


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    organization_id: Optional[str] = None
