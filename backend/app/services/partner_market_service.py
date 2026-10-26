import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.destination_registry import get_destination, list_destinations
from app.models.partner_market import PartnerMarket


REQUIRED_CHECKLIST_ITEMS = frozenset({
    "support_owner",
    "support_language",
    "business_verification",
    "advertising_review",
    "payment_capability",
    "privacy_review",
    "escalation_owner",
})


class PartnerMarketService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def submissions_enabled(market: PartnerMarket) -> bool:
        return market.readiness_status in {"pilot", "open"}

    def list_admin_markets(self) -> list[PartnerMarket]:
        return list(self.db.execute(
            select(PartnerMarket).order_by(PartnerMarket.country_name.asc())
        ).scalars().all())

    def list_public_markets(self) -> list[tuple[PartnerMarket, object]]:
        markets = self.list_admin_markets()
        enabled_destinations = {
            item.country_code: item for item in list_destinations(enabled_only=True)
        }
        return [
            (market, enabled_destinations[market.country_code])
            for market in markets
            if self.submissions_enabled(market)
            and market.country_code in enabled_destinations
        ]

    def get(self, country_code: str) -> PartnerMarket | None:
        return self.db.get(PartnerMarket, country_code.strip().upper())

    def update(self, country_code: str, **values) -> PartnerMarket:
        normalized_code = country_code.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", normalized_code):
            raise HTTPException(status_code=422, detail="Country code must be a two-letter ISO code")

        market = self.get(normalized_code)
        status_value = values["readiness_status"]
        checklist = values["operational_checklist"]
        is_legacy_baseline = bool(market and market.is_legacy_baseline)
        if status_value in {"pilot", "open"} and not is_legacy_baseline:
            if not REQUIRED_CHECKLIST_ITEMS.issubset(checklist) or any(
                checklist.get(item) is not True for item in REQUIRED_CHECKLIST_ITEMS
            ):
                raise HTTPException(
                    status_code=422,
                    detail="All operational checklist items must be approved before accepting submissions",
                )
            destination = get_destination(normalized_code.lower())
            if destination is None or not destination.enabled:
                raise HTTPException(
                    status_code=422,
                    detail="Enable traveler destination support before opening this partner market",
                )

        if market is None:
            market = PartnerMarket(
                country_code=normalized_code,
                readiness_status="closed",
                operating_languages=["en"],
                required_business_fields=[],
                onboarding_guidance="",
                admin_guidance="",
                operational_checklist={},
                is_legacy_baseline=False,
            )
            self.db.add(market)

        market.country_code = normalized_code
        for field, value in values.items():
            setattr(market, field, value)
        self.db.commit()
        self.db.refresh(market)
        return market

    def require_open_market(self, country_code: str) -> PartnerMarket:
        market = self.get(country_code)
        if market is None or not self.submissions_enabled(market):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Partner submissions are not currently open in {country_code.strip().upper()}",
            )
        return market

    @staticmethod
    def validate_required_business_fields(
        market: PartnerMarket, business, place_fields: dict
    ) -> None:
        missing = []
        for field in market.required_business_fields:
            value = getattr(business, field, None) or place_fields.get(field)
            if value is None or not str(value).strip():
                missing.append(field)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Complete these required business details for {market.country_code}: {', '.join(missing)}",
            )
