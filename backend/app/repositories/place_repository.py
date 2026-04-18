from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.models.place import Place


class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_places(self) -> list[Place]:
        stmt = select(Place).where(Place.is_active.is_(True)).order_by(Place.id.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_places_by_city(self, city: str) -> list[Place]:
        stmt = (
            select(Place)
            .where(Place.is_active.is_(True))
            .where(func.lower(Place.city) == city.lower())
            .order_by(Place.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_places_by_city_and_type(self, city: str, place_type: str) -> list[Place]:
        stmt = (
            select(Place)
            .where(Place.is_active.is_(True))
            .where(func.lower(Place.city) == city.lower())
            .where(func.lower(Place.type) == place_type.lower())
            .order_by(Place.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_places_by_city_type_and_price_level(
        self, city: str, place_type: str, price_level: str
    ) -> list[Place]:
        stmt = (
            select(Place)
            .where(Place.is_active.is_(True))
            .where(func.lower(Place.city) == city.lower())
            .where(func.lower(Place.type) == place_type.lower())
            .where(func.lower(Place.price_level) == price_level.lower())
            .order_by(Place.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_place_by_id(self, place_id: int) -> Place | None:
        stmt = select(Place).where(Place.id == place_id)
        return self.db.execute(stmt).scalar_one_or_none()
