import copy
from sqlalchemy.orm import Session

from app.models.place import Place
from app.repositories.hotel_repository import HotelRepository
from app.repositories.place_repository import PlaceRepository


class CatalogService:
    def __init__(self, db: Session):
        self.db = db
        self.hotel_repo = HotelRepository(db)
        self.place_repo = PlaceRepository(db)

    def normalize_budget(self, budget: str) -> str:
        if not budget:
            return "medium"
        normalized = budget.strip().lower()
        if normalized in {"low", "medium", "high"}:
            return normalized
        return "medium"

    def _get_best_rated(self, items: list, exclude_ids: set | None = None):
        if exclude_ids:
            items = [item for item in items if item.id not in exclude_ids]
        if not items:
            return None
        return max(items, key=lambda x: x.rating or 0.0)

    def select_hotel_for_city(self, city: str, budget: str) -> dict | None:
        if not city:
            return None

        normalized_budget = self.normalize_budget(budget)

        hotels = self.hotel_repo.get_hotels_by_city_and_price_level(city, normalized_budget)
        if not hotels:
            hotels = self.hotel_repo.get_hotels_by_city(city)

        best_hotel = self._get_best_rated(hotels)
        if not best_hotel:
            return None

        return {
            "id": best_hotel.id,
            "name": best_hotel.name,
            "city": best_hotel.city,
            "rating": best_hotel.rating,
            "price_level": best_hotel.price_level,
            "price_from": best_hotel.price_from,
            "address": best_hotel.address,
            "image_url": best_hotel.image_url,
        }

    def select_places_for_city(
        self, city: str, budget: str, exclude_ids: set
    ) -> list[dict]:
        if not city:
            return []

        normalized_budget = self.normalize_budget(budget)
        results = []

        # 1. Cafe or Restaurant
        food_places = self.place_repo.get_places_by_city_type_and_price_level(
            city, "restaurant", normalized_budget
        )
        if not food_places:
            food_places = self.place_repo.get_places_by_city_type_and_price_level(
                city, "cafe", normalized_budget
            )
        if not food_places:
            food_places = self.place_repo.get_places_by_city_and_type(city, "restaurant")
        if not food_places:
            food_places = self.place_repo.get_places_by_city_and_type(city, "cafe")

        best_food = self._get_best_rated(food_places, exclude_ids)
        if best_food:
            results.append(self._place_to_dict(best_food))
            exclude_ids.add(best_food.id)

        # 2. Attraction or Activity
        activity_places = self.place_repo.get_places_by_city_type_and_price_level(
            city, "attraction", normalized_budget
        )
        if not activity_places:
            activity_places = self.place_repo.get_places_by_city_type_and_price_level(
                city, "activity", normalized_budget
            )
        if not activity_places:
            activity_places = self.place_repo.get_places_by_city_and_type(city, "attraction")
        if not activity_places:
            activity_places = self.place_repo.get_places_by_city_and_type(city, "activity")

        best_activity = self._get_best_rated(activity_places, exclude_ids)
        if best_activity:
            results.append(self._place_to_dict(best_activity))
            exclude_ids.add(best_activity.id)

        return results

    def _place_to_dict(self, place: Place) -> dict:
        return {
            "id": place.id,
            "name": place.name,
            "city": place.city,
            "rating": place.rating,
            "type": place.type,
            "price_level": place.price_level,
            "address": place.address,
            "image_url": place.image_url,
        }

    def enrich_itinerary_with_catalog(self, itinerary: dict, budget: str) -> dict:
        if not itinerary or "days" not in itinerary:
            return itinerary

        normalized_budget = self.normalize_budget(budget)
        enriched_itinerary = copy.deepcopy(itinerary)
        seen_place_ids = set()

        for day in enriched_itinerary["days"]:
            city = day.get("city") or day.get("location")
            if not city:
                city = "Bishkek"

            hotel = self.select_hotel_for_city(city, normalized_budget)
            if hotel:
                day["hotel"] = hotel

            places = self.select_places_for_city(city, normalized_budget, seen_place_ids)
            if places:
                day["recommended_places"] = places

        return enriched_itinerary
