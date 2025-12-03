from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str
    slug: str
    primary_domain: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime
