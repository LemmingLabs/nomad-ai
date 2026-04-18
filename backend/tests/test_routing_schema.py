import pytest
from pydantic import ValidationError
from app.schemas.routing import RouteResponse


def test_route_response_valid_car():
    """RouteResponse instantiates correctly with valid data for car."""
    obj = RouteResponse(
        origin="A",
        destination="B",
        distance_km=10.0,
        duration_mins=20,
        estimated_cost=100.0,
        transport_type="car"
    )
    assert obj.transport_type == "car"


def test_route_response_valid_taxi():
    """RouteResponse instantiates correctly with valid data for taxi."""
    obj = RouteResponse(
        origin="A",
        destination="B",
        distance_km=1.0,
        duration_mins=5,
        estimated_cost=0.0,
        transport_type="taxi"
    )
    assert obj.transport_type == "taxi"


def test_route_response_valid_walking():
    """RouteResponse instantiates correctly with valid data for walking."""
    obj = RouteResponse(
        origin="A",
        destination="B",
        distance_km=1.0,
        duration_mins=15,
        estimated_cost=0.0,
        transport_type="walking"
    )
    assert obj.transport_type == "walking"


def test_transport_type_bus_invalid():
    """transport_type="bus" raises ValidationError."""
    with pytest.raises(ValidationError):
        RouteResponse(
            origin="A",
            destination="B",
            distance_km=1.0,
            duration_mins=15,
            estimated_cost=0.0,
            transport_type="bus"
        )


def test_distance_km_0_invalid():
    """distance_km=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        RouteResponse(
            origin="A",
            destination="B",
            distance_km=0.0,
            duration_mins=15,
            estimated_cost=0.0,
            transport_type="car"
        )


def test_distance_km_negative_1_invalid():
    """distance_km=-1 raises ValidationError."""
    with pytest.raises(ValidationError):
        RouteResponse(
            origin="A",
            destination="B",
            distance_km=-1.0,
            duration_mins=15,
            estimated_cost=0.0,
            transport_type="car"
        )


def test_duration_mins_0_invalid():
    """duration_mins=0 raises ValidationError."""
    with pytest.raises(ValidationError):
        RouteResponse(
            origin="A",
            destination="B",
            distance_km=1.0,
            duration_mins=0,
            estimated_cost=0.0,
            transport_type="car"
        )


def test_estimated_cost_0_valid():
    """estimated_cost=0 is valid (zero cost is allowed)."""
    obj = RouteResponse(
        origin="A",
        destination="B",
        distance_km=1.0,
        duration_mins=15,
        estimated_cost=0.0,
        transport_type="car"
    )
    assert obj.estimated_cost == 0.0


def test_estimated_cost_negative_1_invalid():
    """estimated_cost=-1 raises ValidationError."""
    with pytest.raises(ValidationError):
        RouteResponse(
            origin="A",
            destination="B",
            distance_km=1.0,
            duration_mins=15,
            estimated_cost=-1.0,
            transport_type="car"
        )


def test_route_response_is_immutable():
    """RouteResponse is immutable — assigning to any field after instantiation raises ValidationError or TypeError."""
    obj = RouteResponse(
        origin="A",
        destination="B",
        distance_km=1.0,
        duration_mins=15,
        estimated_cost=0.0,
        transport_type="car"
    )
    with pytest.raises((ValidationError, TypeError)):
        obj.distance_km = 2.0


def test_from_twogis_returns_correct_response():
    """from_twogis classmethod returns correct RouteResponse with valid inputs."""
    obj = RouteResponse.from_twogis(
        origin="A",
        destination="B",
        distance_km=10.0,
        duration_mins=20,
        estimated_cost=100.0,
        transport_type="car"
    )
    assert isinstance(obj, RouteResponse)
    assert obj.transport_type == "car"
    assert obj.distance_km == 10.0


def test_from_twogis_raises_value_error_for_invalid_type():
    """from_twogis raises ValueError when transport_type is not in allowed literals."""
    with pytest.raises(ValueError) as exc:
        RouteResponse.from_twogis(
            origin="A",
            destination="B",
            distance_km=10.0,
            duration_mins=20,
            estimated_cost=100.0,
            transport_type="bus"
        )
    assert "Invalid transport_type" in str(exc.value)
