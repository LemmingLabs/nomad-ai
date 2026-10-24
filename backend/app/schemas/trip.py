from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.schemas.trip_message import TripMessageListResponse
from app.core.destination_registry import (
    DEFAULT_COUNTRY_CODE,
    DEFAULT_DESTINATION_ID,
    resolve_destination,
)


class TripGenerateRequest(BaseModel):
    budget: str
    days: int
    interests: list[str]
    travel_style: str
    prompt: str | None = Field(default=None, max_length=1000)
    country_code: str = Field(default=DEFAULT_COUNTRY_CODE, min_length=2, max_length=2)
    destination_id: str = Field(default=DEFAULT_DESTINATION_ID, min_length=1, max_length=64)

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("destination_id")
    @classmethod
    def normalize_destination_id(cls, value: str) -> str:
        return value.strip().lower()

    @model_validator(mode="after")
    def validate_destination(self) -> "TripGenerateRequest":
        resolve_destination(country_code=self.country_code, destination_id=self.destination_id)
        return self


class TripResponse(BaseModel):
    id: int
    title: str
    budget: str
    days: int
    interests: list[str]
    travel_style: str
    country_code: str
    destination_id: str
    destination_name: str
    itinerary_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripListItemResponse(BaseModel):
    id: int
    title: str
    days: int
    country_code: str
    destination_id: str
    destination_name: str
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
