from pydantic import BaseModel, ConfigDict

from app.core.destination_registry import Destination


class DestinationBoundsResponse(BaseModel):
    north: float
    south: float
    east: float
    west: float


class DestinationResponse(BaseModel):
    id: str
    country_code: str
    country_name: str
    name: str
    enabled: bool
    center_latitude: float
    center_longitude: float
    bounds: DestinationBoundsResponse
    phone_calling_code: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_destination(cls, destination: Destination) -> "DestinationResponse":
        return cls(
            id=destination.id,
            country_code=destination.country_code,
            country_name=destination.country_name,
            name=destination.name,
            enabled=destination.enabled,
            center_latitude=destination.center_latitude,
            center_longitude=destination.center_longitude,
            bounds=DestinationBoundsResponse(
                north=destination.bounds[0],
                south=destination.bounds[1],
                east=destination.bounds[2],
                west=destination.bounds[3],
            ),
            phone_calling_code=destination.phone_calling_code,
        )
