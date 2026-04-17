from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TripMessageCreateRequest(BaseModel):
    """Schema for creating a new trip message."""
    
    trip_id: int = Field(..., description="ID of the trip")
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


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
    """Schema for trip continuation response from AI assistant."""
    
    message: TripMessageResponse = Field(
        ..., description="Assistant message response"
    )
    updated_itinerary: Optional[dict] = Field(
        default=None, description="Updated trip itinerary JSON (optional)"
    )
