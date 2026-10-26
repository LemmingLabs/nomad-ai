import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.business import Business
from app.models.sponsored_place import SponsoredPlace
from app.models.sponsored_place_media import SponsoredPlaceMedia, SponsoredPlaceMediaType
from app.models.user import User
from app.services.sponsored_injection_service import DEFAULT_SPONSORED_IMAGE, SponsoredInjectionService
from app.services.sponsored_place_service import SponsoredPlaceService


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _create_sponsored_place(
    db_session,
    *,
    city: str = "Bishkek",
    category: str = "Modern Canteen / Cafe",
    region: str | None = None,
) -> SponsoredPlace:
    user = User(email="biz@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()

    business = Business(
        owner_id=user.id,
        name="Cantin",
        description="Modern city canteen",
        contact_phone="+996555000111",
        website_url="https://cantin.example.com",
    )
    db_session.add(business)
    db_session.flush()

    place = SponsoredPlace(
        business_id=business.id,
        title="Cantin",
        description="Modern stylish canteen in the city center",
        region=region,
        city=city,
        lat=42.8746,
        lng=74.5698,
        google_place_id=None,
        address="Bishkek center",
        category=category,
        cta_text="Book a table",
        contact_phone="+996555000111",
        website_url="https://cantin.example.com",
        is_approved=True,
        is_active=True,
    )
    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)
    return place


def test_inject_sponsored_place_from_food_semantics_even_without_meal_activity(db_session):
    place = _create_sponsored_place(db_session)
    itinerary = {
        "days": [
            {
                "day": 1,
                "city": "Bishkek, Kyrgyzstan",
                "title": "Stylish lunch stop in the city center",
                "location": "Bishkek city center shopping mall",
                "routing_location": "Bishkek city center shopping mall",
                "activities": [
                    {
                        "type": "activity",
                        "description": "Browse local spots and stop for lunch in a modern cafe.",
                    }
                ],
            }
        ]
    }

    result = SponsoredInjectionService(db_session).inject_sponsored_places(itinerary, trip_id=77)

    sponsored = result["days"][0].get("sponsored")
    assert sponsored is not None
    assert sponsored["is_sponsored"] is True
    assert sponsored["badge"] == "Partner Pick"
    assert sponsored["place"]["id"] == place.id
    assert sponsored["place"]["category"] == "Modern Canteen / Cafe"


def test_city_matching_handles_city_center_variants(db_session):
    place = _create_sponsored_place(db_session, city="Bishkek")
    service = SponsoredInjectionService(db_session)

    assert service._city_matches(service._normalize_city("Bishkek city center"), place.city) is True
    assert service._city_matches(service._normalize_city("Bishkek, Kyrgyzstan"), place.city) is True


def test_sponsored_injection_matches_country_before_same_named_city(db_session):
    kg_place = _create_sponsored_place(db_session, city="Springfield")
    other_country_place = SponsoredPlace(
        business_id=kg_place.business_id,
        title="Different market",
        description="Same city name in another country",
        country_code="US",
        region="Illinois",
        city="Springfield",
        lat=39.8,
        lng=-89.6,
        address="Springfield, US",
        category="restaurant",
        is_approved=True,
        is_active=True,
    )
    db_session.add(other_country_place)
    db_session.commit()

    itinerary = {
        "days": [{
            "day": 1,
            "city": "Springfield",
            "activities": [{"type": "meal", "description": "Lunch"}],
        }]
    }

    result = SponsoredInjectionService(db_session).inject_sponsored_places(
        itinerary, country_code="KG"
    )

    assert result["days"][0]["sponsored"]["place"]["id"] == kg_place.id


def test_sponsored_injection_rejects_same_city_in_different_region(db_session):
    _create_sponsored_place(db_session, city="Springfield", region="Illinois")
    service = SponsoredInjectionService(db_session)

    candidate = service._pick_best_candidate(
        city="Springfield",
        region="Oregon",
        desired_categories={"restaurant"},
        coords=None,
        used_place_ids=set(),
        country_code="KG",
    )

    assert candidate is None


def test_sponsored_injection_uses_geographic_proximity_when_city_differs(db_session):
    place = _create_sponsored_place(db_session, city="Nearby town")
    service = SponsoredInjectionService(db_session)

    candidate = service._pick_best_candidate(
        city="Another town",
        desired_categories={"restaurant"},
        coords=service._extract_day_coords(
            {"place_candidate": {"lat": 42.875, "lng": 74.571}}
        ),
        used_place_ids=set(),
        country_code="KG",
    )

    assert candidate.id == place.id


def test_sponsored_place_rejects_coordinates_from_another_country(monkeypatch):
    monkeypatch.setattr(
        "app.services.sponsored_place_service.GoogleMapsClient.reverse_geocode_country",
        lambda self, lat, lng: "US",
    )
    service = SponsoredPlaceService(db=object())

    with pytest.raises(HTTPException) as error:
        service._validate_country_location("KG", 39.8, -89.6)

    assert error.value.status_code == 422


def test_category_match_supports_canteen_and_cafe_aliases(db_session):
    service = SponsoredInjectionService(db_session)

    assert service._category_match_score("Modern Canteen / Cafe", {"restaurant"}) >= 2
    assert service._category_match_score("Food Court Cafe", {"restaurant"}) >= 2


def test_inject_sponsored_place_uses_only_place_media(db_session):
    place = _create_sponsored_place(db_session)
    db_session.add(
        SponsoredPlaceMedia(
            sponsored_place_id=place.id,
            type=SponsoredPlaceMediaType.IMAGE,
            url=f"/media/businesses/{place.business_id}/sponsored_places/{place.id}/photo.jpg",
            filename="photo.jpg",
            content_type="image/jpeg",
        )
    )
    db_session.commit()

    itinerary = {
        "days": [
            {
                "day": 1,
                "city": "Bishkek",
                "title": "Lunch",
                "activities": [{"type": "meal", "description": "Lunch stop"}],
            }
        ]
    }

    result = SponsoredInjectionService(db_session).inject_sponsored_places(itinerary)

    assert result["days"][0]["sponsored"]["place"]["images"] == [
        f"/media/businesses/{place.business_id}/sponsored_places/{place.id}/photo.jpg"
    ]


def test_inject_sponsored_place_uses_fallback_image_when_media_missing(db_session):
    _create_sponsored_place(db_session)
    itinerary = {
        "days": [
            {
                "day": 1,
                "city": "Bishkek",
                "title": "Lunch",
                "activities": [{"type": "meal", "description": "Lunch stop"}],
            }
        ]
    }

    result = SponsoredInjectionService(db_session).inject_sponsored_places(itinerary)

    assert result["days"][0]["sponsored"]["place"]["images"] == [DEFAULT_SPONSORED_IMAGE]


def test_sponsored_place_service_normalizes_city_and_category_on_save(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.services.sponsored_place_service.GoogleMapsClient.reverse_geocode_country",
        lambda self, lat, lng: "KG",
    )
    user = User(email="biz2@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()

    business = Business(
        owner_id=user.id,
        name="Cafe Test",
        description="Test business",
        contact_phone="+996555000222",
        website_url="https://example.com",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(user)

    place = SponsoredPlaceService(db_session).create_my_place(
        user,
        title="Cafe Test",
        description="Desc",
        city="  Bishkek, Kyrgyzstan  ",
        lat=42.87,
        lng=74.59,
        google_place_id=None,
        address="Addr",
        category="  Modern Canteen / Cafe  ",
        cta_text="Visit",
        contact_phone="+996555000222",
        website_url="https://example.com",
    )

    assert place.city == "bishkek"
    assert place.country_code == "KG"
    assert place.category == "modern canteen / cafe"
