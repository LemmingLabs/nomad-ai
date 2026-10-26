"""Canonical destination registry used by API validation and itinerary prompts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Destination:
    id: str
    country_code: str
    country_name: str
    name: str
    enabled: bool
    supported_cities: tuple[str, ...]
    center_latitude: float
    center_longitude: float


DESTINATIONS: tuple[Destination, ...] = (
    Destination(
        id="kg",
        country_code="KG",
        country_name="Kyrgyzstan",
        name="Kyrgyzstan",
        enabled=True,
        supported_cities=(
            "Bishkek",
            "Karakol",
            "Cholpon-Ata",
            "Osh",
            "Bokonbaevo",
            "Jeti-Oguz",
            "Ala-Archa",
            "Kochkor",
            "Naryn",
            "Tamga",
            "Barskoon",
        ),
        center_latitude=42.8746,
        center_longitude=74.5698,
    ),
)

DEFAULT_DESTINATION_ID = "kg"
DEFAULT_COUNTRY_CODE = "KG"


def list_destinations(*, enabled_only: bool = False) -> list[Destination]:
    return [destination for destination in DESTINATIONS if destination.enabled or not enabled_only]


def get_destination(destination_id: str) -> Destination | None:
    normalized_id = destination_id.strip().lower()
    return next((item for item in DESTINATIONS if item.id == normalized_id), None)


def resolve_destination(
    *,
    country_code: str,
    destination_id: str,
    require_enabled: bool = True,
) -> Destination:
    destination = get_destination(destination_id)
    if destination is None:
        raise ValueError(f"Destination '{destination_id}' is not supported")
    if require_enabled and not destination.enabled:
        raise ValueError(f"Destination '{destination_id}' is not currently available")
    if destination.country_code != country_code.strip().upper():
        raise ValueError(
            f"Destination '{destination_id}' does not belong to country '{country_code}'"
        )
    return destination
