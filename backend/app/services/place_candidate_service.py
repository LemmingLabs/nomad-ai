import json
import logging
import math
from collections import Counter
from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)

PLACES_BASE_URL = "https://places.googleapis.com/v1"
_place_candidate_service: "PlaceCandidateService | None" = None


class PlaceCandidateService:
    """Retrieve and rank real place candidates from Google Places."""

    INTEREST_TYPE_MAPPING: dict[str, list[str]] = {
        "culture": [
            "museum",
            "tourist_attraction",
            "historical_landmark",
            "cultural_center",
            "church",
            "mosque",
            "cathedral",
            "art_gallery",
        ],
        "history": [
            "museum",
            "historical_landmark",
            "tourist_attraction",
            "cultural_center",
            "monument",
        ],
        "food": [
            "restaurant",
            "cafe",
            "market",
            "bakery",
            "meal_takeaway",
            "food_store",
        ],
        "nature": [
            "park",
            "tourist_attraction",
            "natural_feature",
            "campground",
            "hiking_area",
            "viewpoint",
        ],
        "mountains": [
            "hiking_area",
            "viewpoint",
            "park",
            "national_park",
            "tourist_attraction",
            "natural_feature",
        ],
        "adventure": [
            "hiking_area",
            "tourist_attraction",
            "park",
            "campground",
            "viewpoint",
        ],
        "relaxation": [
            "spa",
            "park",
            "cafe",
            "tourist_attraction",
            "lodging",
        ],
    }

    QUERY_TERMS: dict[str, list[str]] = {
        "culture": [
            "best museums",
            "historic landmarks",
            "cultural centers",
            "church mosque cathedral",
        ],
        "history": [
            "historic landmarks",
            "museums",
            "heritage sites",
        ],
        "food": [
            "best local restaurants",
            "traditional food",
            "cafes",
            "markets",
            "bakeries",
        ],
        "nature": [
            "parks",
            "scenic viewpoints",
            "natural attractions",
            "outdoor attractions",
        ],
        "mountains": [
            "hiking areas",
            "mountain viewpoints",
            "gorges",
            "national parks",
            "alpine nature spots",
        ],
        "adventure": [
            "hiking areas",
            "outdoor activities",
            "scenic viewpoints",
        ],
        "relaxation": [
            "parks",
            "spas",
            "quiet cafes",
            "lakefront",
        ],
    }

    GENERIC_QUERY_TERMS = [
        "top attractions",
        "places to visit",
        "local highlights",
    ]

    BAD_TYPES = {
        "accounting",
        "atm",
        "bank",
        "car_dealer",
        "car_rental",
        "car_repair",
        "courthouse",
        "dentist",
        "doctor",
        "electrician",
        "embassy",
        "finance",
        "insurance_agency",
        "lawyer",
        "local_government_office",
        "moving_company",
        "office",
        "painter",
        "physiotherapist",
        "plumber",
        "police",
        "post_office",
        "primary_school",
        "real_estate_agency",
        "roofing_contractor",
        "school",
        "secondary_school",
        "storage",
        "university",
    }

    TYPE_ALIASES: dict[str, set[str]] = {
        "market": {"market", "supermarket", "grocery_store", "food_store"},
        "viewpoint": {"viewpoint", "tourist_attraction", "point_of_interest"},
        "cultural_center": {"cultural_center", "museum", "art_gallery"},
        "natural_feature": {"natural_feature", "park", "tourist_attraction"},
        "national_park": {"national_park", "park", "tourist_attraction"},
        "hiking_area": {"hiking_area", "park", "tourist_attraction"},
        "historical_landmark": {
            "historical_landmark",
            "tourist_attraction",
            "museum",
            "point_of_interest",
        },
    }

    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self.timeout = timeout
        self._cache: dict[tuple[str, str, int], list[dict]] = {}

    def get_candidates_for_city_and_interest(
        self,
        city: str,
        interest: str,
        limit: int = 10,
        exclude_place_ids: set[str] | None = None,
        exclude_names: set[str] | None = None,
        selected_type_counts: Counter | None = None,
        selected_interest_counts: Counter | None = None,
        previous_interest: str | None = None,
        previous_location: dict | None = None,
    ) -> list[dict]:
        return self.get_candidates_for_day(
            city=city,
            interests=[interest] if interest else [],
            travel_style="",
            limit=limit,
            exclude_place_ids=exclude_place_ids,
            exclude_names=exclude_names,
            selected_type_counts=selected_type_counts,
            selected_interest_counts=selected_interest_counts,
            previous_interest=previous_interest,
            previous_location=previous_location,
        )

    def get_candidates_for_day(
        self,
        city: str,
        interests: list[str],
        travel_style: str,
        user_prompt: str | None = None,
        limit: int = 10,
        exclude_place_ids: set[str] | None = None,
        exclude_names: set[str] | None = None,
        selected_type_counts: Counter | None = None,
        selected_interest_counts: Counter | None = None,
        previous_interest: str | None = None,
        previous_location: dict | None = None,
    ) -> list[dict]:
        normalized_city = self._normalize_text(city)
        if not normalized_city or not self.api_key:
            return []

        normalized_interests = [
            self._normalize_interest(interest)
            for interest in interests
            if self._normalize_interest(interest)
        ]
        if not normalized_interests:
            normalized_interests = self._infer_interests_from_text(
                " ".join([travel_style or "", user_prompt or ""])
            )
        if not normalized_interests:
            normalized_interests = ["culture"]

        cache_key = (
            normalized_city.lower(),
            "|".join(sorted(normalized_interests)),
            max(limit, 10),
        )
        if cache_key in self._cache:
            raw_candidates = [candidate.copy() for candidate in self._cache[cache_key]]
        else:
            raw_candidates = self._retrieve_candidates(
                normalized_city,
                normalized_interests,
                max(limit, 10),
            )
            self._cache[cache_key] = [candidate.copy() for candidate in raw_candidates]

        return self._rank_candidates(
            raw_candidates,
            normalized_interests,
            limit,
            exclude_place_ids or set(),
            exclude_names or set(),
            selected_type_counts or Counter(),
            selected_interest_counts or Counter(),
            self._normalize_interest(previous_interest or ""),
            previous_location,
        )

    def select_best_candidate_with_ai(
        self,
        candidates: list[dict],
        city: str,
        interests: list[str],
        travel_style: str,
        user_prompt: str | None,
    ) -> dict | None:
        if not candidates:
            return None

        fallback_candidate = candidates[0]
        candidate_by_place_id = {
            str(candidate.get("place_id")): candidate
            for candidate in candidates
            if candidate.get("place_id")
        }
        if not candidate_by_place_id:
            return fallback_candidate

        messages = self._build_ai_selection_messages(
            candidates=candidates,
            city=city,
            interests=interests,
            travel_style=travel_style,
            user_prompt=user_prompt,
        )

        try:
            from app.services.ai_service import AIService

            raw = AIService().groq_client.chat_json(messages, mode="place_candidate_selection")
            if isinstance(raw, str):
                raw = json.loads(raw)
            if not isinstance(raw, dict):
                return fallback_candidate

            selected_place_id = str(raw.get("selected_place_id") or "").strip()
            selected_candidate = candidate_by_place_id.get(selected_place_id)
            if not selected_candidate:
                return fallback_candidate
            if self._is_ai_selection_much_worse(selected_candidate, fallback_candidate):
                return fallback_candidate
            return selected_candidate
        except Exception:
            logger.exception("AI place candidate selection failed")
            return fallback_candidate

    def _retrieve_candidates(
        self,
        city: str,
        interests: list[str],
        limit: int,
    ) -> list[dict]:
        candidates_by_id: dict[str, dict] = {}
        seen_names: set[str] = set()
        query_terms = self._build_query_terms(interests)
        target_count = max(limit, 10)

        for query_term in query_terms:
            query = f"{query_term} in {city}"
            places = self._text_search(query, page_size=min(max(limit, 5), 20))
            for place in places:
                candidate = self._normalize_place(place, city)
                place_id = candidate.get("place_id")
                candidate_name = self._normalize_name(candidate.get("name"))
                if not place_id or not self._passes_quality_filter(candidate):
                    continue
                if candidate_name in seen_names:
                    continue
                if place_id and place_id not in candidates_by_id:
                    candidates_by_id[place_id] = candidate
                    if candidate_name:
                        seen_names.add(candidate_name)
                if len(candidates_by_id) >= target_count:
                    break
            if len(candidates_by_id) >= target_count:
                break

        return list(candidates_by_id.values())

    def _text_search(self, query: str, page_size: int = 10) -> list[dict]:
        payload = {
            "textQuery": query,
            "pageSize": page_size,
            "languageCode": "en",
        }
        field_mask = ",".join(
            [
                "places.id",
                "places.displayName",
                "places.formattedAddress",
                "places.location",
                "places.rating",
                "places.userRatingCount",
                "places.types",
                "places.googleMapsUri",
                "places.websiteUri",
                "places.internationalPhoneNumber",
                "places.businessStatus",
            ]
        )

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{PLACES_BASE_URL}/places:searchText",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": self.api_key,
                        "X-Goog-FieldMask": field_mask,
                    },
                )
            response.raise_for_status()
            data = response.json()
            places = data.get("places", [])
            return places if isinstance(places, list) else []
        except httpx.TimeoutException:
            logger.warning("Google Places text search timeout for query: %s", query)
            return []
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Google Places text search failed for query %s: %s",
                query,
                exc.response.status_code,
            )
            return []
        except Exception:
            logger.exception("Google Places text search failed for query: %s", query)
            return []

    def _build_ai_selection_messages(
        self,
        candidates: list[dict],
        city: str,
        interests: list[str],
        travel_style: str,
        user_prompt: str | None,
    ) -> list[dict[str, str]]:
        compact_candidates = [
            {
                "place_id": candidate.get("place_id"),
                "name": candidate.get("name"),
                "types": candidate.get("types", []),
                "rating": candidate.get("rating"),
                "user_rating_count": candidate.get("user_rating_count"),
                "score": candidate.get("score"),
                "formatted_address": candidate.get("formatted_address"),
            }
            for candidate in candidates
            if candidate.get("place_id") and candidate.get("name")
        ]

        payload = {
            "city": city,
            "interests": interests,
            "travel_style": travel_style,
            "user_prompt": user_prompt,
            "candidates": compact_candidates,
        }

        return [
            {
                "role": "system",
                "content": (
                    "You are selecting one real Google Places candidate for a travel itinerary. "
                    "Return only valid JSON with this schema: "
                    '{"selected_place_id":"<one candidate place_id>"}. '
                    "Select the most relevant place for the trip context. Consider interests, "
                    "travel style, and user prompt. Avoid generic tourist traps when a more specific "
                    "and better-matching candidate exists. Prefer high-quality places with strong "
                    "rating and enough reviews. Never invent place ids."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ]

    def _normalize_place(self, place: dict[str, Any], city: str) -> dict:
        location = place.get("location") or {}
        display_name = place.get("displayName") or {}

        return {
            "provider": "google_places",
            "place_id": place.get("id"),
            "name": display_name.get("text") if isinstance(display_name, dict) else None,
            "city": city,
            "formatted_address": place.get("formattedAddress"),
            "lat": location.get("latitude") if isinstance(location, dict) else None,
            "lng": location.get("longitude") if isinstance(location, dict) else None,
            "rating": place.get("rating"),
            "user_rating_count": place.get("userRatingCount"),
            "types": place.get("types") if isinstance(place.get("types"), list) else [],
            "google_maps_uri": place.get("googleMapsUri"),
            "website_uri": place.get("websiteUri"),
            "international_phone_number": place.get("internationalPhoneNumber"),
            "business_status": place.get("businessStatus"),
        }

    def _rank_candidates(
        self,
        candidates: list[dict],
        interests: list[str],
        limit: int,
        exclude_place_ids: set[str],
        exclude_names: set[str],
        selected_type_counts: Counter,
        selected_interest_counts: Counter,
        previous_interest: str | None = None,
        previous_location: dict | None = None,
    ) -> list[dict]:
        ranked = []
        seen_ids = set()
        seen_names = set()
        normalized_exclude_names = {
            self._normalize_name(name)
            for name in exclude_names
            if self._normalize_name(name)
        }

        for candidate in candidates:
            place_id = candidate.get("place_id")
            name = candidate.get("name")
            normalized_name = self._normalize_name(name)
            if not place_id or not name or place_id in seen_ids:
                continue
            if normalized_name in seen_names or normalized_name in normalized_exclude_names:
                continue
            seen_ids.add(place_id)
            if normalized_name:
                seen_names.add(normalized_name)
            if place_id in exclude_place_ids:
                continue
            if candidate.get("business_status") == "CLOSED_PERMANENTLY":
                continue
            if not self._passes_quality_filter(candidate):
                continue

            score = self._score_candidate(
                candidate,
                interests,
                selected_type_counts,
                selected_interest_counts,
                previous_interest,
                previous_location,
            )
            enriched = candidate.copy()
            enriched["score"] = round(score, 4)
            enriched["matched_interest"] = self._best_matched_interest(candidate, interests)
            ranked.append(enriched)

        ranked.sort(key=lambda item: item.get("score", 0), reverse=True)
        return self._apply_type_diversity(ranked, limit)

    def _score_candidate(
        self,
        candidate: dict,
        interests: list[str],
        selected_type_counts: Counter,
        selected_interest_counts: Counter | None = None,
        previous_interest: str | None = None,
        previous_location: dict | None = None,
    ) -> float:
        types = set(candidate.get("types") or [])
        score = 0.0
        selected_interest_counts = selected_interest_counts or Counter()
        matched_interest = self._best_matched_interest(candidate, interests)

        for interest in interests:
            target_types = set(self.INTEREST_TYPE_MAPPING.get(interest, []))
            expanded_target_types = self._expand_types(target_types)
            overlap = types & expanded_target_types
            if overlap:
                score += 4.0 + min(len(overlap), 3) * 0.75

        rating = self._safe_float(candidate.get("rating"))
        if rating:
            score += min(max(rating - 3.0, 0), 2.0) * 1.2

        rating_count = self._safe_int(candidate.get("user_rating_count"))
        if rating_count:
            score += min(math.log10(rating_count + 1), 4.0) * 0.55
            if rating_count < 20:
                score -= 1.5
        else:
            score -= 0.75

        if "tourist_attraction" in types or "point_of_interest" in types:
            score += 0.35

        primary_type = self._primary_type(candidate)
        if primary_type and selected_type_counts.get(primary_type, 0):
            score -= selected_type_counts[primary_type] * 1.2

        if matched_interest:
            score -= selected_interest_counts.get(matched_interest, 0) * 0.6
            if previous_interest and matched_interest == previous_interest:
                score -= 1.0

        if "establishment" in types and len(types) <= 2:
            score -= 0.5

        score -= self._distance_penalty(candidate, previous_location)

        return score

    def _apply_type_diversity(self, ranked: list[dict], limit: int) -> list[dict]:
        selected = []
        type_counts: Counter = Counter()

        for candidate in ranked:
            primary_type = self._primary_type(candidate)
            if primary_type and type_counts[primary_type] >= 2:
                continue
            selected.append(candidate)
            if primary_type:
                type_counts[primary_type] += 1
            if len(selected) >= limit:
                break

        if len(selected) < limit:
            selected_ids = {item.get("place_id") for item in selected}
            for candidate in ranked:
                if candidate.get("place_id") in selected_ids:
                    continue
                selected.append(candidate)
                if len(selected) >= limit:
                    break

        return selected

    def _build_query_terms(self, interests: list[str]) -> list[str]:
        terms = []
        for interest in interests:
            terms.extend(self.QUERY_TERMS.get(interest, []))
        if not terms:
            terms.extend(self.GENERIC_QUERY_TERMS)
        return list(dict.fromkeys(terms))[:2]

    def _passes_quality_filter(self, candidate: dict) -> bool:
        if self._has_bad_type(candidate):
            return False

        rating = self._safe_float(candidate.get("rating"))
        if rating is not None and rating < 3.5:
            return False
        return True

    def _has_bad_type(self, candidate: dict) -> bool:
        types = set(candidate.get("types") or [])
        return bool(types & self.BAD_TYPES)

    def _is_ai_selection_much_worse(self, selected: dict, fallback: dict) -> bool:
        selected_score = self._safe_float(selected.get("score"))
        fallback_score = self._safe_float(fallback.get("score"))
        if selected_score is None or fallback_score is None:
            return False
        if fallback_score <= 0:
            return False
        return selected_score < max(fallback_score - 2.0, fallback_score * 0.7)

    def _distance_penalty(self, candidate: dict, previous_location: dict | None) -> float:
        if not previous_location:
            return 0.0

        lat = self._safe_float(candidate.get("lat"))
        lng = self._safe_float(candidate.get("lng"))
        prev_lat = self._safe_float(previous_location.get("lat"))
        prev_lng = self._safe_float(previous_location.get("lng"))
        if None in {lat, lng, prev_lat, prev_lng}:
            return 0.0

        distance_km = self._haversine_km(prev_lat, prev_lng, lat, lng)
        if distance_km <= 15:
            return 0.0
        if distance_km <= 50:
            return 0.5
        if distance_km <= 100:
            return 1.25
        return 2.0

    @staticmethod
    def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        radius_km = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlng / 2) ** 2
        )
        return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _best_matched_interest(self, candidate: dict, interests: list[str]) -> str | None:
        types = set(candidate.get("types") or [])
        best_interest = None
        best_overlap = 0
        for interest in interests:
            target_types = self._expand_types(set(self.INTEREST_TYPE_MAPPING.get(interest, [])))
            overlap = len(types & target_types)
            if overlap > best_overlap:
                best_interest = interest
                best_overlap = overlap
        return best_interest

    def _primary_type(self, candidate: dict) -> str | None:
        ignored = {"establishment", "point_of_interest"}
        for place_type in candidate.get("types") or []:
            if place_type not in ignored:
                return place_type
        return None

    def _expand_types(self, types: set[str]) -> set[str]:
        expanded = set(types)
        for place_type in list(types):
            expanded.update(self.TYPE_ALIASES.get(place_type, set()))
        return expanded

    def _infer_interests_from_text(self, text: str) -> list[str]:
        normalized = text.lower()
        inferred = []
        keyword_mapping = {
            "culture": ["culture", "museum", "heritage", "history", "landmark"],
            "food": ["food", "restaurant", "cafe", "market", "cuisine"],
            "nature": ["nature", "park", "lake", "outdoor", "scenic"],
            "mountains": ["mountain", "hike", "hiking", "gorge", "alpine"],
        }
        for interest, keywords in keyword_mapping.items():
            if any(keyword in normalized for keyword in keywords):
                inferred.append(interest)
        return inferred

    def _normalize_interest(self, interest: str) -> str:
        normalized = self._normalize_text(interest).lower().replace("-", " ")
        aliases = {
            "cultural": "culture",
            "museums": "culture",
            "historical": "history",
            "local food": "food",
            "cuisine": "food",
            "restaurants": "food",
            "outdoors": "nature",
            "outdoor": "nature",
            "hiking": "mountains",
            "mountain": "mountains",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        return str(value or "").strip()

    @staticmethod
    def _normalize_name(value: Any) -> str:
        normalized = str(value or "").strip().lower()
        return " ".join(normalized.split())

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


def get_place_candidate_service() -> PlaceCandidateService:
    global _place_candidate_service
    if _place_candidate_service is None:
        _place_candidate_service = PlaceCandidateService()
    return _place_candidate_service
