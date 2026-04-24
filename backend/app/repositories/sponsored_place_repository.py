from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.sponsored_place import SponsoredPlace


class SponsoredPlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, place_id: int) -> SponsoredPlace | None:
        statement = (
            select(SponsoredPlace)
            .where(SponsoredPlace.id == place_id)
            .options(selectinload(SponsoredPlace.media))
        )
        return self.db.execute(statement).scalar_one_or_none()

    def list_for_business(self, business_id: int) -> list[SponsoredPlace]:
        statement = (
            select(SponsoredPlace)
            .where(SponsoredPlace.business_id == business_id)
            .options(selectinload(SponsoredPlace.media))
            .order_by(SponsoredPlace.created_at.desc())
        )
        return list(self.db.execute(statement).scalars().all())

    def get_for_business(self, business_id: int, place_id: int) -> SponsoredPlace | None:
        statement = (
            select(SponsoredPlace)
            .where(
                SponsoredPlace.id == place_id,
                SponsoredPlace.business_id == business_id,
            )
            .options(selectinload(SponsoredPlace.media))
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_for_business(
        self,
        *,
        business_id: int,
        title: str,
        description: str,
        city: str,
        lat: float,
        lng: float,
        google_place_id: str | None,
        address: str,
        category: str,
        cta_text: str | None,
        contact_phone: str | None,
        website_url: str | None,
    ) -> SponsoredPlace:
        place = SponsoredPlace(
            business_id=business_id,
            title=title,
            description=description,
            city=city,
            lat=lat,
            lng=lng,
            google_place_id=google_place_id,
            address=address,
            category=category,
            cta_text=cta_text,
            contact_phone=contact_phone,
            website_url=website_url,
            is_approved=False,
            is_active=True,
        )
        self.db.add(place)
        self.db.commit()
        self.db.refresh(place)
        return place

    def update(self, place: SponsoredPlace, **updates) -> SponsoredPlace:
        for key, value in updates.items():
            setattr(place, key, value)
        self.db.commit()
        self.db.refresh(place)
        return place

    def list_all(
        self,
        *,
        is_approved: bool | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SponsoredPlace]:
        statement = (
            select(SponsoredPlace)
            .options(selectinload(SponsoredPlace.media))
            .order_by(SponsoredPlace.created_at.desc())
        )
        if is_approved is not None:
            statement = statement.where(SponsoredPlace.is_approved.is_(is_approved))
        if is_active is not None:
            statement = statement.where(SponsoredPlace.is_active.is_(is_active))
        statement = statement.limit(limit).offset(offset)
        return list(self.db.execute(statement).scalars().all())
