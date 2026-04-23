from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business import Business


class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, business_id: int) -> Business | None:
        return self.db.get(Business, business_id)

    def get_by_owner_id(self, owner_id: int) -> Business | None:
        statement = (
            select(Business)
            .where(Business.owner_id == owner_id)
            .order_by(Business.created_at.desc())
        )
        return self.db.execute(statement).scalar_one_or_none()

    def list_all(self, *, limit: int = 50, offset: int = 0) -> list[Business]:
        statement = (
            select(Business)
            .order_by(Business.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(statement).scalars().all())

    def create(
        self,
        *,
        owner_id: int,
        name: str,
        description: str | None = None,
        contact_phone: str | None = None,
        website_url: str | None = None,
    ) -> Business:
        business = Business(
            owner_id=owner_id,
            name=name,
            description=description,
            contact_phone=contact_phone,
            website_url=website_url,
            is_active=True,
        )
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def update(self, business: Business, **updates) -> Business:
        for key, value in updates.items():
            setattr(business, key, value)
        self.db.commit()
        self.db.refresh(business)
        return business

