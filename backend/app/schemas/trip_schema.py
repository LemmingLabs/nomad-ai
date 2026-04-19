from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class TransportResult(BaseModel):
    from_: str = Field(alias="from")
    to: str
    distance_km: float
    duration_min: float
    price_min: float
    price_max: float
    currency: str = "KGS"
    transport_type: str

class DayPlan(BaseModel):
    day: int
    location: str
    activities: List[str]
    transport: Optional[TransportResult] = None
    accommodation: Optional[Dict] = None
    image_url: Optional[str] = None

class TripRequest(BaseModel):
    budget: float
    days: int = Field(ge=1, le=14)
    interests: List[str]
    accommodation_type: str = "budget"
