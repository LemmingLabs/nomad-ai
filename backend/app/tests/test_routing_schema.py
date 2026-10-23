import pytest
from pydantic import ValidationError

from app.schemas.routing import RouteSegment, RoutingRequest, RoutingResponse


def test_routing_response_computes_totals_from_segments():
    response = RoutingResponse(segments=[
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
            destination="Karakol",
            distance_km=210.5,
            duration_mins=180,
            estimated_cost=None,
            transport_type="walking",
        ),
    ])

    assert response.total_distance_km == 250.75
    assert response.total_duration_mins == 235
    assert response.total_cost == 563.0


def test_routing_request_needs_two_locations():
    with pytest.raises(ValidationError):
        RoutingRequest(locations=["Bishkek"])


def test_route_segment_rejects_unsupported_transport_and_negative_cost():
    values = {"origin": "A", "destination": "B"}
    with pytest.raises(ValidationError):
        RouteSegment(**values, transport_type="bus")
    with pytest.raises(ValidationError):
        RouteSegment(**values, transport_type="taxi", estimated_cost=-1)
