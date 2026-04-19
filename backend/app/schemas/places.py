from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PlaceDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    twogis_id: str
    name: str
    category: str
    city: str
    address: str | None = None
    lat: float
    lon: float
    rating: float | None = None
    review_count: int | None = None
    last_refreshed: datetime


class AccommodationDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    twogis_id: str | None = None
    name: str
    city: str
    accommodation_type: Literal["hostel", "standard", "comfort"]
    price_per_night_usd: float
    address: str | None = None
    lat: float | None = None
    lon: float | None = None
    rating: float | None = None
    review_count: int | None = None
    last_refreshed: datetime | None = None


class PlaceRefreshResult(BaseModel):
    places_upserted: int
    accommodations_upserted: int
    errors: list[str] = Field(default_factory=list)
    refreshed_at: datetime


class AccommodationFilter(BaseModel):
    city: str
    accommodation_type: Literal["hostel", "standard", "comfort"] = "hostel"
    max_price_usd: float | None = None
