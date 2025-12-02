from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    organization_id: Optional[str] = None
    current_organization_id: Optional[str] = None
    is_active: bool = True

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "student"
    organization_id: Optional[str] = None


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserReadWithOrg(UserRead):
    organization_name: Optional[str] = None
    organization_slug: Optional[str] = None
