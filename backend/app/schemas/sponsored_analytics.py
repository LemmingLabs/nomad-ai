from pydantic import BaseModel
from pydantic import Field


class SponsoredAnalyticsBreakdown(BaseModel):
    impressions_count: int
    interactions_count: int
    interactions_by_type: dict[str, int]


class SponsoredPlaceAnalyticsResponse(SponsoredAnalyticsBreakdown):
    sponsored_place_id: int
    country_code: str


class BusinessAnalyticsOverviewResponse(SponsoredAnalyticsBreakdown):
    business_id: int
    country_codes: list[str] = Field(default_factory=list)

