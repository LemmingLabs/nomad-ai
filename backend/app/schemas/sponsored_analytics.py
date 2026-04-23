from pydantic import BaseModel


class SponsoredAnalyticsBreakdown(BaseModel):
    impressions_count: int
    interactions_count: int
    interactions_by_type: dict[str, int]


class SponsoredPlaceAnalyticsResponse(SponsoredAnalyticsBreakdown):
    sponsored_place_id: int


class BusinessAnalyticsOverviewResponse(SponsoredAnalyticsBreakdown):
    business_id: int

