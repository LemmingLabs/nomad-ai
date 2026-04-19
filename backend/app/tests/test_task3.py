from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.routing_service import RoutingService


def _segment_to_dict(segment: object) -> dict:
    return {
        "origin": getattr(segment, "origin"),
        "destination": getattr(segment, "destination"),
        "distance_km": getattr(segment, "distance_km"),
        "duration_mins": getattr(segment, "duration_mins"),
        "estimated_cost": getattr(segment, "estimated_cost"),
        "transport_type": getattr(segment, "transport_type"),
    }




@pytest.mark.asyncio
async def test_enrich_itinerary_uses_fallback_when_search_place_returns_empty_list() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [],
        ]
    )
    client.get_route_info = AsyncMock()
    client.get_dist_matrix = AsyncMock()
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B"])

    client.get_route_info.assert_not_awaited()
    client.get_dist_matrix.assert_not_awaited()

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 0.0,
            "duration_mins": 0,
            "estimated_cost": 0.0,
            "transport_type": "unknown",
        }
    ]



@pytest.mark.asyncio
async def test_enrich_itinerary_sets_walking_cost_to_none() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [{"lon": 74.57, "lat": 42.88}],
        ]
    )
    client.get_route_info = AsyncMock(return_value={"distance_m": 700, "duration_s": 660})
    client.get_dist_matrix = AsyncMock()
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B"], default_transport="walking")

    client.get_dist_matrix.assert_not_awaited()

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 0.7,
            "duration_mins": 11,
            "estimated_cost": None,
            "transport_type": "walking",
        }
    ]

