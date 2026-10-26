import logging
from copy import deepcopy

from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.repositories.trip_message_repository import TripMessageRepository
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService
from fastapi import HTTPException

from app.services.limit_service import LimitService
from app.services.sponsored_injection_service import SponsoredInjectionService
from app.services.usage_service import UsageService
from app.services.itinerary_quality_service import validate_itinerary_quality


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
        provider_itinerary = {
            key: value
            for key, value in updated_itinerary.items()
            if key not in {"generation_status", "quality_warnings", "route_status"}
        }
        old_days = merged.get("days")
        new_days = provider_itinerary.get("days")
        if isinstance(old_days, list) and isinstance(new_days, list):
            merged_days = deepcopy(new_days)
            location_fields = ("city", "location", "routing_location")
            activity_detail_fields = (
                "time_window",
                "duration_minutes",
                "duration_status",
                "practical_details",
                "content_status",
            )
            for index, new_day in enumerate(merged_days):
                if (
                    index >= len(old_days)
                    or not isinstance(old_days[index], dict)
                    or not isinstance(new_day, dict)
                ):
                    continue
                old_day = old_days[index]
                same_location = all(
                    old_day.get(field) == new_day.get(field) for field in location_fields
                )
                if not same_location:
                    continue

                preserved_day = deepcopy(old_day)
                preserved_day.update(new_day)
                old_activities = old_day.get("activities")
                new_activities = new_day.get("activities")
                if isinstance(old_activities, list) and isinstance(new_activities, list):
                    merged_activities = deepcopy(new_activities)
                    for activity_index, activity in enumerate(merged_activities):
                        if (
                            activity_index >= len(old_activities)
                            or not isinstance(old_activities[activity_index], dict)
                            or not isinstance(activity, dict)
                        ):
                            continue
                        old_activity = old_activities[activity_index]
                        if any(
                            old_activity.get(field) != activity.get(field)
                            for field in ("time", "description", "type")
                        ):
                            continue
                        for field in activity_detail_fields:
                            if activity.get(field) is None and field in old_activity:
                                activity[field] = old_activity[field]
                    preserved_day["activities"] = merged_activities
                merged_days[index] = preserved_day
            provider_itinerary["days"] = merged_days
        merged.update(provider_itinerary)

        allowed_keys = {
            "summary",
            "days",
            "total_days",
            "interests",
            "travel_style",
            "generation_status",
            "quality_warnings",
            "route_status",
        }
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

    @staticmethod
    def _preserve_stale_routes(
        itinerary: dict, old_itinerary: dict, changed_indexes: set[int]
    ) -> bool:
        """Keep an old route visible as stale when a refreshed route is unavailable."""
        days = itinerary.get("days")
        old_days = old_itinerary.get("days") if isinstance(old_itinerary, dict) else None
        if not isinstance(days, list) or not isinstance(old_days, list):
            return False

        had_unavailable_route = False
        for index in changed_indexes:
            if index <= 0 or index >= len(days) or index >= len(old_days):
                continue
            day = days[index]
            old_day = old_days[index]
            if not isinstance(day, dict) or not isinstance(old_day, dict):
                continue
            route = day.get("route_from_previous")
            if isinstance(route, dict) and route.get("status") == "available":
                continue

            had_unavailable_route = True
            old_route = old_day.get("route_from_previous")
            if isinstance(old_route, dict) and old_route.get("status", "available") == "available":
                day["route_from_previous"] = {**old_route, "status": "stale"}

        if had_unavailable_route:
            itinerary["route_status"] = "unavailable"
        return had_unavailable_route

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
                country_code=trip.country_code,
                destination_id=trip.destination_id,
            )

            if updated_itinerary is not None and (
                assistant_text.lower().startswith("mock response:")
                or not isinstance(updated_itinerary.get("days"), list)
                or not updated_itinerary.get("days")
                or any(not isinstance(day, dict) for day in updated_itinerary.get("days", []))
            ):
                updated_itinerary = None
                assistant_text = (
                    "I couldn't update the itinerary because the planning service did not return a usable plan. "
                    "Your saved itinerary is unchanged. Please try again later."
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
                location_changed_indexes = self._detect_location_changed_days(
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
                    from app.core.destination_registry import resolve_destination

                    destination = resolve_destination(
                        country_code=trip.country_code,
                        destination_id=trip.destination_id,
                    )

                    merged_itinerary = enrich_selected_days_with_place_candidates(
                        merged_itinerary,
                        changed_day_indexes=place_candidate_refresh_indexes,
                        interests=list(merged_itinerary.get("interests") or trip.interests or []),
                        travel_style=str(merged_itinerary.get("travel_style") or trip.travel_style),
                        prompt=None,
                        country_code=destination.country_code,
                        country_name=destination.country_name,
                    )

                # 5. Catalog enrichment (always, same as before)
                catalog_service = CatalogService(self.db)
                from app.core.destination_registry import resolve_destination

                destination = resolve_destination(
                    country_code=trip.country_code,
                    destination_id=trip.destination_id,
                )
                enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(
                    merged_itinerary,
                    trip.budget,
                    country_code=destination.country_code,
                )

                # After place candidate refresh, routing/images must refresh for the same set
                location_changed_indexes = place_candidate_refresh_indexes

                # 6. Routing enrichment – only when locations actually changed
                enrichment_reasons: list[str] = []
                if location_changed_indexes:
                    logger.info("[CONTINUE] re-running routing enrichment")
                    from app.utils.async_runner import run_async
                    from app.services.routing_service import RoutingService
                    try:
                        enriched_itinerary = run_async(
                            RoutingService(
                                country_code=destination.country_code,
                                center_latitude=destination.center_latitude,
                                center_longitude=destination.center_longitude,
                            ).enrich_from_itinerary_json(enriched_itinerary)
                        )
                    except Exception as exc:
                        print(f"Routing enrichment failed on update: {exc}")
                        enriched_itinerary["route_status"] = "unavailable"
                        enrichment_reasons.append("routing_refresh_failed")
                    if self._preserve_stale_routes(
                        enriched_itinerary, old_itinerary, location_changed_indexes
                    ):
                        enrichment_reasons.append("routing_refresh_unavailable")
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
                            country_name=destination.country_name,
                            country_code=destination.country_code,
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
                                country_name=destination.country_name,
                                country_code=destination.country_code,
                            )
                except Exception as exc:
                    print(f"Image enrichment failed on update: {exc}")
                    enrichment_reasons.append("image_refresh_unavailable")

                try:
                    enriched_itinerary = SponsoredInjectionService(self.db).inject_sponsored_places(
                        enriched_itinerary,
                        trip_id=trip.id,
                        country_code=destination.country_code,
                    )
                except Exception as exc:
                    logger.exception("Sponsored injection failed on update: %s", exc)

                if enrichment_reasons:
                    generation = enriched_itinerary.get("generation_status") or {
                        "state": "complete",
                        "source": "ai",
                        "reasons": [],
                    }
                    enriched_itinerary["generation_status"] = {
                        "state": "degraded",
                        "source": generation.get("source", "ai"),
                        "reasons": list(
                            dict.fromkeys(generation.get("reasons", []) + enrichment_reasons)
                        ),
                    }
                elif enriched_itinerary.get("route_status") == "unavailable":
                    generation = enriched_itinerary.get("generation_status") or {
                        "state": "complete",
                        "source": "ai",
                        "reasons": [],
                    }
                    enriched_itinerary["generation_status"] = {
                        "state": "degraded",
                        "source": generation.get("source", "ai"),
                        "reasons": list(
                            dict.fromkeys(
                                generation.get("reasons", []) + ["route_refresh_unavailable"]
                            )
                        ),
                    }
                from app.services.knowledge_provenance_service import KnowledgeProvenanceService

                enriched_itinerary = KnowledgeProvenanceService(
                    self.db
                ).attach_facts_to_itinerary(enriched_itinerary, trip.country_code)
                validate_itinerary_quality(enriched_itinerary, trip.country_code)

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
