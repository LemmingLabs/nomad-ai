import logging
import math
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.sponsored_impression import SponsoredImpression
from app.models.sponsored_place import SponsoredPlace
from app.models.sponsored_place_media import SponsoredPlaceMediaType
from app.services.storage_service import StorageService


logger = logging.getLogger(__name__)
MIN_SCORE = 1
MAX_SPONSORED_PER_TRIP = 2
_LOCAL_DEFAULT_SPONSORED_IMAGES = {
    "restaurant": "/media/defaults/restaurant.svg",
    "activity": "/media/defaults/activity.svg",
    "default": "/media/defaults/place.svg",
}
DEFAULT_SPONSORED_IMAGE = _LOCAL_DEFAULT_SPONSORED_IMAGES["restaurant"]

_CITY_STOPWORDS = {
    "city",
    "center",
    "centre",
    "downtown",
    "kyrgyzstan",
    "kyrgyz",
    "republic",
    "mall",
}
_FOOD_KEYWORDS = {
    "breakfast",
    "brunch",
    "cafe",
    "cafeteria",
    "canteen",
    "coffee",
    "cuisine",
    "dining",
    "dinner",
    "food",
    "food court",
    "lunch",
    "market",
    "meal",
    "restaurant",
    "self service",
    "self-service",
}
_ATTRACTION_KEYWORDS = {
    "attraction",
    "gallery",
    "historic",
    "landmark",
    "museum",
    "park",
    "sightseeing",
    "tour",
}


@dataclass(frozen=True)
class _Coords:
    lat: float
    lng: float


class SponsoredInjectionService:
    def __init__(self, db: Session):
        self.db = db
        self.storage = StorageService()

    def inject_sponsored_places(self, itinerary_json: dict, trip_id: int | None = None) -> dict:
        logger.info("[SPONSORED] Injecting into itinerary...")
        days = itinerary_json.get("days")
        if not isinstance(days, list):
            return itinerary_json

        for day in days:
            if isinstance(day, dict):
                day.pop("sponsored", None)

        used_place_ids: set[int] = set()
        injected_count = 0
        for day in days:
            if not isinstance(day, dict):
                continue

            logger.info(
                "[SPONSORED DEBUG] day=%s city=%s location=%s routing_location=%s activity_types=%s",
                day.get("day"),
                day.get("city"),
                day.get("location"),
                day.get("routing_location"),
                [a.get("type") for a in day.get("activities", []) if isinstance(a, dict)],
            )

            if injected_count >= MAX_SPONSORED_PER_TRIP:
                logger.info(
                    "[SPONSORED] reached trip limit: injected=%s max=%s",
                    injected_count,
                    MAX_SPONSORED_PER_TRIP,
                )
                continue

            day_number = day.get("day")
            if day_number is not None:
                try:
                    day_number = int(day_number)
                except (TypeError, ValueError):
                    day_number = None

            city = str(day.get("city") or "").strip()
            if not city:
                logger.info("[SPONSORED DEBUG] skipping day=%s because city is empty", day.get("day"))
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
                logger.info(
                    "[SPONSORED] no candidate selected for day=%s city=%s desired_categories=%s",
                    day.get("day"),
                    city,
                    sorted(desired_categories or []),
                )
                continue

            used_place_ids.add(candidate.id)
            day["sponsored"] = self._build_day_payload(candidate)
            injected_count += 1
            logger.info(
                "[SPONSORED DEBUG] final sponsored for day=%s -> %s",
                day.get("day"),
                day.get("sponsored"),
            )
            logger.info(
                "[SPONSORED] impression tracked trip_id=%s place_id=%s",
                trip_id,
                candidate.id,
            )
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
        desired: set[str] = set()
        text_chunks = [
            str(day.get("title") or ""),
            str(day.get("location") or ""),
            str(day.get("routing_location") or ""),
        ]

        types: set[str] = set()
        if isinstance(activities, list):
            for activity in activities:
                if not isinstance(activity, dict):
                    continue
                activity_type = str(activity.get("type") or "").strip().lower()
                if activity_type:
                    types.add(activity_type)
                text_chunks.extend(
                    [
                        str(activity.get("title") or ""),
                        str(activity.get("name") or ""),
                        str(activity.get("description") or ""),
                    ]
                )

        if "meal" in types:
            desired.add("restaurant")
        if "sightseeing" in types:
            desired.add("attraction")

        text_blob = self._normalize_text(" ".join(chunk for chunk in text_chunks if chunk))
        if any(keyword in text_blob for keyword in _FOOD_KEYWORDS):
            desired.add("restaurant")
        if any(keyword in text_blob for keyword in _ATTRACTION_KEYWORDS):
            desired.add("attraction")

        logger.info(
            "[SPONSORED DEBUG] inferred desired categories for day=%s -> %s",
            day.get("day"),
            sorted(desired),
        )
        return desired or None

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
        city_norm = normalize_city(city)
        logger.info("[SPONSORED DEBUG] city raw=%s normalized=%s", city, city_norm)
        if not city_norm:
            logger.info("[SPONSORED] city normalization produced empty value for raw=%s", city)
            return None

        statement = (
            select(SponsoredPlace)
            .where(SponsoredPlace.is_active.is_(True))
            .where(SponsoredPlace.is_approved.is_(True))
            .options(
                selectinload(SponsoredPlace.media),
            )
            .limit(250)
        )

        all_candidates = list(self.db.execute(statement).scalars().all())
        logger.info("[SPONSORED] candidates found: %s", len(all_candidates))

        candidates: list[SponsoredPlace] = []
        for place in all_candidates:
            if self._city_matches(city_norm, place.city):
                candidates.append(place)
                continue
            logger.info(
                "[SPONSORED] filtered out place_id=%s title=%s reason=city_mismatch day_city=%s place_city=%s",
                place.id,
                place.title,
                city_norm,
                place.city,
            )
        logger.info(
            "[SPONSORED DEBUG] city=%s matched %s/%s approved active candidates",
            city_norm,
            len(candidates),
            len(all_candidates),
        )
        if not candidates:
            logger.info("[SPONSORED] filtered candidates: 0")
            return None

        filtered: list[SponsoredPlace] = []
        for place in candidates:
            if place.id in used_place_ids:
                logger.info(
                    "[SPONSORED] filtered out place_id=%s title=%s reason=already_used",
                    place.id,
                    place.title,
                )
                continue
            filtered.append(place)
        logger.info("[SPONSORED] filtered candidates: %s", len(filtered))
        if not filtered:
            return None

        desired_categories_norm = {normalize_category(cat) for cat in (desired_categories or set())}

        def score(place: SponsoredPlace) -> tuple[int, float, int]:
            category_score = self._category_match_score(place.category, desired_categories_norm)

            distance_km = 9_999_999.0
            if coords is not None:
                distance_km = self._haversine_km(coords.lat, coords.lng, place.lat, place.lng)

            return (category_score, -distance_km, place.id)

        for place in filtered:
            category_score, distance_score, recency_score = score(place)
            logger.info(
                "[SPONSORED DEBUG] candidate id=%s title=%s city=%s category=%s score=%s distance_score=%s recency=%s",
                place.id,
                place.title,
                place.city,
                place.category,
                category_score,
                distance_score,
                recency_score,
            )

        selected = max(filtered, key=score)
        selected_score, _, _ = score(selected)
        if selected_score < MIN_SCORE:
            logger.info(
                "[SPONSORED] final candidate rejected by MIN_SCORE: place_id=%s score=%s min_score=%s",
                selected.id,
                selected_score,
                MIN_SCORE,
            )
            return None
        logger.info(
            "[SPONSORED] final choice: place_id=%s title=%s city=%s category=%s score=%s",
            selected.id,
            selected.title,
            selected.city,
            selected.category,
            selected_score,
        )
        return selected

    def _build_day_payload(self, place: SponsoredPlace) -> dict:
        images = [
            self.storage.get_access_url(media.url)
            for media in (place.media or [])
            if media.type in {SponsoredPlaceMediaType.IMAGE, SponsoredPlaceMediaType.COVER}
        ]
        if not images:
            fallback_image = self._fallback_image_for_category(place.category)
            logger.warning(
                "[SPONSORED] place_id=%s has no media, using fallback image %s",
                place.id,
                fallback_image,
            )
            images = [fallback_image]

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
        return normalize_category(raw)

    def _fallback_image_for_category(self, category: str | None) -> str:
        default_images = self._default_sponsored_images()
        category_norm = self._normalize_category(category or "")
        if any(token in category_norm for token in {"restaurant", "cafe", "canteen", "food", "self service"}):
            return default_images["restaurant"]
        if any(token in category_norm for token in {"activity", "attraction", "museum", "park", "tour"}):
            return default_images["activity"]
        return default_images["default"]

    def _default_sponsored_images(self) -> dict[str, str]:
        return {
            "restaurant": self.storage.get_access_url(
                settings.DEFAULT_RESTAURANT_IMAGE_URL or _LOCAL_DEFAULT_SPONSORED_IMAGES["restaurant"]
            ),
            "activity": self.storage.get_access_url(
                settings.DEFAULT_ACTIVITY_IMAGE_URL or _LOCAL_DEFAULT_SPONSORED_IMAGES["activity"]
            ),
            "default": self.storage.get_access_url(
                settings.DEFAULT_PLACE_IMAGE_URL or _LOCAL_DEFAULT_SPONSORED_IMAGES["default"]
            ),
        }

    def _category_match_score(self, place_category: str | None, desired: set[str]) -> int:
        if not desired:
            return 0

        place_norm = self._normalize_category(place_category or "")
        if not place_norm:
            return 0
        place_parts = self._split_category_parts(place_category or "")

        desired_norm = {normalize_category(item) for item in desired if normalize_category(item)}

        if place_norm in desired_norm or any(part in desired_norm for part in place_parts):
            return 3

        aliases: dict[str, set[str]] = {
            "restaurant": {
                "restaurant",
                "restaurants",
                "cafe",
                "cafes",
                "canteen",
                "cafeteria",
                "coffee",
                "coffee shop",
                "coffeehouse",
                "bar",
                "bakery",
                "food",
                "food court",
                "dining",
                "dining hall",
                "self service",
                "self service cafe",
                "self service restaurant",
                "self-service",
                "self-service cafe",
                "self-service restaurant",
                "self-service canteen",
                "self service canteen",
                "canteens",
                "foodcourt",
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
            if token_norm in place_norm or token_norm in place_parts:
                return 2

        if "restaurant" in desired_norm and any(token in place_norm for token in aliases["restaurant"]):
            return 1

        return 0

    def _normalize_text(self, raw: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9]+", " ", str(raw or "").lower()).split())

    def _split_category_parts(self, raw: str) -> set[str]:
        normalized_full = self._normalize_category(raw)
        parts = {normalized_full} if normalized_full else set()
        for part in re.split(r"[/&,;|]+", str(raw or "")):
            normalized = self._normalize_category(part)
            if normalized:
                parts.add(normalized)
        return parts

    def _normalize_city(self, raw: str) -> str:
        return normalize_city(raw)

    def _city_matches(self, day_city_norm: str, place_city: str | None) -> bool:
        place_city_norm = self._normalize_city(place_city or "")
        if not place_city_norm:
            return False

        logger.info(
            "[SPONSORED DEBUG] comparing city day_normalized=%s place_raw=%s place_normalized=%s",
            day_city_norm,
            place_city,
            place_city_norm,
        )
        return (
            day_city_norm == place_city_norm
            or day_city_norm.startswith(f"{place_city_norm} ")
            or place_city_norm.startswith(f"{day_city_norm} ")
        )

    def _haversine_km(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lng2 - lng1)

        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c


def normalize_category(raw: str | None) -> str:
    return " ".join(str(raw or "").strip().lower().replace("_", " ").split())


def normalize_city(raw: str | None) -> str:
    cleaned = " ".join(re.sub(r"[^a-z0-9]+", " ", str(raw or "").lower()).split())
    if not cleaned:
        return ""

    tokens = [token for token in cleaned.split() if token not in _CITY_STOPWORDS]
    return " ".join(tokens) or cleaned
