from unittest.mock import AsyncMock, patch

import pytest

from app.api.v1.routing import estimate_routing, router
from app.schemas.routing import RouteSegment, RoutingRequest, RoutingResponse


@pytest.mark.asyncio
async def test_estimate_routing_returns_correct_totals_on_success() -> None:
    request = RoutingRequest(
        locations=["Bishkek", "Ala-Archa", "Issyk-Kul"],
        transport_type="taxi",
    )
    segments = [
        RouteSegment(
            origin="Bishkek",
            destination="Ala-Archa",
            distance_km=40.25,
            duration_mins=55,
            estimated_cost=563.0,
            transport_type="taxi",
        ),
        RouteSegment(
            origin="Ala-Archa",
            destination="Issyk-Kul",
            distance_km=210.5,
            duration_mins=180,
            estimated_cost=2606.0,
            transport_type="taxi",
        ),
    ]

    with patch("app.api.v1.routing.RoutingService") as routing_service_cls:
        routing_service_cls.return_value.enrich_itinerary = AsyncMock(return_value=segments)

        response = await estimate_routing(request)

    assert isinstance(response, RoutingResponse)
    assert response.segments == segments
    assert response.total_distance_km == 250.75
    assert response.total_duration_mins == 235
    assert response.total_cost == 3169.0


@pytest.mark.asyncio
async def test_estimate_routing_returns_empty_response_when_service_raises() -> None:
    request = RoutingRequest(
        locations=["Bishkek", "Ala-Archa"],
        transport_type="taxi",
    )

    with patch("app.api.v1.routing.RoutingService") as routing_service_cls:
        routing_service_cls.return_value.enrich_itinerary = AsyncMock(
            side_effect=RuntimeError("routing failed")
        )

        response = await estimate_routing(request)

    assert isinstance(response, RoutingResponse)
    assert response.segments == []
    assert response.total_distance_km == 0.0
    assert response.total_duration_mins == 0
    assert response.total_cost == 0.0


def test_routing_router_has_correct_prefix_and_post_estimate_route() -> None:
    assert router.prefix == "/routing"

    estimate_route = next(
        route for route in router.routes if getattr(route, "path", None) == "/routing/estimate"
    )

    assert "POST" in estimate_route.methods
