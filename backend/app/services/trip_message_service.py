from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.repositories.trip_message_repository import TripMessageRepository
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService


class TripMessageService:
    def __init__(
        self,
        db,
        ai_service: AIService | None = None,
        repository: TripMessageRepository | None = None,
    ):
        self.db = db
        self.repo = repository or TripMessageRepository(db)
        self.ai_service = ai_service or AIService()

    # ------------------------------------------------------------------
    # Itinerary merge helpers
    # ------------------------------------------------------------------

    def _merge_itinerary(
        self,
        current_itinerary: dict,
        updated_itinerary: dict,
    ) -> dict:
        merged = dict(current_itinerary) if current_itinerary else {}
        merged.update(updated_itinerary)

        allowed_keys = {"summary", "days", "total_days", "interests", "travel_style"}
        merged = {k: v for k, v in merged.items() if k in allowed_keys}

        mapping = {
            "ala-archa": "Bishkek",
            "chuy": "Bishkek",
            "jeti-oguz": "Karakol",
            "jeti oguz": "Karakol",
            "altyn arashan": "Karakol",
            "altyn-arashan": "Karakol",
            "cholpon-ata": "Cholpon-Ata",
            "bosteri": "Cholpon-Ata",
            "suusamyr": "Bishkek",
            "son-kul": "Kochkor",
            "tash-rabat": "Naryn"
        }

        if "days" in merged and isinstance(merged["days"], list):
            for day in merged["days"]:
                if isinstance(day, dict):
                    city = str(day.get("city", "")).strip().lower()
                    if city in mapping:
                        day["city"] = mapping[city]

        return merged

    # ------------------------------------------------------------------
    # Diff-detection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_day_snapshot(day: dict) -> dict:
        """Return the fields we care about for change detection."""
        return {
            "location": day.get("location"),
            "routing_location": day.get("routing_location"),
            "city": day.get("city"),
            "title": day.get("title"),
            "activities": day.get("activities"),
        }

    def _detect_changed_days(
        self,
        old_itinerary: dict,
        new_itinerary: dict,
    ) -> set[int]:
        """
        Return 0-based indexes of days where *any* key field changed.
        Includes location, routing_location, city, title, activities.
        """
        old_days = old_itinerary.get("days", []) if old_itinerary else []
        new_days = new_itinerary.get("days", []) if new_itinerary else []
        changed: set[int] = set()

        for idx, new_day in enumerate(new_days):
            if not isinstance(new_day, dict):
                continue
            if idx >= len(old_days) or not isinstance(old_days[idx], dict):
                # New day added → consider it changed
                changed.add(idx)
                continue
            if self._get_day_snapshot(old_days[idx]) != self._get_day_snapshot(new_day):
                changed.add(idx)

        return changed

    def _detect_location_changed_days(
        self,
        old_itinerary: dict,
        new_itinerary: dict,
    ) -> set[int]:
        """
        Return 0-based indexes of days where location-sensitive fields changed:
        location, routing_location, or city.
        These are the days that require image and routing re-enrichment.
        """
        old_days = old_itinerary.get("days", []) if old_itinerary else []
        new_days = new_itinerary.get("days", []) if new_itinerary else []
        changed: set[int] = set()

        LOC_FIELDS = {"location", "routing_location", "city"}

        for idx, new_day in enumerate(new_days):
            if not isinstance(new_day, dict):
                continue
            if idx >= len(old_days) or not isinstance(old_days[idx], dict):
                changed.add(idx)
                continue
            old_day = old_days[idx]
            for field in LOC_FIELDS:
                if old_day.get(field) != new_day.get(field):
                    changed.add(idx)
                    break

        return changed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def continue_trip(
        self, trip: Trip, user_content: str
    ) -> tuple[TripMessage, dict | None]:
        try:
            self.repo.create_message(trip_id=trip.id, role="user", content=user_content)

            history, _ = self.repo.get_trip_messages(trip_id=trip.id)
            assistant_text, updated_itinerary = self.ai_service.continue_trip(
                history_messages=history,
                user_message=user_content,
                current_itinerary=trip.itinerary_json,
            )

            assistant_message = self.repo.create_message(
                trip_id=trip.id,
                role="assistant",
                content=assistant_text,
            )

            if updated_itinerary is not None:
                old_itinerary = trip.itinerary_json or {}

                # 1. Merge + normalize city names
                merged_itinerary = self._merge_itinerary(
                    current_itinerary=old_itinerary,
                    updated_itinerary=updated_itinerary,
                )

                # 2. Catalog enrichment (always, same as before)
                catalog_service = CatalogService(self.db)
                enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(
                    merged_itinerary,
                    trip.budget,
                )

                # 3. Detect which days had location-sensitive changes
                location_changed_indexes = self._detect_location_changed_days(
                    old_itinerary, enriched_itinerary
                )

                # 4. Routing enrichment – only when locations actually changed
                if location_changed_indexes:
                    from app.utils.async_runner import run_async
                    from app.services.routing_service import RoutingService
                    try:
                        enriched_itinerary = run_async(
                            RoutingService().enrich_from_itinerary_json(enriched_itinerary)
                        )
                    except Exception as exc:
                        print(f"Routing enrichment failed on update: {exc}")
                else:
                    # Preserve existing route_from_previous values from old itinerary
                    old_days = old_itinerary.get("days", [])
                    new_days = enriched_itinerary.get("days", [])
                    for idx, new_day in enumerate(new_days):
                        if isinstance(new_day, dict) and idx < len(old_days):
                            old_day = old_days[idx]
                            if isinstance(old_day, dict) and "route_from_previous" in old_day:
                                new_day.setdefault(
                                    "route_from_previous", old_day["route_from_previous"]
                                )

                # 5. Image enrichment – only for location-changed days
                from app.services.image_enrichment_service import ImageEnrichmentService
                try:
                    if location_changed_indexes:
                        # Selective: only re-fetch images for changed days
                        enriched_itinerary = ImageEnrichmentService().enrich_trip_with_images(
                            enriched_itinerary,
                            changed_day_indexes=location_changed_indexes,
                        )
                    else:
                        # No location changes → carry over existing images, fill missing only
                        old_days = old_itinerary.get("days", [])
                        new_days = enriched_itinerary.get("days", [])
                        for idx, new_day in enumerate(new_days):
                            if isinstance(new_day, dict) and idx < len(old_days):
                                old_day = old_days[idx]
                                if isinstance(old_day, dict) and old_day.get("images"):
                                    new_day.setdefault("images", old_day["images"])
                        # Still fill any missing images (e.g. newly-added days)
                        missing_indexes = {
                            idx
                            for idx, d in enumerate(new_days)
                            if isinstance(d, dict) and not d.get("images")
                        }
                        if missing_indexes:
                            enriched_itinerary = ImageEnrichmentService().enrich_trip_with_images(
                                enriched_itinerary,
                                changed_day_indexes=missing_indexes,
                            )
                except Exception as exc:
                    print(f"Image enrichment failed on update: {exc}")

                trip.itinerary_json = enriched_itinerary
                updated_itinerary = enriched_itinerary
                self.db.add(trip)

            self.db.commit()
            self.db.refresh(assistant_message)
            return assistant_message, updated_itinerary

        except Exception:
            self.db.rollback()
            raise

    def get_trip_messages(
        self, trip: Trip, limit: int = 50, offset: int = 0
    ) -> tuple[list[TripMessage], int]:
        return self.repo.get_trip_messages(trip.id, limit=limit, offset=offset)
