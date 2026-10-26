from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class KnowledgeSourceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    owner: str | None = Field(default=None, max_length=200)
    source_url: AnyHttpUrl
    terms_url: AnyHttpUrl
    license_basis: str = Field(min_length=1, max_length=200)
    allowed_use: str = Field(min_length=1, max_length=10000)
    attribution_text: str = Field(min_length=1, max_length=1000)
    geographic_scope: list[str] = Field(min_length=1)
    freshness_days: int = Field(gt=0, le=3650)
    approval_evidence: str | None = Field(default=None, max_length=10000)

    @field_validator("geographic_scope")
    @classmethod
    def normalize_scope(cls, value: list[str]) -> list[str]:
        result = list(dict.fromkeys(item.strip().upper() for item in value if item.strip()))
        if not result or any(item != "*" and len(item) != 2 for item in result):
            raise ValueError("Geographic scope must contain two-letter country codes")
        return result


class KnowledgeSourceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    owner: str | None = Field(default=None, max_length=200)
    source_url: AnyHttpUrl | None = None
    terms_url: AnyHttpUrl | None = None
    license_basis: str | None = Field(default=None, min_length=1, max_length=200)
    allowed_use: str | None = Field(default=None, min_length=1, max_length=10000)
    attribution_text: str | None = Field(default=None, min_length=1, max_length=1000)
    geographic_scope: list[str] | None = None
    freshness_days: int | None = Field(default=None, gt=0, le=3650)
    approval_evidence: str | None = Field(default=None, max_length=10000)
    status: Literal["pending", "approved", "rejected", "withdrawn"] | None = None

    @field_validator("geographic_scope")
    @classmethod
    def normalize_scope(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        result = list(dict.fromkeys(item.strip().upper() for item in value if item.strip()))
        if not result or any(item != "*" and len(item) != 2 for item in result):
            raise ValueError("Geographic scope must contain two-letter country codes")
        return result


class KnowledgeSourceResponse(BaseModel):
    id: int
    name: str
    owner: str | None
    source_url: str
    terms_url: str
    license_basis: str
    allowed_use: str
    attribution_text: str
    geographic_scope: list[str]
    freshness_days: int
    approval_evidence: str | None
    status: str
    approved_by: int | None
    approved_at: datetime | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeFactCreateRequest(BaseModel):
    source_id: int = Field(gt=0)
    subject_type: Literal["place", "route"]
    subject_id: str = Field(min_length=1, max_length=500)
    country_code: str = Field(min_length=2, max_length=2)
    fact_type: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=10000)
    source_record_id: str | None = Field(default=None, max_length=500)
    source_record_url: AnyHttpUrl | None = None
    checked_at: datetime
    freshness_days: int | None = Field(default=None, gt=0, le=3650)
    review_notes: str | None = Field(default=None, max_length=10000)


class KnowledgeFactUpdateRequest(BaseModel):
    source_id: int | None = Field(default=None, gt=0)
    subject_type: Literal["place", "route"] | None = None
    subject_id: str | None = Field(default=None, min_length=1, max_length=500)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    fact_type: str | None = Field(default=None, min_length=1, max_length=80)
    value: str | None = Field(default=None, min_length=1, max_length=10000)
    source_record_id: str | None = Field(default=None, max_length=500)
    source_record_url: AnyHttpUrl | None = None
    checked_at: datetime | None = None
    freshness_days: int | None = Field(default=None, gt=0, le=3650)
    review_notes: str | None = Field(default=None, max_length=10000)
    status: Literal["pending", "approved", "rejected", "withdrawn"] | None = None


class KnowledgeFactResponse(BaseModel):
    id: int
    source_id: int
    source_name: str
    source_url: str
    attribution_text: str
    subject_type: str
    subject_id: str
    country_code: str
    fact_type: str
    value: str
    source_record_id: str | None
    source_record_url: str | None
    checked_at: datetime
    freshness_days: int
    status: str
    review_notes: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeFactAuditResponse(BaseModel):
    id: int
    fact_id: int
    actor_id: int | None
    action: str
    note: str | None
    before_state: dict | None
    after_state: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicReviewedFactResponse(BaseModel):
    subject_type: Literal["place", "route"]
    fact_type: str
    value: str
    source_name: str
    source_url: str
    attribution_text: str
    checked_at: datetime
    verification_status: Literal["reviewed"] = "reviewed"
