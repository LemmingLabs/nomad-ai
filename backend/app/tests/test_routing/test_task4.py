import pytest
from pydantic import ValidationError

from app.schemas.routing import RouteSegment, RoutingRequest, RoutingResponse


def test_route_segment_validates_correctly() -> None:
    segment = RouteSegment(
        origin="Bishkek",
        destination="Ala-Archa",
        distance_km=40.25,
        duration_mins=55,
        estimated_cost=563.0,
        transport_type="taxi",
    )

    assert segment.origin == "Bishkek"
    assert segment.destination == "Ala-Archa"
    assert segment.distance_km == 40.25
    assert segment.duration_mins == 55
    assert segment.estimated_cost == 563.0
    assert segment.transport_type == "taxi"


def test_route_segment_rejects_invalid_transport_type() -> None:
    with pytest.raises(ValidationError):
        RouteSegment(
            origin="Bishkek",
            destination="Ala-Archa",
            distance_km=40.25,
            duration_mins=55,
            estimated_cost=563.0,
            transport_type="bus",
        )


def test_routing_response_auto_computes_totals_from_segments() -> None:
    response = RoutingResponse(
        segments=[
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
                destination="Chunkurchak",
                distance_km=28.75,
                duration_mins=42,
                estimated_cost=425.0,
                transport_type="driving",
            ),
        ]
    )

    assert response.total_distance_km == 69.0
    assert response.total_duration_mins == 97
    assert response.total_cost == 988.0


def test_routing_request_rejects_locations_with_fewer_than_two_items() -> None:
    with pytest.raises(ValidationError):
        RoutingRequest(locations=["Bishkek"])
