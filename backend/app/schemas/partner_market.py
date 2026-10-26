from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.destination import DestinationBoundsResponse


class PartnerMarketUpdateRequest(BaseModel):
    country_name: str = Field(min_length=1, max_length=120)
    readiness_status: Literal["closed", "pilot", "open"]
    operating_languages: list[str] = Field(min_length=1)
    required_business_fields: list[str] = Field(default_factory=list)
    onboarding_guidance: str = Field(default="", max_length=4000)
    admin_guidance: str = Field(default="", max_length=4000)
    operational_checklist: dict[str, bool] = Field(default_factory=dict)

    @field_validator("operating_languages")
    @classmethod
    def normalize_languages(cls, value: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(item.strip().lower() for item in value if item.strip()))
        if not normalized:
            raise ValueError("At least one operating language is required")
        return normalized


class PartnerMarketResponse(BaseModel):
    country_code: str
    country_name: str
    readiness_status: Literal["closed", "pilot", "open"]
    submissions_enabled: bool
    operating_languages: list[str]
    required_business_fields: list[str]
    onboarding_guidance: str
    center_latitude: float | None = None
    center_longitude: float | None = None
    bounds: DestinationBoundsResponse | None = None
    phone_calling_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminPartnerMarketResponse(PartnerMarketResponse):
    admin_guidance: str
    operational_checklist: dict[str, bool]
    is_legacy_baseline: bool = False
