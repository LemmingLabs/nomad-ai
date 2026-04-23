from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_media import BusinessMedia, BusinessMediaType


class BusinessMediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_business(self, business_id: int) -> list[BusinessMedia]:
        statement = (
            select(BusinessMedia)
            .where(BusinessMedia.business_id == business_id)
            .order_by(BusinessMedia.created_at.desc())
        )
        return list(self.db.execute(statement).scalars().all())

    def create(
        self,
        *,
        business_id: int,
        type: BusinessMediaType,
        url: str,
    ) -> BusinessMedia:
        media = BusinessMedia(
            business_id=business_id,
            type=type,
            url=url,
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def get_for_business(self, business_id: int, media_id: int) -> BusinessMedia | None:
        statement = select(BusinessMedia).where(
            BusinessMedia.id == media_id,
            BusinessMedia.business_id == business_id,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def delete(self, media: BusinessMedia) -> None:
        self.db.delete(media)
        self.db.commit()

