from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.sponsored_place import SponsoredPlace
from app.repositories.business_repository import BusinessRepository
from app.repositories.sponsored_place_repository import SponsoredPlaceRepository


class AdminModerationService:
    def __init__(self, db: Session):
        self.db = db
        self.business_repo = BusinessRepository(db)
        self.place_repo = SponsoredPlaceRepository(db)

    def list_businesses(self, *, limit: int = 50, offset: int = 0) -> list[Business]:
        return self.business_repo.list_all(limit=limit, offset=offset)

    def get_business(self, business_id: int) -> Business:
        business = self.business_repo.get_by_id(business_id)
        if business is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        return business

    def list_sponsored_places(
        self,
        *,
        is_approved: bool | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SponsoredPlace]:
        return self.place_repo.list_all(
            is_approved=is_approved,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

    def get_sponsored_place(self, place_id: int) -> SponsoredPlace:
        place = self.place_repo.get_by_id(place_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place not found")
        return place

    def approve_place(self, place_id: int) -> SponsoredPlace:
        place = self.get_sponsored_place(place_id)
        return self.place_repo.update(place, is_approved=True)

    def reject_place(self, place_id: int) -> SponsoredPlace:
        place = self.get_sponsored_place(place_id)
        return self.place_repo.update(place, is_approved=False, is_active=False)

    def activate_place(self, place_id: int) -> SponsoredPlace:
        place = self.get_sponsored_place(place_id)
        return self.place_repo.update(place, is_active=True)

    def deactivate_place(self, place_id: int) -> SponsoredPlace:
        place = self.get_sponsored_place(place_id)
        return self.place_repo.update(place, is_active=False)

