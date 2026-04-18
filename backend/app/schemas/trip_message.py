from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripMessageCreateRequest(BaseModel):
    """Payload for a user continuation message."""

    content: str = Field(..., min_length=1, description="User message text")

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Message content cannot be empty.")
        return stripped_value


class TripMessageResponse(BaseModel):
    """Schema for returning a trip message."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    role: str
    content: str
    created_at: datetime


class TripContinuationResponse(BaseModel):
    """Response for trip continuation."""

    message: TripMessageResponse = Field(
        ..., description="Assistant message response"
    )
    updated_itinerary: dict[str, Any] | None = Field(
        default=None, description="Updated trip itinerary JSON (optional)"
    )
