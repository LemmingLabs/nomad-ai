import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.business import Business
from app.models.sponsored_place import SponsoredPlace
from app.models.user import User
from app.services.sponsored_injection_service import SponsoredInjectionService


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


def _create_sponsored_place(db_session, *, city: str = "Bishkek", category: str = "Modern Canteen / Cafe") -> SponsoredPlace:
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


def test_category_match_supports_canteen_and_cafe_aliases(db_session):
    service = SponsoredInjectionService(db_session)

    assert service._category_match_score("Modern Canteen / Cafe", {"restaurant"}) >= 2
    assert service._category_match_score("Food Court Cafe", {"restaurant"}) >= 2
