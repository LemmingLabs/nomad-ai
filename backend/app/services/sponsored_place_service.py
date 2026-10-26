from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations.google_maps_client import GoogleMapsClient
from app.models.sponsored_place import SponsoredPlace
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.sponsored_place_repository import SponsoredPlaceRepository
from app.services.sponsored_injection_service import normalize_category, normalize_city
from app.services.partner_market_service import PartnerMarketService


class SponsoredPlaceService:
    def __init__(self, db: Session):
        self.db = db
        self.business_repo = BusinessRepository(db)
        self.place_repo = SponsoredPlaceRepository(db)

    def _get_my_business_id(self, current_user: User) -> int:
        business = self.business_repo.get_by_owner_id(current_user.id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found",
            )
        return business.id

    def list_my_places(self, current_user: User) -> list[SponsoredPlace]:
        business_id = self._get_my_business_id(current_user)
        return self.place_repo.list_for_business(business_id)

    def get_my_place(self, current_user: User, place_id: int) -> SponsoredPlace:
        business_id = self._get_my_business_id(current_user)
        place = self.place_repo.get_for_business(business_id, place_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place not found")
        return place

    def create_my_place(self, current_user: User, **payload) -> SponsoredPlace:
        business_id = self._get_my_business_id(current_user)
        payload = self._normalize_payload(payload)
        payload.setdefault("country_code", "KG")
        payload.setdefault("region", None)
        payload.setdefault("operating_language", "en")
        market = PartnerMarketService(self.db).require_open_market(payload["country_code"])
        business = self.business_repo.get_by_id(business_id)
        PartnerMarketService.validate_required_business_fields(market, business, payload)
        if payload.get("operating_language") not in market.operating_languages:
            raise HTTPException(status_code=422, detail="Choose an operating language enabled for this market")
        payload["country_code"] = self._validate_country_location(
            payload["country_code"], payload["lat"], payload["lng"]
        )
        payload["location_verified"] = True
        return self.place_repo.create_for_business(business_id=business_id, **payload)

    def update_my_place(self, current_user: User, place_id: int, **updates) -> SponsoredPlace:
        place = self.get_my_place(current_user, place_id)
        if not updates:
            return place
        # Business cannot approve via this endpoint
        updates.pop("is_approved", None)
        updates = self._normalize_payload(updates)
        country_code = updates.get("country_code", place.country_code)
        market = PartnerMarketService(self.db).get(country_code)
        if market is None:
            raise HTTPException(status_code=422, detail="Partner market is not configured")
        if (
            country_code != place.country_code
            and not PartnerMarketService.submissions_enabled(market)
        ):
            raise HTTPException(status_code=422, detail="Partner submissions are not open in this market")
        language = updates.get("operating_language", place.operating_language)
        if language not in market.operating_languages:
            raise HTTPException(status_code=422, detail="Choose an operating language enabled for this market")
        current_fields = {
            "contact_phone": place.contact_phone,
            "website_url": place.website_url,
        }
        current_fields.update(updates)
        PartnerMarketService.validate_required_business_fields(market, place.business, current_fields)
        if {"country_code", "lat", "lng"} & updates.keys():
            lat = updates.get("lat", place.lat)
            lng = updates.get("lng", place.lng)
            updates["country_code"] = self._validate_country_location(
                country_code, lat, lng
            )
            updates["location_verified"] = True
        return self.place_repo.update(place, **updates)

    def deactivate_my_place(self, current_user: User, place_id: int) -> SponsoredPlace:
        place = self.get_my_place(current_user, place_id)
        return self.place_repo.update(place, is_active=False)

    def _normalize_payload(self, payload: dict) -> dict:
        normalized = dict(payload)
        if "country_code" in normalized:
            normalized["country_code"] = str(normalized["country_code"] or "KG").strip().upper()
        if "region" in normalized and normalized["region"] is not None:
            normalized["region"] = normalized["region"].strip() or None
        if "city" in normalized and normalized["city"] is not None:
            normalized["city"] = normalize_city(normalized["city"])
        if "category" in normalized and normalized["category"] is not None:
            normalized["category"] = normalize_category(normalized["category"])
        return normalized

    def _validate_country_location(
        self, country_code: str, lat: float, lng: float
    ) -> str:
        normalized_country = str(country_code or "").strip().upper()
        if PartnerMarketService(self.db).get(normalized_country) is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Country '{normalized_country}' is not currently configured for partners",
            )

        try:
            latitude = float(lat)
            longitude = float(lng)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A valid latitude and longitude are required",
            ) from None
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Coordinates are outside valid latitude/longitude ranges",
            )

        try:
            actual_country = GoogleMapsClient().reverse_geocode_country(latitude, longitude)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not validate the selected location right now",
            ) from exc
        if actual_country is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The selected coordinates do not resolve to a supported country",
            )
        if actual_country != normalized_country:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Selected coordinates are in {actual_country}, not "
                    f"{normalized_country}"
                ),
            )
        return normalized_country
