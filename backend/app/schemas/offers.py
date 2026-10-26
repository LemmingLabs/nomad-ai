from datetime import date
import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


def _normalize_country_code(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Destination country must be a two-letter country code")
    normalized = value.strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", normalized):
        raise ValueError("Destination country must be a two-letter country code")
    return normalized


def _normalize_place_query(value: str) -> str:
    normalized = value.strip()
    if not 2 <= len(normalized) <= 120:
        raise ValueError("Place must contain between 2 and 120 non-whitespace characters")
    return normalized


class FlightOfferSearchRequest(BaseModel):
    kind: Literal["flight"]
    destination_country_code: str = Field(min_length=2, max_length=2)
    origin: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    departure_date: date
    return_date: date | None = None
    passengers: int = Field(default=1, ge=1, le=9)

    @field_validator("destination_country_code", mode="before")
    @classmethod
    def validate_country_code(cls, value: object) -> str:
        return _normalize_country_code(value)

    @field_validator("origin", "destination")
    @classmethod
    def normalize_flight_locations(cls, value: str) -> str:
        return _normalize_place_query(value)

    @field_validator("departure_date")
    @classmethod
    def validate_departure_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Departure date cannot be in the past")
        return value

    @model_validator(mode="after")
    def validate_return_date(self):
        if self.return_date and self.return_date < self.departure_date:
            raise ValueError("Return date must be on or after departure date")
        return self


class StayOfferSearchRequest(BaseModel):
    kind: Literal["stay"]
    destination_country_code: str = Field(min_length=2, max_length=2)
    destination_city: str = Field(min_length=2, max_length=120)
    check_in: date
    check_out: date
    adults: int = Field(default=1, ge=1, le=16)
    rooms: int = Field(default=1, ge=1, le=8)

    @field_validator("destination_country_code", mode="before")
    @classmethod
    def validate_country_code(cls, value: object) -> str:
        return _normalize_country_code(value)

    @field_validator("destination_city")
    @classmethod
    def normalize_destination_city(cls, value: str) -> str:
        return _normalize_place_query(value)

    @field_validator("check_in", "check_out")
    @classmethod
    def validate_dates_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Stay dates cannot be in the past")
        return value

    @model_validator(mode="after")
    def validate_stay_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("Check-out must be after check-in")
        return self


OfferSearchRequest = Annotated[
    FlightOfferSearchRequest | StayOfferSearchRequest,
    Field(discriminator="kind"),
]


class OffersUnavailableResponse(BaseModel):
    state: Literal["unavailable"] = "unavailable"
    reason: Literal["feature_disabled", "provider_unconfigured"]
    message: str
