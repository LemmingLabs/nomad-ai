from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.sponsored_place_media import SponsoredPlaceMediaType


class SponsoredPlaceMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sponsored_place_id: int
    type: SponsoredPlaceMediaType
    url: str
    filename: str
    content_type: str
    created_at: datetime
