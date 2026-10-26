from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TripActivityResponse(BaseModel):
    time: str | None = None
    time_window: str | None = None
    duration_minutes: int | None = None
    duration_status: Literal["estimated", "unknown"] = "unknown"
    practical_details: list[str] = Field(default_factory=list)
    content_status: str | None = None
    description: str = ""
    type: str = "activity"

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def normalize_optional_activity_details(cls, value):
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        duration = normalized.get("duration_minutes")
        if isinstance(duration, bool):
            duration = None
        try:
            duration = int(round(float(duration))) if duration is not None else None
        except (TypeError, ValueError):
            duration = None
        if duration is not None and duration <= 0:
            duration = None
        normalized["duration_minutes"] = duration
        normalized["duration_status"] = "estimated" if duration is not None else "unknown"
        if not isinstance(normalized.get("time"), str):
            normalized["time"] = None
        if not isinstance(normalized.get("time_window"), str):
            normalized["time_window"] = None
        details = normalized.get("practical_details")
        normalized["practical_details"] = (
            [str(item) for item in details if item]
            if isinstance(details, list)
            else []
        )
        if not isinstance(normalized.get("description"), str):
            normalized["description"] = ""
        if not isinstance(normalized.get("type"), str):
            normalized["type"] = "activity"
        return normalized


class ReviewedFactResponse(BaseModel):
    subject_type: Literal["place", "route"]
    fact_type: str
    value: str
    source_name: str
    source_url: str
    attribution_text: str
    checked_at: str
    verification_status: Literal["reviewed"]


class TripDayResponse(BaseModel):
    day: int = 1
    title: str = ""
    city: str = ""
    location: str = "Unknown location"
    routing_location: str | None = None
    activities: list[TripActivityResponse] = Field(default_factory=list)
    reviewed_facts: list[ReviewedFactResponse] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @field_validator("activities", mode="before")
    @classmethod
    def normalize_legacy_activities(cls, value):
        if not isinstance(value, list):
            return []
        return [
            {
                "description": activity,
                "type": "activity",
                "duration_minutes": None,
                "duration_status": "unknown",
            }
            if isinstance(activity, str)
            else activity
            for activity in value
        ]


class TripGenerationStatusResponse(BaseModel):
    state: Literal["complete", "degraded"]
    source: Literal["ai", "mock"]
    reasons: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class TripQualityWarningResponse(BaseModel):
    code: str
    message: str
    day: int | str | None = None

    model_config = ConfigDict(extra="allow")


class TripItineraryResponse(BaseModel):
    summary: str | None = None
    total_days: int | None = None
    interests: list[str] | None = None
    travel_style: str | None = None
    days: list[TripDayResponse] = Field(default_factory=list)
    generation_status: TripGenerationStatusResponse | None = None
    quality_warnings: list[TripQualityWarningResponse] = Field(default_factory=list)
    route_status: Literal["available", "unavailable"] | None = None

    model_config = ConfigDict(extra="allow")
