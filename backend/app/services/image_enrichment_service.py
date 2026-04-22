import logging
from app.integrations.pexels_client import PexelsClient

logger = logging.getLogger(__name__)

PHOTO_QUERY_OVERRIDES = {
    "State Historical Museum": "State Historical Museum Bishkek Kyrgyzstan",
    "Issyk-Kul Lakefront": "Issyk Kul lake Cholpon-Ata Kyrgyzstan",
    "Jeti-Oguz Gorge": "Jeti-Oguz Gorge Karakol Kyrgyzstan",
    "Ala-Archa National Park": "Ala-Archa National Park Kyrgyzstan",
    "Osh Bazaar": "Osh Bazaar Bishkek Kyrgyzstan",
    "Ala-Too Square": "Ala-Too Square Bishkek Kyrgyzstan"
}

MAX_IMAGES_FULL_TRIP = 3   # cap only for full (initial) enrichment runs


class ImageEnrichmentService:
    def __init__(self):
        self.client = PexelsClient()

    def enrich_trip_with_images(
        self,
        itinerary_json: dict,
        changed_day_indexes: set[int] | None = None,
        force_refresh: bool = False,
    ) -> dict:
        """
        Enrich days with hero images.

        Args:
            itinerary_json:      The full itinerary dict (mutated in-place).
            changed_day_indexes: Set of 0-based day indices whose location changed.
                                 • None  → full run with MAX_IMAGES_FULL_TRIP cap.
                                 • set   → selective run; all changed days are
                                           refreshed, no count cap applied.
            force_refresh:       Replace image even when the day already has one.
        """
        days = itinerary_json.get("days", [])
        if not isinstance(days, list):
            return itinerary_json

        is_selective = changed_day_indexes is not None

        # Collect already-used photo ids to avoid duplicates across days
        used_photo_ids: set = set()
        for day in days:
            if isinstance(day, dict):
                existing = (day.get("images") or {}).get("hero") or {}
                pid = existing.get("photo_id")
                if pid:
                    used_photo_ids.add(pid)

        # Full-run counter (only relevant when is_selective=False)
        full_run_count = 0

        for idx, day in enumerate(days):
            if not isinstance(day, dict) or "location" not in day:
                continue

            if is_selective:
                # ── SELECTIVE MODE ──────────────────────────────────────
                if idx not in changed_day_indexes:
                    continue  # keep existing image untouched

                # Clear stale image before re-fetching
                old_pid = ((day.get("images") or {}).get("hero") or {}).get("photo_id")
                if old_pid:
                    used_photo_ids.discard(old_pid)
                day.pop("images", None)

                # No count cap in selective mode — refresh every changed day
                image_data = self._fetch_image_for_day(day, itinerary_json, used_photo_ids)
                if image_data:
                    day["images"] = {"hero": image_data, "gallery": []}
                    used_photo_ids.add(image_data["photo_id"])

            else:
                # ── FULL MODE ───────────────────────────────────────────
                if not force_refresh and day.get("images"):
                    continue  # already has an image

                if full_run_count >= MAX_IMAGES_FULL_TRIP:
                    break

                image_data = self._fetch_image_for_day(day, itinerary_json, used_photo_ids)
                if image_data:
                    day["images"] = {"hero": image_data, "gallery": []}
                    used_photo_ids.add(image_data["photo_id"])
                    full_run_count += 1

        return itinerary_json

    def _fetch_image_for_day(self, day: dict, itinerary: dict, used_ids: set) -> dict | None:
        queries = self._build_search_queries(day, itinerary)
        for q in queries:
            result = self.client.search_photo(q)
            if result and result["photo_id"] not in used_ids:
                return result
        return None

    def _build_search_queries(self, day: dict, itinerary: dict) -> list[str]:
        queries = []
        routing_loc = day.get("routing_location")
        loc = day.get("location")
        city = day.get("city", "")

        if loc and loc in PHOTO_QUERY_OVERRIDES:
            queries.append(PHOTO_QUERY_OVERRIDES[loc])

        suffix = "Kyrgyzstan"

        if routing_loc:
            queries.append(f"{routing_loc} {city} {suffix}".strip())

        if loc:
            queries.append(f"{loc} {city} {suffix}".strip())

        interests = itinerary.get("interests", [])
        themes = ["mountains", "nature", "lake", "culture", "city", "food"]

        theme_added = False
        for interest in interests:
            if interest.lower() in themes:
                if city:
                    queries.append(f"{interest} {city} {suffix}".strip())
                else:
                    queries.append(f"{interest} {suffix}".strip())
                theme_added = True
                break

        if not theme_added:
            queries.append(f"{city} {suffix}".strip() if city else "Kyrgyzstan nature")

        clean_queries = []
        for q in queries:
            cleaned = " ".join(q.split())
            if cleaned and cleaned not in clean_queries:
                clean_queries.append(cleaned)

        return clean_queries
