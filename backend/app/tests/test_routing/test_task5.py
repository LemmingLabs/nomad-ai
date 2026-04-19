from copy import deepcopy
from unittest.mock import AsyncMock

import pytest

from app.schemas.routing import RouteSegment
from app.services.routing_service import RoutingService


@pytest.mark.asyncio
async def test_enrich_from_itinerary_json_attaches_route_from_previous_to_day_two_plus() -> None:
    itinerary = {
        "days": [
            {"day": 1, "location": "Bishkek", "activities": [], "tips": "A"},
            {"day": 2, "location": "Ala-Archa", "activities": [], "tips": "B"},
            {"day": 3, "location": "Karakol", "activities": [], "tips": "C"},
        ]
    }
    segments = [
        RouteSegment(
            origin="Bishkek",
            destination="Ala-Archa",
            distance_km=40.0,
            duration_mins=60,
            estimated_cost=560.0,
            transport_type="taxi",
        ),
        RouteSegment(
            origin="Ala-Archa",
            destination="Karakol",
            distance_km=390.5,
            duration_mins=360,
            estimated_cost=4766.0,
            transport_type="driving",
        ),
    ]
    service = RoutingService(client=AsyncMock())
    service.enrich_itinerary = AsyncMock(return_value=segments)

    result = await service.enrich_from_itinerary_json(itinerary)

    assert result["days"][1]["route_from_previous"] == segments[0].model_dump()
    assert result["days"][2]["route_from_previous"] == segments[1].model_dump()


@pytest.mark.asyncio
async def test_enrich_from_itinerary_json_sets_day_one_route_to_none() -> None:
    itinerary = {
        "days": [
            {"day": 1, "location": "Bishkek", "activities": [], "tips": "A"},
            {"day": 2, "location": "Ala-Archa", "activities": [], "tips": "B"},
        ]
    }
    service = RoutingService(client=AsyncMock())
    service.enrich_itinerary = AsyncMock(
        return_value=[
            RouteSegment(
                origin="Bishkek",
                destination="Ala-Archa",
                distance_km=40.0,
                duration_mins=60,
                estimated_cost=560.0,
                transport_type="taxi",
            )
        ]
    )

    result = await service.enrich_from_itinerary_json(itinerary)

    assert result["days"][0]["route_from_previous"] is None


@pytest.mark.asyncio
async def test_enrich_from_itinerary_json_returns_itinerary_unchanged_when_days_less_than_two() -> None:
    itinerary = {
        "days": [
            {"day": 1, "location": "Bishkek", "activities": [], "tips": "A"},
        ]
    }
    original = deepcopy(itinerary)
    service = RoutingService(client=AsyncMock())
    service.enrich_itinerary = AsyncMock()

    result = await service.enrich_from_itinerary_json(itinerary)

    assert result == original
    service.enrich_itinerary.assert_not_awaited()


@pytest.mark.asyncio
async def test_enrich_from_itinerary_json_returns_original_itinerary_on_internal_exception() -> None:
    itinerary = {
        "days": [
            {"day": 1, "location": "Bishkek", "activities": [], "tips": "A"},
            {"day": 2, "location": "Ala-Archa", "activities": [], "tips": "B"},
        ]
    }
    original = deepcopy(itinerary)
    service = RoutingService(client=AsyncMock())
    service.enrich_itinerary = AsyncMock(side_effect=RuntimeError("routing failed"))

    result = await service.enrich_from_itinerary_json(itinerary)

    assert result == original
