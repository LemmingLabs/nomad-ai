from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.business_media import BusinessMedia, BusinessMediaType
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.business_media_repository import BusinessMediaRepository


class BusinessService:
    def __init__(self, db: Session):
        self.db = db
        self.business_repo = BusinessRepository(db)
        self.media_repo = BusinessMediaRepository(db)

    def get_my_business(self, current_user: User) -> Business:
        business = self.business_repo.get_by_owner_id(current_user.id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found",
            )
        return business

    def create_my_business(self, current_user: User, *, name: str, description: str | None, contact_phone: str | None, website_url: str | None) -> Business:
        existing = self.business_repo.get_by_owner_id(current_user.id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Business profile already exists",
            )
        return self.business_repo.create(
            owner_id=current_user.id,
            name=name,
            description=description,
            contact_phone=contact_phone,
            website_url=website_url,
        )

    def update_my_business(self, current_user: User, **updates) -> Business:
        business = self.get_my_business(current_user)
        if not updates:
            return business
        return self.business_repo.update(business, **updates)

    def list_my_media(self, current_user: User) -> list[BusinessMedia]:
        business = self.get_my_business(current_user)
        return self.media_repo.list_for_business(business.id)

    def add_my_media(self, current_user: User, *, type: BusinessMediaType, url: str) -> BusinessMedia:
        business = self.get_my_business(current_user)
        return self.media_repo.create(business_id=business.id, type=type, url=url)

    def delete_my_media(self, current_user: User, media_id: int) -> None:
        business = self.get_my_business(current_user)
        media = self.media_repo.get_for_business(business.id, media_id)
        if media is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
        self.media_repo.delete(media)
