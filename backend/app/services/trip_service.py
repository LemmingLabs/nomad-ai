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


def generate_trip(
    db: Session,
    user_id: int | None,
    budget: str,
    days: int,
    interests: list[str],
    travel_style: str,
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

    ai_service = AIService()
    title = None
    itinerary = None
    
    try:
        ai_result = ai_service.generate_initial_trip(
            budget=normalized_budget,
            days=days,
            interests=normalized_interests,
            travel_style=normalized_travel_style,
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

    catalog_service = CatalogService(db)
    enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(itinerary, normalized_budget)

    trip_data = {
        "user_id": user_id,
        "title": title,
        "budget": normalized_budget,
        "days": days,
        "interests": normalized_interests,
        "travel_style": normalized_travel_style,
        "itinerary_json": enriched_itinerary,
    }

    return create_trip(db, **trip_data)


def list_user_trips(db: Session, user_id: int) -> list[Trip]:
    """Get all trips for a specific user."""
    return get_user_trips(db, user_id)


def get_user_trip_by_id(db: Session, user_id: int, trip_id: int) -> Trip:
    """Get a specific trip by ID, ensuring it belongs to the user."""
    trip = get_trip_by_id(db, trip_id)
    if trip is None or trip.user_id != user_id:
        raise ValueError("Trip not found")
    return trip


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