from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.business_media import BusinessMediaType


class BusinessMediaCreateRequest(BaseModel):
    type: BusinessMediaType
    url: str = Field(min_length=1, max_length=500)


class BusinessMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    type: BusinessMediaType
    url: str
    created_at: datetime

