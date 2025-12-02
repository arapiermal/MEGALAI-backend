from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserSettingsBase(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    local_api_key: Optional[str] = None

    class Config:
        orm_mode = True


class UserSettingsRead(UserSettingsBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    has_openai_api_key: bool = False
    has_google_api_key: bool = False
    has_anthropic_api_key: bool = False
    has_local_api_key: bool = False


class UserSettingsUpdate(UserSettingsBase):
    pass
