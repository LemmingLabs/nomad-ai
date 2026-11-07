from app.services.itinerary_quality_service import validate_itinerary_quality
from app.schemas.itinerary import TripItineraryResponse
import pytest


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
        "activities_missing",
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


def test_duration_longer_than_window_is_flagged_without_treating_unknown_as_conflict():
    itinerary = {"days": [{"day": 1, "city": "Bishkek", "location": "Center", "activities": [
        {"time_window": "09:00-10:00", "duration_minutes": 90},
        {"time_window": "11:00-12:00", "duration_minutes": None},
    ]}]}
    codes = {warning["code"] for warning in validate_itinerary_quality(itinerary, "KG")}
    assert "activity_duration_exceeds_window" in codes
    assert "activity_duration_unknown" in codes


@pytest.mark.parametrize(
    ("duration", "status", "window", "expected"),
    [
        (181, "available", "09:00-20:00", True),
        (180, "available", "09:00-20:00", False),
        (181, "stale", "09:00-20:00", False),
        (181, "available", None, False),
        (181, "available", "invalid", False),
    ],
)
def test_transfer_check_requires_complete_current_data(duration, status, window, expected):
    itinerary = {"days": [
        {"day": 1, "city": "Bishkek", "location": "Center", "activities": []},
        {"day": 2, "city": "Karakol", "location": "Lake", "activities": [
            {"time_window": window, "duration_minutes": 60},
        ], "route_from_previous": {"status": status, "distance_km": 100, "duration_mins": duration}},
    ]}
    warnings = validate_itinerary_quality(itinerary, "KG")
    matches = [warning for warning in warnings if warning["code"] == "transfer_time_unscheduled"]
    assert bool(matches) is expected
    if matches:
        assert matches[0]["day"] == 2


def test_scheduled_transfer_is_not_counted_twice():
    itinerary = {"days": [
        {"city": "Bishkek", "location": "Center", "activities": []},
        {"city": "Karakol", "location": "Lake", "activities": [
            {"type": "transfer", "time_window": "09:00-20:00", "duration_minutes": 660},
        ], "route_from_previous": {"status": "available", "distance_km": 100, "duration_mins": 181}},
    ]}
    assert "transfer_time_unscheduled" not in {
        warning["code"] for warning in validate_itinerary_quality(itinerary, "KG")
    }


def test_optional_alternative_is_not_counted_as_part_of_the_schedule():
    itinerary = {"days": [{"day": 1, "city": "Bishkek", "location": "Center", "activities": [
        {"type": "activity", "time_window": "09:00-17:00", "duration_minutes": 480},
        {"type": "alternative", "time_window": "09:00-17:00", "duration_minutes": 480},
    ]}]}
    assert validate_itinerary_quality(itinerary, "KG") == []


def test_empty_or_alternative_only_day_is_open_and_legacy_string_has_unknown_duration():
    itinerary = {"days": [
        {"day": 1, "city": "Bishkek", "location": "Center", "activities": []},
        {"day": 2, "city": "Bishkek", "location": "Center", "activities": [{"type": "alternative"}]},
        {"day": 3, "city": "Bishkek", "location": "Center", "activities": ["Visit the market"]},
    ]}
    warnings = validate_itinerary_quality(itinerary, "KG")
    assert [w["day"] for w in warnings if w["code"] == "activities_missing"] == [1, 2]
    assert [w["day"] for w in warnings if w["code"] == "activity_duration_unknown"] == [3]


def test_scheduled_transfer_is_not_added_twice_to_daily_total():
    itinerary = {"days": [
        {"day": 1, "city": "Bishkek", "location": "Center", "activities": []},
        {"day": 2, "city": "Karakol", "location": "Lake", "activities": [
            {"type": "transfer", "duration_minutes": 420},
            {"type": "activity", "duration_minutes": 300},
        ], "route_from_previous": {"status": "available", "distance_km": 100, "duration_mins": 420}},
    ]}
    assert "travel_day_overloaded" not in {
        warning["code"] for warning in validate_itinerary_quality(itinerary, "KG")
    }
