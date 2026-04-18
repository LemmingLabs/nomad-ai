import sys
from unittest.mock import AsyncMock

import pytest

# Inject a mock schema module so the file doesn't complain about missing imports
class MockTransportResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __eq__(self, other):
        if hasattr(other, "__dict__"):
            return self.__dict__ == other.__dict__
        return False

class MockDayPlan:
    def __init__(self, location, transport_type=None):
        self.location = location
        class Transport:
            def __init__(self, t_type):
                self.transport_type = t_type
        self.transport = Transport(transport_type) if transport_type else None

try:
    from app.schemas.trip_schema import TransportResult, DayPlan
except ImportError:
    TransportResult = MockTransportResult
    DayPlan = MockDayPlan

from app.services.routing_service import RoutingService, RoutingServiceError
from app.exceptions import TwoGISAuthError, TwoGISTimeoutError


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_estimate_transport_tuple_inputs(mock_client):
    """estimate_transport with tuple inputs calls get_route_info with correct coords."""
    mock_client.get_route_info.return_value = {"distance_km": 10.0, "duration_min": 20.0}
    
    svc = RoutingService(mock_client)
    res = await svc.estimate_transport((1.0, 1.0), (2.0, 2.0), "taxi")
    
    mock_client.get_route_info.assert_called_once_with((1.0, 1.0), (2.0, 2.0), "taxi")
    assert getattr(res, "distance_km") == 10.0
    assert getattr(res, "currency") == "KGS"


@pytest.mark.asyncio
async def test_estimate_transport_string_inputs(mock_client):
    """estimate_transport with string inputs calls search_place, then get_route_info."""
    mock_client.search_place.side_effect = [
        [{"lon": 74.0, "lat": 42.0}],  # Origin resolve
        [{"lon": 75.0, "lat": 43.0}],  # Destination resolve
    ]
    mock_client.get_route_info.return_value = {"distance_km": 10.0, "duration_min": 20.0}
    
    svc = RoutingService(mock_client)
    await svc.estimate_transport("Osh", "Bishkek", "taxi")
    
    assert mock_client.search_place.call_count == 2
    mock_client.get_route_info.assert_called_once_with((74.0, 42.0), (75.0, 43.0), "taxi")


@pytest.mark.asyncio
@pytest.mark.parametrize("transport_type, expected_price", [
    ("taxi", 1400.0),       # 80 + 100*12 + 60*2 = 1400
    ("marshrutka", 360.0),  # 30 + 100*3 + 60*0.5 = 360
    ("transfer", 2680.0),   # 500 + 100*20 + 60*3 = 2680
])
async def test_price_formula(mock_client, transport_type, expected_price):
    """Price formula is correct for taxi, marshrutka, and transfer."""
    mock_client.get_route_info.return_value = {"distance_km": 100.0, "duration_min": 60.0}
    
    svc = RoutingService(mock_client)
    res = await svc.estimate_transport((1.0, 1.0), (2.0, 2.0), transport_type)
    
    assert getattr(res, "price_min") == round(expected_price * 0.9, 2)
    assert getattr(res, "price_max") == round(expected_price * 1.1, 2)


@pytest.mark.asyncio
async def test_enrich_itinerary_attaches_result(mock_client):
    """enrich_itinerary attaches TransportResult to each DayPlan correctly."""
    mock_client.get_route_info.return_value = {"distance_km": 10.0, "duration_min": 20.0}
    
    plans = [
        DayPlan((1.0, 1.0), "taxi"),
        DayPlan((2.0, 2.0), "marshrutka"),
    ]
    
    svc = RoutingService(mock_client)
    enriched = await svc.enrich_itinerary(plans)
    
    assert hasattr(enriched[0].transport, "result")
    assert getattr(enriched[0].transport.result, "distance_km") == 10.0


@pytest.mark.asyncio
async def test_enrich_itinerary_defaults_to_marshrutka(mock_client):
    """enrich_itinerary defaults to "marshrutka" when transport_type is not set."""
    mock_client.get_route_info.return_value = {"distance_km": 10.0, "duration_min": 20.0}
    
    plans = [
        DayPlan((1.0, 1.0)), # No transport set
        DayPlan((2.0, 2.0)),
    ]
    
    svc = RoutingService(mock_client)
    await svc.enrich_itinerary(plans)
    
    # Check what was passed to get_route_info
    mock_client.get_route_info.assert_called_once_with((1.0, 1.0), (2.0, 2.0), "marshrutka")


@pytest.mark.asyncio
async def test_twogis_auth_error_raises(mock_client):
    """TwoGISAuthError from client raises RoutingServiceError."""
    mock_client.get_route_info.side_effect = TwoGISAuthError("auth err")
    
    svc = RoutingService(mock_client)
    with pytest.raises(RoutingServiceError):
        await svc.estimate_transport((1.0, 1.0), (2.0, 2.0), "taxi")


@pytest.mark.asyncio
async def test_twogis_timeout_error_raises(mock_client):
    """TwoGISTimeoutError from client raises RoutingServiceError."""
    mock_client.get_route_info.side_effect = TwoGISTimeoutError("timeout arr")
    
    svc = RoutingService(mock_client)
    with pytest.raises(RoutingServiceError):
        await svc.estimate_transport((1.0, 1.0), (2.0, 2.0), "taxi")
