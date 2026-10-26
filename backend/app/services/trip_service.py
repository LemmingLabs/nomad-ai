import logging
from collections import Counter

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.trip import Trip
from app.repositories.trip_repository import (
    create_trip,
    get_trip_by_id,
    get_user_trips,
    assign_trip_to_user,
)
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService
from app.core.destination_registry import (
    DEFAULT_COUNTRY_CODE,
    DEFAULT_DESTINATION_ID,
    resolve_destination,
)
from app.services.limit_service import LimitService
from app.services.place_candidate_service import get_place_candidate_service
from app.services.usage_service import UsageService
from app.services.itinerary_quality_service import validate_itinerary_quality


logger = logging.getLogger(__name__)


def _build_initial_user_message(
    *,
    prompt: str | None,
    days: int,
    budget: str,
    interests: list[str],
    travel_style: str,
    destination_name: str = "Kyrgyzstan",
) -> str:
    prompt_text = (prompt or "").strip()
    if prompt_text:
        return prompt_text

    interests_text = ", ".join([item for item in interests if item]) if interests else ""
    base = f"Plan me a {days}-day {travel_style.strip()} trip in {destination_name} with {budget.strip()} budget."
    if interests_text:
        return f"{base} Interests: {interests_text}."
    return base


def _build_initial_assistant_message(
    *,
    assistant_text: str | None,
    title: str,
    itinerary_json: dict,
    days: int,
    travel_style: str,
) -> str:
    generation_status = (itinerary_json or {}).get("generation_status") or {}
    if generation_status.get("state") == "degraded":
        return (
            "Some planning services did not complete. I saved a clearly marked draft so you can review it; "
            "its timing or route details may be incomplete."
        )

    text = (assistant_text or "").strip()
    if text:
        return text

    summary = str((itinerary_json or {}).get("summary") or "").strip()
    trip_days = (itinerary_json or {}).get("days")
    cities: list[str] = []
    highlights: list[str] = []
    if isinstance(trip_days, list):
        for day in trip_days:
            if not isinstance(day, dict):
                continue
            city = str(day.get("city") or "").strip()
            if city and city not in cities:
                cities.append(city)
            location = str(day.get("location") or "").strip()
            if location and len(highlights) < 3:
                highlights.append(location)

    cities_text = ""
    if cities:
        cities_text = " through " + " and ".join(cities[:2])

    highlights_text = ""
    if highlights:
        highlights_text = f" Highlights: {', '.join(highlights)}."

    if summary:
        return (
            f'I created a {days}-day {travel_style.strip()} trip{cities_text} titled "{title}". '
            f"{summary}{highlights_text}"
        ).strip()

    return (
        f'I created a {days}-day {travel_style.strip()} trip{cities_text} titled "{title}".'
        f"{highlights_text}"
    ).strip()


def build_mock_itinerary(days: int, interests: list[str], travel_style: str) -> dict:
    """Generate a mock itinerary for development purposes."""
    interest_focus = ", ".join(interests[:2]) if interests else "local highlights"
    summary = f"{days}-day {travel_style} trip focusing on {interest_focus}"

    days_plan = []
    for day in range(1, days + 1):
        if days <= 2:
            city = "Bishkek"
        elif days <= 4:
            city = "Bishkek" if day <= 2 else "Karakol"
        else:
            if day <= 2:
                city = "Bishkek"
            elif day <= 4:
                city = "Karakol"
            else:
                city = "Cholpon-Ata"

        if city == "Bishkek":
            location = "Ala-Too Square" if day == 1 else "Bishkek City Center"
            title = "Arrival and Exploration in Bishkek" if day == 1 else "Exploring Bishkek"
        elif city == "Karakol":
            location = "Karakol Town" if day == 3 else "Mountain Area"
            title = "Journey to Karakol" if day == 3 else "Mountain Adventure in Karakol"
        else:
            location = "Cholpon-Ata Lakefront" if day == 5 else "Issyk-Kul Shore"
            title = "Arrival at Issyk-Kul Lake" if day == 5 else "Relaxing by the Lake"

        day_interest = interests[(day - 1) % len(interests)] if interests else ""

        if "nature" in day_interest or "mountains" in day_interest:
            morning_desc = f"Hike and enjoy the nature near {location}"
            afternoon_desc = f"Outdoor {travel_style} activity in the area"
            evening_desc = "Relax and enjoy the view"
        elif "food" in day_interest:
            morning_desc = "Visit local markets and taste morning treats"
            afternoon_desc = f"Local culinary {travel_style} experience"
            evening_desc = "Dinner at top-rated traditional restaurant"
        else:
            morning_desc = f"Morning sightseeing around {location}"
            afternoon_desc = f"Enjoy a {travel_style} experience"
            evening_desc = "Dinner and rest"

        activities = [
            {"time": "Morning", "description": morning_desc, "type": "sightseeing"},
            {"time": "Afternoon", "description": afternoon_desc, "type": "activity"},
            {"time": "Evening", "description": evening_desc, "type": "meal"},
        ]

        days_plan.append({
            "day": day,
            "title": title,
            "city": city,
            "location": location,
            "activities": activities,
        })

    return {
        "summary": summary,
        "days": days_plan,
        "total_days": days,
        "interests": interests,
        "travel_style": travel_style,
    }


def normalize_generated_itinerary(
    itinerary: dict,
    title: str | None,
    days: int,
    travel_style: str,
    country_name: str = "Kyrgyzstan",
) -> tuple[dict, str]:
    """Normalize itinerary metadata without inventing replacement locations."""
    if not isinstance(itinerary, dict):
        return itinerary, title or f"{days}-Day Trip"

    for metadata_key in ("generation_status", "quality_warnings", "route_status"):
        itinerary.pop(metadata_key, None)

    valid_types = {"sightseeing", "activity", "meal", "transfer", "rest", "alternative"}
    days_list = itinerary.get("days", [])
    seen_cities = []

    if isinstance(days_list, list):
        for day in days_list:
            if isinstance(day, dict):
                city_val = str(day.get("city", "")).strip()
                if city_val and city_val not in seen_cities:
                    seen_cities.append(city_val)

                activities = day.get("activities", [])
                if isinstance(activities, list):
                    for act in activities:
                        if isinstance(act, dict):
                            act_type = str(act.get("type", "")).lower().strip()
                            if act_type not in valid_types:
                                act["type"] = "activity"
                            duration = act.get("duration_minutes")
                            if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
                                act["duration_minutes"] = None
                                act["duration_status"] = "unknown"
                            else:
                                act["duration_status"] = "estimated"
                            if not isinstance(act.get("time_window"), str):
                                act["time_window"] = None
                            practical_details = act.get("practical_details")
                            act["practical_details"] = (
                                [str(detail) for detail in practical_details if detail]
                                if isinstance(practical_details, list)
                                else []
                            )
                            act.setdefault("content_status", "ai_suggestion")

                vague_locations = [
                    "city center", "downtown", "old town", "local area", 
                    "nature spot", "mountain area", "mountains", "center", 
                    "city", "town center", "city exploration",
                    "area", "region", "zone", "district"
                ]
                loc_val = str(day.get("location", "")).lower().strip()

                is_vague = any(v in loc_val for v in vague_locations)

                if is_vague or not loc_val:
                    day["location"] = day.get("location") or "Unknown Location"

                if not day.get("routing_location"):
                    routing_location = day.get("location", "")
                    if city_val and city_val.lower() not in routing_location.lower():
                        routing_location = f"{routing_location} {city_val}".strip()
                    day["routing_location"] = routing_location

    generic_titles = [
        f"scenic {country_name.lower()} getaway", f"discover {country_name.lower()}",
        f"trip to {country_name.lower()}", f"{country_name.lower()} trip",
        f"{country_name.lower()} adventure", f"explore {country_name.lower()}"
    ]
    final_title = title or ""
    if not final_title or str(final_title).lower().strip() in generic_titles:
        final_title = f"{days}-Day {travel_style.title()} Trip in {country_name}"

    generic_summaries = [
        f"discover the beauty of {country_name.lower()}", "an unforgettable journey",
        "a scenic trip", "explore the best of", "amazing trip", "enjoy a trip",
        "beautiful trip"
    ]
    summary = str(itinerary.get("summary", "")).strip()
    is_generic_summary = any(g in summary.lower() for g in generic_summaries)

    if not summary or is_generic_summary or len(summary) < 20 or len(str(summary).split()) < 5:
        cities_str = " and ".join(seen_cities[:2]) if seen_cities else country_name
        itinerary["summary"] = f"A {days}-day {travel_style.lower()} trip through {cities_str} with nature, local food, and cultural highlights."

    return itinerary, final_title


def _normalize_city_name(city_raw: str, country_code: str = DEFAULT_COUNTRY_CODE) -> str:
    """Map nearby destinations to the closest supported city for downstream services."""
    if country_code.strip().upper() != "KG":
        return city_raw
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
        "tash-rabat": "Naryn",
    }
    city_lower = str(city_raw or "").strip().lower()
    return mapping.get(city_lower, city_raw)


def _day_interest(day: dict, day_index: int, interests: list[str]) -> str:
    text_parts = [
        str(day.get("title", "")),
        str(day.get("location", "")),
    ]
    activities = day.get("activities", [])
    if isinstance(activities, list):
        text_parts.extend(
            str(activity.get("description", ""))
            for activity in activities
            if isinstance(activity, dict)
        )
    text = " ".join(text_parts).lower()

    keyword_mapping = {
        "mountains": ["mountain", "hike", "hiking", "gorge", "alpine", "viewpoint"],
        "nature": ["nature", "park", "lake", "outdoor", "scenic", "valley"],
        "food": ["food", "restaurant", "cafe", "market", "cuisine", "dinner"],
        "culture": ["culture", "museum", "heritage", "historic", "mosque", "church"],
    }
    for interest, keywords in keyword_mapping.items():
        if any(keyword in text for keyword in keywords):
            return interest

    if interests:
        return interests[day_index % len(interests)]
    return "culture"


def _build_routing_location(day: dict, selected: dict, city: str) -> str:
    place_name = str(selected.get("name") or "").strip()
    formatted_address = str(selected.get("formatted_address") or "").strip()
    city_name = str(city or "").strip()

    parts = []
    if place_name:
        parts.append(place_name)
    if formatted_address and formatted_address.lower() != place_name.lower():
        parts.append(formatted_address)
    elif city_name and city_name.lower() not in place_name.lower():
        parts.append(city_name)

    if parts:
        return ", ".join(dict.fromkeys(parts))

    fallback_location = str(day.get("location") or "").strip()
    if fallback_location and city_name and city_name.lower() not in fallback_location.lower():
        return f"{fallback_location}, {city_name}"
    return fallback_location or city_name


def _ensure_day_routing_location(day: dict) -> None:
    if day.get("routing_location"):
        return

    city = str(day.get("city") or "").strip()
    location = str(day.get("location") or "").strip()
    if location and city and city.lower() not in location.lower():
        day["routing_location"] = f"{location}, {city}"
    else:
        day["routing_location"] = location or city


def enrich_itinerary_with_place_candidates(
    itinerary: dict,
    interests: list[str],
    travel_style: str,
    prompt: str | None = None,
    country_code: str = DEFAULT_COUNTRY_CODE,
    country_name: str = "Kyrgyzstan",
) -> dict:
    """Replace AI-invented day locations with real Google Places candidates."""
    if not isinstance(itinerary, dict) or not isinstance(itinerary.get("days"), list):
        return itinerary

    place_candidate_service = get_place_candidate_service()
    used_place_ids: set[str] = set()
    used_place_names: set[str] = set()
    selected_type_counts: Counter = Counter()
    selected_interest_counts: Counter = Counter()
    previous_interest: str | None = None
    previous_location: dict | None = None

    for index, day in enumerate(itinerary["days"]):
        if not isinstance(day, dict):
            continue

        city = str(day.get("city") or "").strip()
        if not city:
            if country_code.upper() == "KG":
                city = "Bishkek"
                day["city"] = city
            else:
                day["place_resolution"] = {
                    "status": "unresolved",
                    "provider": "google_places",
                    "country_code": country_code.upper(),
                }
                continue

        interest = _day_interest(day, index, interests)
        candidates = place_candidate_service.get_candidates_for_day(
            city=city,
            interests=[interest],
            travel_style=travel_style,
            user_prompt=prompt,
            limit=8,
            exclude_place_ids=used_place_ids,
            exclude_names=used_place_names,
            selected_type_counts=selected_type_counts,
            selected_interest_counts=selected_interest_counts,
            previous_interest=previous_interest,
            previous_location=previous_location,
            country_code=country_code,
            country_name=country_name,
        )
        if not candidates:
            logger.info(
                "No Google Places candidates for day=%s city=%s interest=%s",
                day.get("day") or index + 1,
                city,
                interest,
            )
            day.pop("place_candidate", None)
            day["place_resolution"] = {
                "status": "unresolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
            _ensure_day_routing_location(day)
            previous_interest = interest
            continue

        selected = candidates[0]
        if len(candidates) > 3:
            selected = (
                place_candidate_service.select_best_candidate_with_ai(
                    candidates=candidates,
                    city=city,
                    interests=[interest],
                    travel_style=travel_style,
                    user_prompt=prompt,
                )
                or candidates[0]
            )

        place_id = selected.get("place_id")
        if place_id:
            used_place_ids.add(place_id)
        place_name = selected.get("name")
        if place_name:
            used_place_names.add(" ".join(str(place_name).strip().lower().split()))

        primary_type = next(
            (
                place_type
                for place_type in selected.get("types", [])
                if place_type not in {"establishment", "point_of_interest"}
            ),
            None,
        )
        if primary_type:
            selected_type_counts[primary_type] += 1
        selected_interest_counts[interest] += 1

        if place_name:
            day["location"] = place_name
            day["routing_location"] = _build_routing_location(day, selected, city)
            day["place_candidate"] = selected
            day["place_resolution"] = {
                "status": "resolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
        else:
            day["place_resolution"] = {
                "status": "unresolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
            _ensure_day_routing_location(day)

        if selected.get("lat") is not None and selected.get("lng") is not None:
            previous_location = {
                "lat": selected.get("lat"),
                "lng": selected.get("lng"),
            }
        previous_interest = interest

    return itinerary


def enrich_selected_days_with_place_candidates(
    itinerary: dict,
    changed_day_indexes: set[int],
    interests: list[str],
    travel_style: str,
    prompt: str | None = None,
    country_code: str = DEFAULT_COUNTRY_CODE,
    country_name: str = "Kyrgyzstan",
) -> dict:
    """Re-enrich only selected days with Google Places candidates."""
    if not changed_day_indexes:
        return itinerary
    if not isinstance(itinerary, dict) or not isinstance(itinerary.get("days"), list):
        return itinerary

    place_candidate_service = get_place_candidate_service()

    used_place_ids: set[str] = set()
    used_place_names: set[str] = set()
    selected_type_counts: Counter = Counter()
    selected_interest_counts: Counter = Counter()

    days: list = itinerary["days"]

    for idx, day in enumerate(days):
        if idx in changed_day_indexes or not isinstance(day, dict):
            continue

        candidate = day.get("place_candidate")
        if isinstance(candidate, dict):
            place_id = candidate.get("place_id")
            if place_id:
                used_place_ids.add(place_id)

            place_name = candidate.get("name")
            if place_name:
                used_place_names.add(" ".join(str(place_name).strip().lower().split()))

            primary_type = next(
                (
                    place_type
                    for place_type in candidate.get("types", [])
                    if place_type not in {"establishment", "point_of_interest"}
                ),
                None,
            )
            if primary_type:
                selected_type_counts[primary_type] += 1

        interest = _day_interest(day, idx, interests)
        selected_interest_counts[interest] += 1

    previous_interest: str | None = None
    previous_location: dict | None = None

    for index, day in enumerate(days):
        if not isinstance(day, dict):
            continue

        city = str(day.get("city") or "").strip()
        if not city:
            if country_code.upper() == "KG":
                city = "Bishkek"
                day["city"] = city
            else:
                day.pop("place_candidate", None)
                day["place_resolution"] = {
                    "status": "unresolved",
                    "provider": "google_places",
                    "country_code": country_code.upper(),
                }
                continue

        interest = _day_interest(day, index, interests)

        if index not in changed_day_indexes:
            candidate = day.get("place_candidate")
            if isinstance(candidate, dict):
                if candidate.get("lat") is not None and candidate.get("lng") is not None:
                    previous_location = {
                        "lat": candidate.get("lat"),
                        "lng": candidate.get("lng"),
                    }
            _ensure_day_routing_location(day)
            previous_interest = interest
            continue

        candidates = place_candidate_service.get_candidates_for_day(
            city=city,
            interests=[interest],
            travel_style=travel_style,
            user_prompt=prompt,
            limit=8,
            exclude_place_ids=used_place_ids,
            exclude_names=used_place_names,
            selected_type_counts=selected_type_counts,
            selected_interest_counts=selected_interest_counts,
            previous_interest=previous_interest,
            previous_location=previous_location,
            country_code=country_code,
            country_name=country_name,
        )

        if not candidates:
            logger.info(
                "No Google Places candidates for day=%s city=%s interest=%s (selective)",
                day.get("day") or index + 1,
                city,
                interest,
            )
            day.pop("place_candidate", None)
            day["place_resolution"] = {
                "status": "unresolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
            _ensure_day_routing_location(day)
            previous_interest = interest
            continue

        selected = candidates[0]
        if len(candidates) > 3:
            selected = (
                place_candidate_service.select_best_candidate_with_ai(
                    candidates=candidates,
                    city=city,
                    interests=[interest],
                    travel_style=travel_style,
                    user_prompt=prompt,
                )
                or candidates[0]
            )

        place_id = selected.get("place_id")
        if place_id:
            used_place_ids.add(place_id)
        place_name = selected.get("name")
        if place_name:
            used_place_names.add(" ".join(str(place_name).strip().lower().split()))

        primary_type = next(
            (
                place_type
                for place_type in selected.get("types", [])
                if place_type not in {"establishment", "point_of_interest"}
            ),
            None,
        )
        if primary_type:
            selected_type_counts[primary_type] += 1
        selected_interest_counts[interest] += 1

        if place_name:
            day["location"] = place_name
            day["routing_location"] = _build_routing_location(day, selected, city)
            day["place_candidate"] = selected
            day["place_resolution"] = {
                "status": "resolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
            logger.info(
                "[CONTINUE] re-enriched place candidate for day=%s",
                day.get("day") or index + 1,
            )
        else:
            day.pop("place_candidate", None)
            day["place_resolution"] = {
                "status": "unresolved",
                "provider": "google_places",
                "country_code": country_code.upper(),
            }
            _ensure_day_routing_location(day)

        if selected.get("lat") is not None and selected.get("lng") is not None:
            previous_location = {
                "lat": selected.get("lat"),
                "lng": selected.get("lng"),
            }
        previous_interest = interest

    return itinerary


def generate_trip(
    db: Session,
    user_id: int | None,
    budget: str,
    days: int,
    interests: list[str],
    travel_style: str,
    prompt: str | None = None,
    country_code: str = DEFAULT_COUNTRY_CODE,
    destination_id: str = DEFAULT_DESTINATION_ID,
) -> Trip:
    """Create a new trip with a generated mock itinerary."""
    if days < 1:
        raise ValueError("Days must be at least 1")
    if user_id is not None and not LimitService(db).can_generate_trip(user_id):
        raise HTTPException(
            status_code=403,
            detail="Daily limit exceeded. Upgrade your plan.",
        )
    normalized_budget = budget.strip().lower()
    if not normalized_budget:
        raise ValueError("Budget cannot be empty")
    normalized_travel_style = travel_style.strip().lower()
    if not normalized_travel_style:
        raise ValueError("Travel style cannot be empty")
    normalized_interests = [item.strip() for item in interests if item.strip()]
    normalized_prompt = prompt.strip() if prompt else None
    destination = resolve_destination(
        country_code=country_code,
        destination_id=destination_id,
    )

    ai_service = AIService()
    title = None
    itinerary = None
    assistant_text = None
    generation_status = {"state": "complete", "source": "ai", "reasons": []}
    generation_reasons: list[str] = []
    
    try:
        ai_result = ai_service.generate_initial_trip(
            budget=normalized_budget,
            days=days,
            interests=normalized_interests,
            travel_style=normalized_travel_style,
            prompt=normalized_prompt,
            country_code=destination.country_code,
            destination_id=destination.id,
        )
        if isinstance(ai_result, dict):
            provider_status = ai_result.get("_provider_status")
            if isinstance(provider_status, dict) and provider_status.get("source") == "mock":
                generation_status = {
                    "state": "degraded",
                    "source": "mock",
                    "reasons": [str(provider_status.get("reason") or "provider_unavailable")],
                }
            title = ai_result.get("title")
            candidate_itinerary = ai_result.get("itinerary")
            if isinstance(candidate_itinerary, dict) and "days" in candidate_itinerary:
                itinerary = candidate_itinerary
            candidate_message = (
                ai_result.get("message")
                or ai_result.get("assistant_message")
                or ai_result.get("content")
            )
            if isinstance(candidate_message, str) and candidate_message.strip():
                assistant_text = candidate_message.strip()
    except Exception as exc:
        print(f"AI initial generation failed: {exc}")
        generation_status = {
            "state": "degraded",
            "source": "mock",
            "reasons": ["ai_generation_failed"],
        }

    if not itinerary:
        itinerary = build_mock_itinerary(days, normalized_interests, normalized_travel_style)
        generation_status = {
            "state": "degraded",
            "source": "mock",
            "reasons": ["ai_generation_failed"],
        }

    if not title:
        title = f"{days}-day {normalized_travel_style} trip"

    itinerary, title = normalize_generated_itinerary(
        itinerary,
        title,
        days,
        normalized_travel_style,
        country_name=destination.country_name,
    )

    if "days" in itinerary and isinstance(itinerary["days"], list):
        for day in itinerary["days"]:
            if isinstance(day, dict):
                day["city"] = _normalize_city_name(
                    day.get("city", ""), country_code=destination.country_code
                )

    try:
        itinerary = enrich_itinerary_with_place_candidates(
            itinerary,
            normalized_interests,
            normalized_travel_style,
            normalized_prompt,
            country_code=destination.country_code,
            country_name=destination.country_name,
        )
    except Exception as exc:
        print(f"Place candidate enrichment failed: {exc}")
        generation_reasons.append("place_enrichment_unavailable")

    catalog_service = CatalogService(db)
    enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(
        itinerary,
        normalized_budget,
        country_code=destination.country_code,
    )

    from app.utils.async_runner import run_async
    from app.services.routing_service import RoutingService
    try:
        enriched_itinerary = run_async(
            RoutingService(
                country_code=destination.country_code,
                center_latitude=destination.center_latitude,
                center_longitude=destination.center_longitude,
            ).enrich_from_itinerary_json(
                enriched_itinerary
            )
        )
    except Exception as exc:
        print(f"Routing enrichment failed: {exc}")
        enriched_itinerary["route_status"] = "unavailable"
        generation_reasons.append("routing_unavailable")
    if enriched_itinerary.get("route_status") == "unavailable":
        generation_reasons.append("route_metrics_unavailable")

    from app.services.image_enrichment_service import ImageEnrichmentService
    try:
        enriched_itinerary = ImageEnrichmentService().enrich_trip_with_images(
            enriched_itinerary,
            country_name=destination.country_name,
            country_code=destination.country_code,
        )
    except Exception as exc:
        print(f"Image enrichment failed: {exc}")
        generation_reasons.append("image_enrichment_unavailable")

    from app.services.sponsored_injection_service import SponsoredInjectionService
    try:
        enriched_itinerary = SponsoredInjectionService(db).inject_sponsored_places(
            enriched_itinerary,
            trip_id=None,
            country_code=destination.country_code,
        )
    except Exception as exc:
        logger.exception("Sponsored injection failed: %s", exc)
        generation_reasons.append("sponsored_enrichment_unavailable")

    if generation_reasons:
        generation_status = {
            "state": "degraded",
            "source": generation_status["source"],
            "reasons": list(dict.fromkeys(generation_status["reasons"] + generation_reasons)),
        }
    enriched_itinerary["generation_status"] = generation_status
    content_status = (
        "mock_suggestion" if generation_status["source"] == "mock" else "ai_suggestion"
    )
    for day in enriched_itinerary.get("days", []):
        if not isinstance(day, dict):
            continue
        activities = day.get("activities")
        if not isinstance(activities, list):
            continue
        for activity in activities:
            if isinstance(activity, dict):
                activity["content_status"] = content_status
    validate_itinerary_quality(enriched_itinerary, destination.country_code)
    cleaned_itinerary = enriched_itinerary

    trip_data = {
        "user_id": user_id,
        "title": title,
        "budget": normalized_budget,
        "days": days,
        "interests": normalized_interests,
        "travel_style": normalized_travel_style,
        "country_code": destination.country_code,
        "destination_id": destination.id,
        "destination_name": destination.name,
        "itinerary_json": cleaned_itinerary,
    }
    trip = create_trip(db, **trip_data)

    try:
        from app.repositories.trip_message_repository import TripMessageRepository

        message_repo = TripMessageRepository(db)
        initial_user_message = _build_initial_user_message(
            prompt=prompt,
            days=days,
            budget=normalized_budget,
            interests=normalized_interests,
            travel_style=normalized_travel_style,
            destination_name=destination.name,
        )
        initial_assistant_message = _build_initial_assistant_message(
            assistant_text=assistant_text,
            title=title,
            itinerary_json=cleaned_itinerary,
            days=days,
            travel_style=normalized_travel_style,
        )

        message_repo.create_message(trip_id=trip.id, role="user", content=initial_user_message)
        message_repo.create_message(
            trip_id=trip.id,
            role="assistant",
            content=initial_assistant_message,
        )
    except Exception:
        logger.exception("Failed to create initial trip chat messages")

    if user_id is not None:
        UsageService(db).increment_trip_generation(user_id)

    db.commit()
    return trip


def list_user_trips(db: Session, user_id: int) -> list[dict]:
    """Get all trips for a specific user with previews."""
    trips = get_user_trips(db, user_id)
    
    from app.repositories.trip_message_repository import TripMessageRepository
    message_repo = TripMessageRepository(db)
    
    result = []
    for trip in trips:
        last_message = message_repo.get_last_trip_message(trip.id)
        
        last_message_preview = None
        if last_message:
            last_msg = getattr(last_message, "content", "")
            if len(last_msg) > 90:
                last_message_preview = last_msg[:87] + "..."
            else:
                last_message_preview = last_msg
                
        result.append({
            "id": trip.id,
            "title": trip.title,
            "days": trip.days,
            "country_code": trip.country_code,
            "destination_id": trip.destination_id,
            "destination_name": trip.destination_name,
            "created_at": trip.created_at,
            "updated_at": trip.updated_at,
            "last_message_preview": last_message_preview,
        })
    return result


def get_user_trip_by_id(db: Session, user_id: int, trip_id: int) -> Trip:
    """Get a specific trip by ID, ensuring it belongs to the user."""
    trip = get_trip_by_id(db, trip_id)
    if trip is None or trip.user_id != user_id:
        raise ValueError("Trip not found")
    return trip


def get_trip_detail(db: Session, user_id: int, trip_id: int) -> dict:
    """Get trip details including the first page of messages."""
    trip = get_user_trip_by_id(db, user_id, trip_id)
    
    from app.services.trip_message_service import TripMessageService
    message_service = TripMessageService(db)
    messages, total = message_service.get_trip_messages(trip=trip, limit=50, offset=0)
    
    return {
        "trip": trip,
        "messages": {
            "total": total,
            "limit": 50,
            "offset": 0,
            "items": messages,
        }
    }


def sync_guest_trip_to_user(db: Session, trip_id: int, user_id: int) -> Trip:
    """Assign a guest trip to a user account."""
    trip = get_trip_by_id(db, trip_id)
    if trip is None:
        raise ValueError("Trip not found")

    if trip.user_id == user_id:
        return trip

    if trip.user_id is None:
        return assign_trip_to_user(db, trip, user_id)

    raise ValueError("Trip not found")


def delete_user_trip(db: Session, user_id: int, trip_id: int) -> None:
    trip = get_trip_by_id(db, trip_id)
    if trip is None or trip.user_id != user_id:
        raise ValueError("Trip not found")
    
    from app.repositories.trip_repository import delete_trip
    delete_trip(db, trip)
