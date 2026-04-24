import logging

from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.repositories.trip_message_repository import TripMessageRepository
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService
from fastapi import HTTPException

from app.services.limit_service import LimitService
from app.services.sponsored_injection_service import SponsoredInjectionService
from app.services.usage_service import UsageService


logger = logging.getLogger(__name__)


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
        Return 0-based indexes of days where location/semantic fields changed.
        These are the days that require Google Places / routing / image re-enrichment.
        """
        old_days = old_itinerary.get("days", []) if old_itinerary else []
        new_days = new_itinerary.get("days", []) if new_itinerary else []
        changed: set[int] = set()

        LOC_FIELDS = {"location", "routing_location", "city", "title", "activities"}

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
            if trip.user_id is not None and not LimitService(self.db).can_edit_chat(trip.user_id):
                raise HTTPException(
                    status_code=403,
                    detail="Daily limit exceeded. Upgrade your plan.",
                )
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

                merged_itinerary.setdefault("interests", trip.interests or [])
                merged_itinerary.setdefault("travel_style", trip.travel_style)
                merged_itinerary.setdefault("total_days", trip.days)

                # 2. Detect changes (pre-enrichment)
                force_refresh = any(
                    word in user_content.lower()
                    for word in ["change", "replace", "another", "better", "different"]
                )
                location_changed_indexes = self._detect_location_changed_days(
                    old_itinerary, merged_itinerary
                )
                semantic_changed_indexes = self._detect_changed_days(
                    old_itinerary, merged_itinerary
                )
                missing_place_candidate_indexes: set[int] = set()
                days = merged_itinerary.get("days", [])
                if isinstance(days, list):
                    for idx, day in enumerate(days):
                        if not isinstance(day, dict):
                            continue
                        candidate = day.get("place_candidate")
                        if not isinstance(candidate, dict) or candidate.get("place_id") is None:
                            missing_place_candidate_indexes.add(idx)

                place_candidate_refresh_indexes = location_changed_indexes | missing_place_candidate_indexes
                if force_refresh:
                    place_candidate_refresh_indexes |= semantic_changed_indexes

                logger.info("[DEBUG] force_refresh=%s", force_refresh)
                logger.info("[DEBUG] changed_days=%s", place_candidate_refresh_indexes)
                logger.info("[CONTINUE] location_changed_indexes=%s", location_changed_indexes)
                logger.info(
                    "[CONTINUE] place_candidate_refresh_indexes=%s", place_candidate_refresh_indexes
                )

                # 3. Reset stale fields before re-enrichment
                if place_candidate_refresh_indexes and isinstance(days, list):
                    for idx in sorted(place_candidate_refresh_indexes):
                        if idx < 0 or idx >= len(days):
                            continue
                        day = days[idx]
                        if not isinstance(day, dict):
                            continue
                        day.pop("place_candidate", None)
                        day.pop("images", None)
                        day.pop("route_from_previous", None)

                # 4. Google Places candidate re-enrichment (selective)
                if place_candidate_refresh_indexes:
                    logger.info("[DEBUG] re-enriching places/images")
                    logger.info(
                        "[CONTINUE] re-running Google Places enrichment for changed days"
                    )
                    from app.services.trip_service import (
                        enrich_selected_days_with_place_candidates,
                    )

                    merged_itinerary = enrich_selected_days_with_place_candidates(
                        merged_itinerary,
                        changed_day_indexes=place_candidate_refresh_indexes,
                        interests=list(merged_itinerary.get("interests") or trip.interests or []),
                        travel_style=str(merged_itinerary.get("travel_style") or trip.travel_style),
                        prompt=None,
                    )

                # 5. Catalog enrichment (always, same as before)
                catalog_service = CatalogService(self.db)
                enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(
                    merged_itinerary,
                    trip.budget,
                )

                # After place candidate refresh, routing/images must refresh for the same set
                location_changed_indexes = place_candidate_refresh_indexes

                # 6. Routing enrichment – only when locations actually changed
                if location_changed_indexes:
                    logger.info("[CONTINUE] re-running routing enrichment")
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

                # 7. Image enrichment – only for location-changed days
                from app.services.image_enrichment_service import ImageEnrichmentService
                try:
                    if location_changed_indexes:
                        logger.info("[CONTINUE] re-running image enrichment")
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

                try:
                    enriched_itinerary = SponsoredInjectionService(self.db).inject_sponsored_places(
                        enriched_itinerary,
                        trip_id=trip.id,
                    )
                except Exception as exc:
                    logger.exception("Sponsored injection failed on update: %s", exc)

                trip.itinerary_json = enriched_itinerary
                updated_itinerary = enriched_itinerary
                self.db.add(trip)

            if trip.user_id is not None:
                UsageService(self.db).increment_chat_edit(trip.user_id)

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
