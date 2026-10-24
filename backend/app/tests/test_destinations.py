import pytest
from pydantic import ValidationError

from app.api.v1.destinations import get_destinations
from app.schemas.trip import TripGenerateRequest


def test_destination_catalog_lists_only_enabled_destinations():
    destinations = get_destinations()

    assert [destination.model_dump() for destination in destinations] == [{
        "id": "kg",
        "country_code": "KG",
        "country_name": "Kyrgyzstan",
        "name": "Kyrgyzstan",
        "enabled": True,
    }]


def test_legacy_trip_request_defaults_to_kyrgyzstan():
    request = TripGenerateRequest(
        budget="medium",
        days=3,
        interests=["nature"],
        travel_style="relaxed",
    )

    assert request.country_code == "KG"
    assert request.destination_id == "kg"


@pytest.mark.parametrize(
    "country_code,destination_id",
    [("FR", "fr"), ("FR", "kg"), ("KG", "unknown")],
)
def test_trip_request_rejects_unsupported_or_mismatched_destination(country_code, destination_id):
    with pytest.raises(ValidationError):
        TripGenerateRequest(
            budget="medium",
            days=3,
            interests=["nature"],
            travel_style="relaxed",
            country_code=country_code,
            destination_id=destination_id,
        )
