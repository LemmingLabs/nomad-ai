from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RouteSegment(BaseModel):
    origin: str
    destination: str
    distance_km: float
    duration_mins: int
    estimated_cost: float
    transport_type: Literal["taxi", "driving", "walking", "unknown"]

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    """
    Internal contract for route data passed between routing_service,
    twogis_client, and downstream modules. Do not change field names
    without updating all consumers.
    """
    origin: str
    destination: str
    distance_km: float = Field(gt=0.0)
    duration_mins: int = Field(gt=0)
    estimated_cost: float = Field(ge=0.0)
    transport_type: Literal["car", "taxi", "walking"]

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    @classmethod
    def from_twogis(
        cls,
        origin: str,
        destination: str,
        distance_km: float,
        duration_mins: int,
        estimated_cost: float,
        transport_type: str
    ) -> "RouteResponse":
        allowed_transports = {"car", "taxi", "walking"}
        if transport_type not in allowed_transports:
            raise ValueError(
                f"Invalid transport_type '{transport_type}'. Must be one of {allowed_transports}."
            )
        
        return cls(
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            duration_mins=duration_mins,
            estimated_cost=estimated_cost,
            transport_type=transport_type,  # type: ignore
        )
