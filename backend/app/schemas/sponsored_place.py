from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.sponsored_place_media import SponsoredPlaceMediaResponse


class SponsoredPlaceCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    country_code: str = Field(default="KG", min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=120)
    operating_language: str = Field(default="en", min_length=2, max_length=12)
    city: str = Field(min_length=1, max_length=100)
    lat: float
    lng: float
    google_place_id: str | None = Field(default=None, max_length=255)
    address: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=50)
    cta_text: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    website_url: str | None = Field(default=None, max_length=500)


class SponsoredPlaceUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=120)
    operating_language: str | None = Field(default=None, min_length=2, max_length=12)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    lat: float | None = None
    lng: float | None = None
    google_place_id: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    cta_text: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    website_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class SponsoredPlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    title: str
    description: str
    country_code: str
    region: str | None
    operating_language: str
    location_verified: bool
    city: str
    lat: float
    lng: float
    google_place_id: str | None
    address: str
    category: str
    cta_text: str | None
    contact_phone: str | None
    website_url: str | None
    is_approved: bool
    is_active: bool
    created_at: datetime
    media: list[SponsoredPlaceMediaResponse] = Field(default_factory=list)
