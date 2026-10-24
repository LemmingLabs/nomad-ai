from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.integrations.google_maps_client import GoogleMapsClient


def _mock_http_client(response=None, error=None):
    client = AsyncMock()
    if error is not None:
        client.post.side_effect = error
    else:
        client.post.return_value = response
    context = AsyncMock()
    context.__aenter__.return_value = client
    context.__aexit__.return_value = None
    return context, client


@pytest.mark.asyncio
async def test_search_place_parses_google_place_response():
    response = Mock()
    response.json.return_value = {
        "places": [{
            "id": "place-1",
            "displayName": {"text": "Osh Bazaar"},
            "formattedAddress": "Bishkek, Kyrgyzstan",
            "location": {"latitude": 42.87, "longitude": 74.58},
        }]
    }
    context, client = _mock_http_client(response)

    with patch("app.integrations.google_maps_client.httpx.AsyncClient", return_value=context):
        places = await GoogleMapsClient().search_place("Osh Bazaar", 74.56, 42.87)

    assert places == [{
        "id": "place-1",
        "name": "Osh Bazaar",
        "address_name": "Bishkek, Kyrgyzstan",
        "lat": 42.87,
        "lon": 74.58,
    }]
    client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_place_returns_empty_list_on_timeout():
    context, _ = _mock_http_client(error=httpx.TimeoutException("timeout"))
    with patch("app.integrations.google_maps_client.httpx.AsyncClient", return_value=context):
        assert await GoogleMapsClient().search_place("Osh Bazaar", 74.56, 42.87) == []


@pytest.mark.asyncio
async def test_route_info_parses_distance_and_duration():
    response = Mock()
    response.json.return_value = {"routes": [{"distanceMeters": 1200, "duration": "300s"}]}
    context, client = _mock_http_client(response)

    with patch("app.integrations.google_maps_client.httpx.AsyncClient", return_value=context):
        route = await GoogleMapsClient().get_route_info(74.56, 42.87, 74.59, 42.88)

    assert route == {"distance_m": 1200, "duration_s": 300}
    client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_route_info_returns_none_on_provider_error():
    request = httpx.Request("POST", "https://routes.googleapis.com/directions/v2:computeRoutes")
    response = httpx.Response(503, request=request)
    context, _ = _mock_http_client(
        error=httpx.HTTPStatusError("server error", request=request, response=response)
    )

    with patch("app.integrations.google_maps_client.httpx.AsyncClient", return_value=context):
        assert await GoogleMapsClient().get_route_info(74.56, 42.87, 74.59, 42.88) is None
