from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    organization_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TopicCreate(TopicBase):
    pass


class TopicRead(TopicBase):
    id: str
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime


class TopicListResponse(BaseModel):
    topics: List[TopicRead]
