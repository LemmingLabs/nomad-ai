from app.services.itinerary_quality_service import validate_itinerary_quality
from app.schemas.itinerary import TripItineraryResponse


def test_quality_warnings_flag_overlapping_schedule_and_unknown_durations():
    itinerary = {
        "days": [{
            "day": 1,
        "city": "Bishkek",
        "location": "Ala-Too Square",
            "activities": [
                {"time_window": "09:00-11:00", "duration_minutes": 120},
                {"time_window": "10:30-12:00", "duration_minutes": None},
            ],
        }]
    }

    warnings = validate_itinerary_quality(itinerary, "KG")

    assert {warning["code"] for warning in warnings} == {
        "overlapping_activity_times",
        "activity_duration_unknown",
    }


def test_quality_warnings_flag_missing_route_and_wrong_country_stop():
    itinerary = {
        "days": [
            {"day": 1, "city": "Bishkek", "location": "Ala-Too Square", "activities": []},
            {
                "day": 2,
                "city": "Osh",
                "location": "Osh Bazaar",
                "activities": [],
                "place_candidate": {"country_code": "KZ"},
            },
        ]
    }

    warnings = validate_itinerary_quality(itinerary, "KG")

    assert {warning["code"] for warning in warnings} == {
        "route_details_unavailable",
        "stop_outside_destination",
    }


def test_itinerary_response_keeps_legacy_activity_fields_optional():
    response = TripItineraryResponse.model_validate({
        "days": [{
            "day": 1,
            "title": "Old saved day",
            "city": "Bishkek",
            "location": "Ala-Too Square",
            "activities": [
                {"time": "Morning", "description": "Walk", "type": "activity"},
                "Visit the old bazaar",
            ],
            "place_candidate": {"name": "Ala-Too Square"},
        }]
    })

    activity = response.days[0].activities[0]
    assert activity.duration_minutes is None
    assert activity.time_window is None
    assert response.days[0].activities[1].description == "Visit the old bazaar"
    assert response.days[0].model_extra["place_candidate"] == {"name": "Ala-Too Square"}
