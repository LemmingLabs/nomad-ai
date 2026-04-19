from datetime import datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.places import (
    AccommodationDB,
    AccommodationFilter,
    PlaceDB,
    PlaceRefreshResult,
)


def test_place_db_validates_correctly_with_all_fields() -> None:
    place = PlaceDB.model_validate(
        SimpleNamespace(
            id=1,
            twogis_id="70000001031668425",
            name="Ala-Too Square",
            category="attraction",
            city="Bishkek",
            address="Chuy Ave",
            lat=42.8765,
            lon=74.6065,
            rating=4.7,
            review_count=1280,
            last_refreshed=datetime(2026, 4, 19, 12, 0, 0),
        )
    )

    assert place.id == 1
    assert place.twogis_id == "70000001031668425"
    assert place.name == "Ala-Too Square"
    assert place.category == "attraction"
    assert place.city == "Bishkek"
    assert place.address == "Chuy Ave"
    assert place.lat == 42.8765
    assert place.lon == 74.6065
    assert place.rating == 4.7
    assert place.review_count == 1280
    assert place.last_refreshed == datetime(2026, 4, 19, 12, 0, 0)


def test_accommodation_db_allows_none_for_twogis_id_and_coordinates() -> None:
    accommodation = AccommodationDB(
        id=10,
        twogis_id=None,
        name="Nomad Hostel",
        city="Karakol",
        accommodation_type="hostel",
        price_per_night_usd=25.0,
        address=None,
        lat=None,
        lon=None,
        rating=None,
        review_count=None,
        last_refreshed=None,
    )

    assert accommodation.twogis_id is None
    assert accommodation.lat is None
    assert accommodation.lon is None


def test_accommodation_db_rejects_invalid_accommodation_type() -> None:
    with pytest.raises(ValidationError):
        AccommodationDB(
            id=11,
            twogis_id="70000001099999999",
            name="Nomad Stay",
            city="Bishkek",
            accommodation_type="luxury",
            price_per_night_usd=80.0,
        )


def test_place_refresh_result_defaults_errors_to_empty_list() -> None:
    result = PlaceRefreshResult(
        places_upserted=4,
        accommodations_upserted=2,
        refreshed_at=datetime(2026, 4, 19, 12, 30, 0),
    )

    assert result.errors == []


def test_accommodation_filter_defaults_type_to_hostel() -> None:
    filters = AccommodationFilter(city="Bishkek")

    assert filters.accommodation_type == "hostel"
    assert filters.max_price_usd is None
