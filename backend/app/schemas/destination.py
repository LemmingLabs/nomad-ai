from pydantic import BaseModel, ConfigDict

from app.core.destination_registry import Destination


class DestinationResponse(BaseModel):
    id: str
    country_code: str
    country_name: str
    name: str
    enabled: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_destination(cls, destination: Destination) -> "DestinationResponse":
        return cls(
            id=destination.id,
            country_code=destination.country_code,
            country_name=destination.country_name,
            name=destination.name,
            enabled=destination.enabled,
        )
