from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TripMessageCreateRequest(BaseModel):
    """Payload for a user continuation message."""

    content: str = Field(..., min_length=1, description="User message text")


class TripMessageResponse(BaseModel):
    """Schema for returning a trip message."""

    id: int
    trip_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TripContinuationResponse(BaseModel):
    """Response for trip continuation."""

    message: TripMessageResponse = Field(
        ..., description="Assistant message response"
    )
    updated_itinerary: dict[str, Any] | None = Field(
        default=None, description="Updated trip itinerary JSON (optional)"
    )
