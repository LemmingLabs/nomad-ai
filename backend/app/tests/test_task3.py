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
async def test_enrich_itinerary_happy_path_returns_distance_duration_and_cost() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [{"lon": 74.57, "lat": 42.88}],
            [{"lon": 74.58, "lat": 42.89}],
        ]
    )
    client.get_dist_matrix = AsyncMock(
        return_value=[
            [
                {"distance_m": 1200, "duration_s": 600},
                {"distance_m": 9999, "duration_s": 9999},
            ],
            [
                {"distance_m": 8888, "duration_s": 8888},
                {"distance_m": 2500, "duration_s": 900},
            ],
        ]
    )
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B", "C"])

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 1.2,
            "duration_mins": 10,
            "estimated_cost": 94.0,
            "transport_type": "taxi",
        },
        {
            "origin": "B",
            "destination": "C",
            "distance_km": 2.5,
            "duration_mins": 15,
            "estimated_cost": 110.0,
            "transport_type": "taxi",
        },
    ]


@pytest.mark.asyncio
async def test_enrich_itinerary_uses_fallback_when_search_place_returns_empty_list() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [],
        ]
    )
    client.get_dist_matrix = AsyncMock(return_value=None)
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B"])

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
async def test_enrich_itinerary_uses_route_info_fallback_when_get_dist_matrix_returns_none() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [{"lon": 74.57, "lat": 42.88}],
        ]
    )
    client.get_dist_matrix = AsyncMock(return_value=None)
    client.get_route_info = AsyncMock(return_value={"distance_m": 3400, "duration_s": 780})
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B"])

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 3.4,
            "duration_mins": 13,
            "estimated_cost": 121.0,
            "transport_type": "taxi",
        }
    ]


@pytest.mark.asyncio
async def test_enrich_itinerary_sets_walking_cost_to_zero() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(
        side_effect=[
            [{"lon": 74.56, "lat": 42.87}],
            [{"lon": 74.57, "lat": 42.88}],
        ]
    )
    client.get_dist_matrix = AsyncMock(return_value=[[{"distance_m": 700, "duration_s": 660}]])
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B"], default_transport="walking")

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 0.7,
            "duration_mins": 11,
            "estimated_cost": 0.0,
            "transport_type": "walking",
        }
    ]


@pytest.mark.asyncio
async def test_enrich_itinerary_total_exception_still_returns_list() -> None:
    client = MagicMock()
    client.search_place = AsyncMock(side_effect=RuntimeError("boom"))
    with patch("app.services.routing_service.TwoGISClient", return_value=client):
        service = RoutingService()
        segments = await service.enrich_itinerary(["A", "B", "C"])

    assert [_segment_to_dict(segment) for segment in segments] == [
        {
            "origin": "A",
            "destination": "B",
            "distance_km": 0.0,
            "duration_mins": 0,
            "estimated_cost": 0.0,
            "transport_type": "unknown",
        },
        {
            "origin": "B",
            "destination": "C",
            "distance_km": 0.0,
            "duration_mins": 0,
            "estimated_cost": 0.0,
            "transport_type": "unknown",
        },
    ]
