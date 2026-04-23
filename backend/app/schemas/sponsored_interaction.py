from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.sponsored_interaction import SponsoredInteractionType


class SponsoredInteractionCreateRequest(BaseModel):
    trip_id: int | None = None
    sponsored_place_id: int
    business_id: int
    interaction_type: SponsoredInteractionType


class SponsoredInteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int | None
    sponsored_place_id: int
    business_id: int
    interaction_type: SponsoredInteractionType
    created_at: datetime

