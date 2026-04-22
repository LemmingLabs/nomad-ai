from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RouteSegment(BaseModel):
    origin: str
    destination: str
    distance_km: float | None = None
    duration_mins: int | None = None
    estimated_cost: float | None = Field(default=None, ge=0.0)
    transport_type: Literal["taxi", "driving", "walking", "unknown"]

    model_config = ConfigDict(from_attributes=True)




class RoutingRequest(BaseModel):
    locations: list[str] = Field(min_length=2)
    transport_type: str = "taxi"


class RoutingResponse(BaseModel):
    segments: list[RouteSegment]
    total_distance_km: float = 0.0
    total_duration_mins: int = 0
    total_cost: float = 0.0

    @model_validator(mode="after")
    def compute_totals(self) -> "RoutingResponse":
        total_distance_km = round(sum((segment.distance_km or 0.0) for segment in self.segments), 2)
        total_duration_mins = sum((segment.duration_mins or 0) for segment in self.segments)
        total_cost = round(sum((segment.estimated_cost or 0.0) for segment in self.segments), 2)

        if self.total_distance_km == 0:
            self.total_distance_km = total_distance_km
        if self.total_duration_mins == 0:
            self.total_duration_mins = total_duration_mins
        if self.total_cost == 0:
            self.total_cost = total_cost

        return self
