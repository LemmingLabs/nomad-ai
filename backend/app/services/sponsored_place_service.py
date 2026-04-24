from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sponsored_place import SponsoredPlace
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.sponsored_place_repository import SponsoredPlaceRepository
from app.services.sponsored_injection_service import normalize_category, normalize_city


class SponsoredPlaceService:
    def __init__(self, db: Session):
        self.db = db
        self.business_repo = BusinessRepository(db)
        self.place_repo = SponsoredPlaceRepository(db)

    def _get_my_business_id(self, current_user: User) -> int:
        business = self.business_repo.get_by_owner_id(current_user.id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found",
            )
        return business.id

    def list_my_places(self, current_user: User) -> list[SponsoredPlace]:
        business_id = self._get_my_business_id(current_user)
        return self.place_repo.list_for_business(business_id)

    def get_my_place(self, current_user: User, place_id: int) -> SponsoredPlace:
        business_id = self._get_my_business_id(current_user)
        place = self.place_repo.get_for_business(business_id, place_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place not found")
        return place

    def create_my_place(self, current_user: User, **payload) -> SponsoredPlace:
        business_id = self._get_my_business_id(current_user)
        payload = self._normalize_payload(payload)
        return self.place_repo.create_for_business(business_id=business_id, **payload)

    def update_my_place(self, current_user: User, place_id: int, **updates) -> SponsoredPlace:
        place = self.get_my_place(current_user, place_id)
        if not updates:
            return place
        # Business cannot approve via this endpoint
        updates.pop("is_approved", None)
        updates = self._normalize_payload(updates)
        return self.place_repo.update(place, **updates)

    def deactivate_my_place(self, current_user: User, place_id: int) -> SponsoredPlace:
        place = self.get_my_place(current_user, place_id)
        return self.place_repo.update(place, is_active=False)

    def _normalize_payload(self, payload: dict) -> dict:
        normalized = dict(payload)
        if "city" in normalized and normalized["city"] is not None:
            normalized["city"] = normalize_city(normalized["city"])
        if "category" in normalized and normalized["category"] is not None:
            normalized["category"] = normalize_category(normalized["category"])
        return normalized
