from sqlalchemy.orm import Session

from app.models.sponsored_interaction import SponsoredInteraction, SponsoredInteractionType
from app.repositories.sponsored_place_repository import SponsoredPlaceRepository


class SponsoredAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.place_repo = SponsoredPlaceRepository(db)

    def log_interaction(
        self,
        *,
        sponsored_place_id: int,
        business_id: int,
        interaction_type: SponsoredInteractionType,
        trip_id: int | None = None,
    ) -> SponsoredInteraction:
        place = self.place_repo.get_by_id(sponsored_place_id)
        if place is None:
            raise ValueError("Sponsored place not found")
        if place.business_id != business_id:
            raise ValueError("Business does not own this sponsored place")

        interaction = SponsoredInteraction(
            trip_id=trip_id,
            sponsored_place_id=sponsored_place_id,
            business_id=business_id,
            interaction_type=interaction_type,
        )
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction
