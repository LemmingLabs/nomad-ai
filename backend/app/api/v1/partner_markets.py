from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.destination import DestinationBoundsResponse
from app.schemas.partner_market import (
    AdminPartnerMarketResponse,
    PartnerMarketResponse,
    PartnerMarketUpdateRequest,
)
from app.services.partner_market_service import PartnerMarketService


router = APIRouter(tags=["Partner markets"])


@router.get("/partner-markets", response_model=list[PartnerMarketResponse])
def get_partner_markets(db: Session = Depends(get_db)) -> list[PartnerMarketResponse]:
    result = []
    for market, destination in PartnerMarketService(db).list_public_markets():
        result.append(PartnerMarketResponse(
            country_code=market.country_code,
            country_name=market.country_name,
            readiness_status=market.readiness_status,
            submissions_enabled=True,
            operating_languages=market.operating_languages,
            required_business_fields=market.required_business_fields,
            onboarding_guidance=market.onboarding_guidance,
            center_latitude=destination.center_latitude,
            center_longitude=destination.center_longitude,
            bounds=DestinationBoundsResponse(
                north=destination.bounds[0],
                south=destination.bounds[1],
                east=destination.bounds[2],
                west=destination.bounds[3],
            ),
            phone_calling_code=destination.phone_calling_code,
        ))
    return result


@router.get("/admin/partner-markets", response_model=list[AdminPartnerMarketResponse])
def get_admin_partner_markets(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[AdminPartnerMarketResponse]:
    return [
        AdminPartnerMarketResponse(
            country_code=market.country_code,
            country_name=market.country_name,
            readiness_status=market.readiness_status,
            submissions_enabled=PartnerMarketService.submissions_enabled(market),
            operating_languages=market.operating_languages,
            required_business_fields=market.required_business_fields,
            onboarding_guidance=market.onboarding_guidance,
            center_latitude=None,
            center_longitude=None,
            bounds=None,
            phone_calling_code=None,
            admin_guidance=market.admin_guidance,
            operational_checklist=market.operational_checklist,
            is_legacy_baseline=market.is_legacy_baseline,
        )
        for market in PartnerMarketService(db).list_admin_markets()
    ]


@router.put("/admin/partner-markets/{country_code}", response_model=AdminPartnerMarketResponse)
def update_admin_partner_market(
    country_code: str,
    payload: PartnerMarketUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AdminPartnerMarketResponse:
    market = PartnerMarketService(db).update(country_code, **payload.model_dump())
    return AdminPartnerMarketResponse(
        country_code=market.country_code,
        country_name=market.country_name,
        readiness_status=market.readiness_status,
        submissions_enabled=PartnerMarketService.submissions_enabled(market),
        operating_languages=market.operating_languages,
        required_business_fields=market.required_business_fields,
        onboarding_guidance=market.onboarding_guidance,
        center_latitude=None,
        center_longitude=None,
        bounds=None,
        phone_calling_code=None,
        admin_guidance=market.admin_guidance,
        operational_checklist=market.operational_checklist,
        is_legacy_baseline=market.is_legacy_baseline,
    )
