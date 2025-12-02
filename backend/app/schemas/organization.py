from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str
    slug: str
    primary_domain: Optional[str] = None

    class Config:
        orm_mode = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime
