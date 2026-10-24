from unittest.mock import AsyncMock

import pytest

from app.services.routing_service import RoutingService


@pytest.mark.asyncio
async def test_enrich_itinerary_falls_back_when_geocoding_misses_a_stop():
    client = AsyncMock()
    client.search_place.side_effect = [
        [{"name": "A", "lat": 42.87, "lon": 74.56}],
        [],
    ]
    service = RoutingService(client=client)

    segments = await service.enrich_itinerary(["A", "B"])

    assert len(segments) == 1
    assert segments[0].transport_type == "unknown"
    assert segments[0].distance_km is None
    client.get_route_info.assert_not_awaited()


@pytest.mark.asyncio
async def test_enrich_itinerary_does_not_charge_for_walking():
    client = AsyncMock()
    client.search_place.side_effect = [
        [{"name": "A", "lat": 42.87, "lon": 74.56}],
        [{"name": "B", "lat": 42.88, "lon": 74.57}],
    ]
    client.get_route_info.return_value = {"distance_m": 700, "duration_s": 660}
    service = RoutingService(client=client)

    segments = await service.enrich_itinerary(["A", "B"], default_transport="walking")

    assert len(segments) == 1
    assert segments[0].distance_km == 0.7
    assert segments[0].duration_mins == 11
    assert segments[0].estimated_cost is None
    assert segments[0].transport_type == "walking"
