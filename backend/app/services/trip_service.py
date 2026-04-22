import logging
from collections import Counter

from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.repositories.trip_repository import (
    create_trip,
    get_trip_by_id,
    get_user_trips,
    assign_trip_to_user,
)
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService
from app.services.place_candidate_service import get_place_candidate_service


logger = logging.getLogger(__name__)


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
            title = f"Arrival and Exploration in Bishkek" if day == 1 else f"Exploring Bishkek"
        elif city == "Karakol":
            location = "Karakol Town" if day == 3 else "Mountain Area"
            title = f"Journey to Karakol" if day == 3 else f"Mountain Adventure in Karakol"
        else:
            location = "Cholpon-Ata Lakefront" if day == 5 else "Issyk-Kul Shore"
            title = f"Arrival at Issyk-Kul Lake" if day == 5 else f"Relaxing by the Lake"

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


def normalize_generated_itinerary(itinerary: dict, title: str | None, days: int, travel_style: str) -> tuple[dict, str]:
    """Post-process generated itinerary to ensure concrete locations, activities, and metadata."""
    if not isinstance(itinerary, dict):
        return itinerary, title or f"{days}-Day Trip"

    valid_types = {"sightseeing", "activity", "meal"}
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

                vague_locations = [
                    "city center", "downtown", "old town", "local area", 
                    "nature spot", "mountain area", "mountains", "center", 
                    "city", "town center", "city exploration",
                    "area", "region", "zone", "district"
                ]
                loc_val = str(day.get("location", "")).lower().strip()

                is_vague = any(v in loc_val for v in vague_locations)

                if is_vague or not loc_val:
                    mapped_loc = day.get("location", "Unknown Location")
                    city_lower = city_val.lower()
                    if city_lower == "bishkek":
                        mapped_loc = "Ala-Too Square"
                    elif city_lower == "karakol":
                        mapped_loc = "Dungan Mosque"
                    elif city_lower == "cholpon-ata":
                        mapped_loc = "Rukh Ordo Cultural Center"
                    elif city_lower == "osh":
                        mapped_loc = "Osh Bazaar"
                    
                    day["location"] = mapped_loc

                if not day.get("routing_location"):
                    mapped = day.get("location", "")
                    if city_val.lower() not in mapped.lower():
                        mapped = f"{mapped} {city_val}"
                    day["routing_location"] = mapped

    generic_titles = [
        "scenic kyrgyzstan getaway", "discover kyrgyzstan", 
        "trip to kyrgyzstan", "kyrgyzstan trip", "kyrgyzstan adventure", 
        "explore kyrgyzstan"
    ]
    final_title = title or ""
    if not final_title or str(final_title).lower().strip() in generic_titles:
        final_title = f"{days}-Day {travel_style.title()} Trip in Kyrgyzstan"

    generic_summaries = [
        "discover the beauty of kyrgyzstan", "an unforgettable journey", 
        "a scenic trip", "explore the best of", "amazing trip", "enjoy a trip",
        "beautiful trip"
    ]
    summary = str(itinerary.get("summary", "")).strip()
    is_generic_summary = any(g in summary.lower() for g in generic_summaries)

    if not summary or is_generic_summary or len(summary) < 20 or len(str(summary).split()) < 5:
        cities_str = " and ".join(seen_cities[:2]) if seen_cities else "Kyrgyzstan"
        itinerary["summary"] = f"A {days}-day {travel_style.lower()} trip through {cities_str} with nature, local food, and cultural highlights."

    return itinerary, final_title


def _normalize_city_name(city_raw: str) -> str:
    """Map nearby destinations to the closest supported city for downstream services."""
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
            city = "Bishkek"
            day["city"] = city

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
        )
        if not candidates:
            logger.info(
                "No Google Places candidates for day=%s city=%s interest=%s",
                day.get("day") or index + 1,
                city,
                interest,
            )
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
        else:
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
) -> Trip:
    """Create a new trip with a generated mock itinerary."""
    if days < 1:
        raise ValueError("Days must be at least 1")
    normalized_budget = budget.strip().lower()
    if not normalized_budget:
        raise ValueError("Budget cannot be empty")
    normalized_travel_style = travel_style.strip().lower()
    if not normalized_travel_style:
        raise ValueError("Travel style cannot be empty")
    normalized_interests = [item.strip() for item in interests if item.strip()]
    normalized_prompt = prompt.strip() if prompt else None

    ai_service = AIService()
    title = None
    itinerary = None
    
    try:
        ai_result = ai_service.generate_initial_trip(
            budget=normalized_budget,
            days=days,
            interests=normalized_interests,
            travel_style=normalized_travel_style,
            prompt=normalized_prompt,
        )
        if isinstance(ai_result, dict):
            title = ai_result.get("title")
            candidate_itinerary = ai_result.get("itinerary")
            if isinstance(candidate_itinerary, dict) and "days" in candidate_itinerary:
                itinerary = candidate_itinerary
    except Exception as exc:
        print(f"AI initial generation failed: {exc}")

    if not itinerary:
        itinerary = build_mock_itinerary(days, normalized_interests, normalized_travel_style)

    if not title:
        title = f"{days}-day {normalized_travel_style} trip"

    itinerary, title = normalize_generated_itinerary(itinerary, title, days, normalized_travel_style)

    if "days" in itinerary and isinstance(itinerary["days"], list):
        for day in itinerary["days"]:
            if isinstance(day, dict):
                day["city"] = _normalize_city_name(day.get("city", ""))

    try:
        itinerary = enrich_itinerary_with_place_candidates(
            itinerary,
            normalized_interests,
            normalized_travel_style,
            normalized_prompt,
        )
    except Exception as exc:
        print(f"Place candidate enrichment failed: {exc}")

    catalog_service = CatalogService(db)
    enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(itinerary, normalized_budget)

    from app.utils.async_runner import run_async
    from app.services.routing_service import RoutingService
    try:
        enriched_itinerary = run_async(RoutingService().enrich_from_itinerary_json(enriched_itinerary))
    except Exception as exc:
        print(f"Routing enrichment failed: {exc}")

    from app.services.image_enrichment_service import ImageEnrichmentService
    try:
        enriched_itinerary = ImageEnrichmentService().enrich_trip_with_images(enriched_itinerary)
    except Exception as exc:
        print(f"Image enrichment failed: {exc}")

    cleaned_itinerary = enriched_itinerary

    trip_data = {
        "user_id": user_id,
        "title": title,
        "budget": normalized_budget,
        "days": days,
        "interests": normalized_interests,
        "travel_style": normalized_travel_style,
        "itinerary_json": cleaned_itinerary,
    }

    return create_trip(db, **trip_data)


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
