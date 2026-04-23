from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sponsored_impression import SponsoredImpression
from app.models.sponsored_interaction import SponsoredInteraction


class SponsoredAnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_impressions_for_business(self, business_id: int) -> int:
        statement = select(func.count(SponsoredImpression.id)).where(
            SponsoredImpression.business_id == business_id
        )
        return int(self.db.execute(statement).scalar() or 0)

    def count_interactions_for_business(self, business_id: int) -> int:
        statement = select(func.count(SponsoredInteraction.id)).where(
            SponsoredInteraction.business_id == business_id
        )
        return int(self.db.execute(statement).scalar() or 0)

    def interactions_breakdown_for_business(self, business_id: int) -> dict[str, int]:
        statement = (
            select(
                SponsoredInteraction.interaction_type,
                func.count(SponsoredInteraction.id),
            )
            .where(SponsoredInteraction.business_id == business_id)
            .group_by(SponsoredInteraction.interaction_type)
        )
        rows = self.db.execute(statement).all()
        return {
            getattr(interaction_type, "value", str(interaction_type)): int(count)
            for interaction_type, count in rows
        }

    def count_impressions_for_place(self, sponsored_place_id: int) -> int:
        statement = select(func.count(SponsoredImpression.id)).where(
            SponsoredImpression.sponsored_place_id == sponsored_place_id
        )
        return int(self.db.execute(statement).scalar() or 0)

    def count_interactions_for_place(self, sponsored_place_id: int) -> int:
        statement = select(func.count(SponsoredInteraction.id)).where(
            SponsoredInteraction.sponsored_place_id == sponsored_place_id
        )
        return int(self.db.execute(statement).scalar() or 0)

    def interactions_breakdown_for_place(self, sponsored_place_id: int) -> dict[str, int]:
        statement = (
            select(
                SponsoredInteraction.interaction_type,
                func.count(SponsoredInteraction.id),
            )
            .where(SponsoredInteraction.sponsored_place_id == sponsored_place_id)
            .group_by(SponsoredInteraction.interaction_type)
        )
        rows = self.db.execute(statement).all()
        return {
            getattr(interaction_type, "value", str(interaction_type)): int(count)
            for interaction_type, count in rows
        }
