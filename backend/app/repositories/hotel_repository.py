from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.models.hotel import Hotel


class HotelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_hotels(self) -> list[Hotel]:
        stmt = select(Hotel).where(Hotel.is_active.is_(True)).order_by(Hotel.id.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_hotels_by_city(self, city: str) -> list[Hotel]:
        stmt = (
            select(Hotel)
            .where(Hotel.is_active.is_(True))
            .where(func.lower(Hotel.city) == city.lower())
            .order_by(Hotel.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_hotels_by_city_and_price_level(self, city: str, price_level: str) -> list[Hotel]:
        stmt = (
            select(Hotel)
            .where(Hotel.is_active.is_(True))
            .where(func.lower(Hotel.city) == city.lower())
            .where(func.lower(Hotel.price_level) == price_level.lower())
            .order_by(Hotel.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_hotel_by_id(self, hotel_id: int) -> Hotel | None:
        stmt = select(Hotel).where(Hotel.id == hotel_id)
        return self.db.execute(stmt).scalar_one_or_none()
