from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.trip_message import TripMessageListResponse


class TripGenerateRequest(BaseModel):
    budget: str
    days: int
    interests: list[str]
    travel_style: str
    prompt: str | None = Field(default=None, max_length=1000)


class TripResponse(BaseModel):
    id: int
    title: str
    budget: str
    days: int
    interests: list[str]
    travel_style: str
    itinerary_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripListItemResponse(BaseModel):
    id: int
    title: str
    days: int
    created_at: datetime
    updated_at: datetime
    last_message_preview: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TripListResponse(BaseModel):
    items: list[TripListItemResponse]


class SyncGuestTripRequest(BaseModel):
    trip_id: int

class TripDetailResponse(BaseModel):
    trip: TripResponse
    messages: TripMessageListResponse
