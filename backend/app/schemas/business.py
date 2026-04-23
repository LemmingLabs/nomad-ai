from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BusinessCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    website_url: str | None = Field(default=None, max_length=500)


class BusinessUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    website_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    description: str | None
    contact_phone: str | None
    website_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

