import pytest
from fastapi import HTTPException

from app.models.partner_market import PartnerMarket
from app.api.v1.partner_markets import get_partner_markets
from app.services.partner_market_service import (
    REQUIRED_CHECKLIST_ITEMS,
    PartnerMarketService,
)


def _market(**overrides):
    values = {
        "country_name": "Test Country",
        "readiness_status": "closed",
        "operating_languages": ["en"],
        "required_business_fields": [],
        "onboarding_guidance": "",
        "admin_guidance": "",
        "operational_checklist": {},
    }
    values.update(overrides)
    return values


def test_public_partner_market_list_only_includes_open_supported_destinations(db_session):
    db_session.add(PartnerMarket(
        country_code="KG",
        is_legacy_baseline=True,
        **_market(country_name="Kyrgyzstan", readiness_status="open"),
    ))
    db_session.add(PartnerMarket(country_code="US", **_market()))
    db_session.commit()

    markets = PartnerMarketService(db_session).list_public_markets()
    api_markets = get_partner_markets(db_session)

    assert [(market.country_code, destination.id) for market, destination in markets] == [("KG", "kg")]
    assert [market.country_code for market in api_markets] == ["KG"]
    assert api_markets[0].operating_languages == ["en"]
    assert not hasattr(api_markets[0], "admin_guidance")


def test_new_market_cannot_open_until_all_readiness_checks_are_approved(db_session):
    service = PartnerMarketService(db_session)

    with pytest.raises(HTTPException) as error:
        service.update(
            "US",
            **_market(
                readiness_status="open",
                operational_checklist={key: True for key in REQUIRED_CHECKLIST_ITEMS - {"privacy_review"}},
            ),
        )

    assert error.value.status_code == 422
    assert "checklist" in error.value.detail.lower()


def test_new_market_needs_traveler_destination_support_before_opening(db_session):
    service = PartnerMarketService(db_session)

    with pytest.raises(HTTPException) as error:
        service.update(
            "US",
            **_market(
                readiness_status="pilot",
                operational_checklist={key: True for key in REQUIRED_CHECKLIST_ITEMS},
            ),
        )

    assert error.value.status_code == 422
    assert "destination" in error.value.detail.lower()


def test_market_can_be_configured_as_closed_without_checklist_completion(db_session):
    market = PartnerMarketService(db_session).update(
        "US",
        **_market(operational_checklist={"support_owner": True}),
    )

    assert market.readiness_status == "closed"
    assert not PartnerMarketService(db_session).submissions_enabled(market)
