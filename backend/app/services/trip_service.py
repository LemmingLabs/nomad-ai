from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.repositories.trip_repository import (
    create_trip,
    get_trip_by_id,
    get_user_trips,
    assign_trip_to_user,
)


def build_mock_itinerary(days: int, interests: list[str], travel_style: str) -> dict:
    """Generate a mock itinerary for development purposes."""
    interest_focus = ", ".join(interests[:2]) if interests else "local highlights"
    summary = f"{days}-day {travel_style} trip focusing on {interest_focus}"

    days_plan = []
    for day in range(1, days + 1):
        if interests:
            day_interest = interests[(day - 1) % len(interests)]
            morning_activity = f"Explore {day_interest}"
        else:
            morning_activity = "Explore local area"

        activities = [
            {"time": "Morning", "description": morning_activity, "type": "sightseeing"},
            {"time": "Afternoon", "description": f"{travel_style.title()} experience", "type": "activity"},
            {"time": "Evening", "description": "Dinner and rest", "type": "meal"},
        ]

        days_plan.append({
            "day": day,
            "title": f"Day {day}: {interests[(day - 1) % len(interests)].title() if interests else 'Local Exploration'}",
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

    itinerary = build_mock_itinerary(days, normalized_interests, normalized_travel_style)
    title = f"{days}-day {normalized_travel_style} trip"

    trip_data = {
        "user_id": user_id,
        "title": title,
        "budget": normalized_budget,
        "days": days,
        "interests": normalized_interests,
        "travel_style": normalized_travel_style,
        "itinerary_json": itinerary,
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