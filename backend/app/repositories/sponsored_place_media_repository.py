from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sponsored_place_media import SponsoredPlaceMedia, SponsoredPlaceMediaType


class SponsoredPlaceMediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_place(self, sponsored_place_id: int) -> list[SponsoredPlaceMedia]:
        statement = (
            select(SponsoredPlaceMedia)
            .where(SponsoredPlaceMedia.sponsored_place_id == sponsored_place_id)
            .order_by(SponsoredPlaceMedia.created_at.desc(), SponsoredPlaceMedia.id.desc())
        )
        return list(self.db.execute(statement).scalars().all())

    def create(
        self,
        *,
        sponsored_place_id: int,
        type: SponsoredPlaceMediaType,
        url: str,
        filename: str,
        content_type: str,
    ) -> SponsoredPlaceMedia:
        media = SponsoredPlaceMedia(
            sponsored_place_id=sponsored_place_id,
            type=type,
            url=url,
            filename=filename,
            content_type=content_type,
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def get_for_place(self, sponsored_place_id: int, media_id: int) -> SponsoredPlaceMedia | None:
        statement = select(SponsoredPlaceMedia).where(
            SponsoredPlaceMedia.id == media_id,
            SponsoredPlaceMedia.sponsored_place_id == sponsored_place_id,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def delete(self, media: SponsoredPlaceMedia) -> None:
        self.db.delete(media)
        self.db.commit()
