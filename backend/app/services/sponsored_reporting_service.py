from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.sponsored_analytics_repository import SponsoredAnalyticsRepository
from app.repositories.sponsored_place_repository import SponsoredPlaceRepository


class SponsoredReportingService:
    def __init__(self, db: Session):
        self.db = db
        self.business_repo = BusinessRepository(db)
        self.place_repo = SponsoredPlaceRepository(db)
        self.analytics_repo = SponsoredAnalyticsRepository(db)

    def business_overview_for_me(self, current_user: User) -> tuple[int, int, int, dict[str, int]]:
        business = self.business_repo.get_by_owner_id(current_user.id)
        if business is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found")

        impressions = self.analytics_repo.count_impressions_for_business(business.id)
        interactions = self.analytics_repo.count_interactions_for_business(business.id)
        breakdown = self.analytics_repo.interactions_breakdown_for_business(business.id)
        return business.id, impressions, interactions, breakdown

    def sponsored_place_stats_for_me(self, current_user: User, sponsored_place_id: int) -> tuple[int, int, dict[str, int]]:
        business = self.business_repo.get_by_owner_id(current_user.id)
        if business is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found")

        place = self.place_repo.get_for_business(business.id, sponsored_place_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place not found")

        impressions = self.analytics_repo.count_impressions_for_place(place.id)
        interactions = self.analytics_repo.count_interactions_for_place(place.id)
        breakdown = self.analytics_repo.interactions_breakdown_for_place(place.id)
        return impressions, interactions, breakdown

    def admin_business_stats(self, business_id: int) -> tuple[int, int, dict[str, int]]:
        business = self.business_repo.get_by_id(business_id)
        if business is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

        impressions = self.analytics_repo.count_impressions_for_business(business.id)
        interactions = self.analytics_repo.count_interactions_for_business(business.id)
        breakdown = self.analytics_repo.interactions_breakdown_for_business(business.id)
        return impressions, interactions, breakdown

    def admin_place_stats(self, sponsored_place_id: int) -> tuple[int, int, dict[str, int]]:
        place = self.place_repo.get_by_id(sponsored_place_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place not found")

        impressions = self.analytics_repo.count_impressions_for_place(place.id)
        interactions = self.analytics_repo.count_interactions_for_place(place.id)
        breakdown = self.analytics_repo.interactions_breakdown_for_place(place.id)
        return impressions, interactions, breakdown
