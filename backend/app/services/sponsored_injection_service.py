import logging
import math
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.business import Business
from app.models.business_media import BusinessMediaType
from app.models.sponsored_impression import SponsoredImpression
from app.models.sponsored_place import SponsoredPlace


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Coords:
    lat: float
    lng: float


class SponsoredInjectionService:
    def __init__(self, db: Session):
        self.db = db

    def inject_sponsored_places(self, itinerary_json: dict, trip_id: int | None = None) -> dict:
        logger.info("[SPONSORED] Injecting into itinerary...")
        days = itinerary_json.get("days")
        if not isinstance(days, list):
            return itinerary_json

        used_place_ids: set[int] = set()
        for day in days:
            if not isinstance(day, dict):
                continue

            if day.get("sponsored"):
                continue

            day_number = day.get("day")
            if day_number is not None:
                try:
                    day_number = int(day_number)
                except (TypeError, ValueError):
                    day_number = None

            city = str(day.get("city") or "").strip()
            if not city:
                continue

            desired_categories = self._infer_desired_categories(day)
            coords = self._extract_day_coords(day)

            candidate = self._pick_best_candidate(
                city=city,
                desired_categories=desired_categories,
                coords=coords,
                used_place_ids=used_place_ids,
            )
            if candidate is None:
                continue

            used_place_ids.add(candidate.id)
            day["sponsored"] = self._build_day_payload(candidate)
            self.db.add(
                SponsoredImpression(
                    trip_id=trip_id,
                    sponsored_place_id=candidate.id,
                    business_id=candidate.business_id,
                    day_number=day_number,
                    city=city,
                )
            )

        logger.info("[SPONSORED] Injection complete")
        return itinerary_json

    def _infer_desired_categories(self, day: dict) -> set[str] | None:
        activities = day.get("activities")
        if not isinstance(activities, list):
            return None

        types = {
            str(activity.get("type") or "").strip().lower()
            for activity in activities
            if isinstance(activity, dict)
        }

        if "meal" in types:
            return {"restaurant"}
        if "sightseeing" in types:
            return {"attraction"}
        return None

    def _extract_day_coords(self, day: dict) -> _Coords | None:
        candidate = day.get("place_candidate")
        if not isinstance(candidate, dict):
            return None

        lat = candidate.get("lat")
        lng = candidate.get("lng")
        if lat is None or lng is None:
            return None

        try:
            return _Coords(lat=float(lat), lng=float(lng))
        except (TypeError, ValueError):
            return None

    def _pick_best_candidate(
        self,
        city: str,
        desired_categories: set[str] | None,
        coords: _Coords | None,
        used_place_ids: set[int],
    ) -> SponsoredPlace | None:
        city_norm = " ".join(city.strip().lower().split())

        statement = (
            select(SponsoredPlace)
            .where(SponsoredPlace.is_active.is_(True))
            .where(SponsoredPlace.is_approved.is_(True))
            .where(func.lower(func.trim(SponsoredPlace.city)) == city_norm)
            .options(
                selectinload(SponsoredPlace.business).selectinload(Business.media),
            )
            .limit(100)
        )

        candidates = list(self.db.execute(statement).scalars().all())
        if not candidates:
            return None

        filtered = [place for place in candidates if place.id not in used_place_ids]
        if not filtered:
            return None

        desired_categories_norm = {self._normalize_category(cat) for cat in (desired_categories or set())}

        def score(place: SponsoredPlace) -> tuple[int, float, int]:
            category_score = self._category_match_score(place.category, desired_categories_norm)

            distance_km = 9_999_999.0
            if coords is not None:
                distance_km = self._haversine_km(coords.lat, coords.lng, place.lat, place.lng)

            # Higher is better:
            # - match category first (with aliases)
            # - then closer distance
            # - then newer places (by id)
            return (category_score, -distance_km, place.id)

        return max(filtered, key=score)

    def _build_day_payload(self, place: SponsoredPlace) -> dict:
        images: list[str] = []
        business = place.business
        if business is not None:
            for media in business.media or []:
                if media.type == BusinessMediaType.IMAGE:
                    images.append(media.url)

        return {
            "is_sponsored": True,
            "badge": "Partner Pick",
            "place": {
                "id": place.id,
                "business_id": place.business_id,
                "title": place.title,
                "description": place.description,
                "cta": place.cta_text,
                "images": images,
                "contact": place.contact_phone,
                "website": place.website_url,
                "category": place.category,
                "address": place.address,
            },
        }

    def _normalize_category(self, raw: str) -> str:
        return " ".join(str(raw or "").strip().lower().replace("_", " ").split())

    def _category_match_score(self, place_category: str | None, desired: set[str]) -> int:
        if not desired:
            return 0

        place_norm = self._normalize_category(place_category or "")
        if not place_norm:
            return 0

        desired_norm = {self._normalize_category(item) for item in desired if self._normalize_category(item)}

        if place_norm in desired_norm:
            return 3

        aliases: dict[str, set[str]] = {
            "restaurant": {
                "restaurant",
                "restaurants",
                "cafe",
                "cafes",
                "coffee",
                "coffee shop",
                "coffeehouse",
                "bar",
                "bakery",
                "food",
                "dining",
            },
            "attraction": {
                "attraction",
                "tourist attraction",
                "tourist_attraction",
                "sightseeing",
                "activity",
                "activities",
                "tour",
                "tours",
                "museum",
                "park",
                "landmark",
            },
        }

        expanded: set[str] = set()
        for item in desired_norm:
            expanded.add(item)
            expanded.update(aliases.get(item, set()))

        for token in sorted(expanded, key=len, reverse=True):
            token_norm = self._normalize_category(token)
            if not token_norm:
                continue
            if token_norm in place_norm:
                return 2

        return 0

    def _haversine_km(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lng2 - lng1)

        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
