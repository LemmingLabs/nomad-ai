from pathlib import Path
import sys
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.integrations.twogis_client import TwoGISClient


def _build_async_client(response: object | None = None, exception: Exception | None = None):
    client = AsyncMock()
    if exception is not None:
        client.get.side_effect = exception
        client.post.side_effect = exception
    else:
        client.get.return_value = response
        client.post.return_value = response

    async_client_cm = AsyncMock()
    async_client_cm.__aenter__.return_value = client
    async_client_cm.__aexit__.return_value = None
    return async_client_cm, client


@pytest.mark.asyncio
async def test_search_place_returns_parsed_list_on_200() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "result": {
            "items": [
                {
                    "id": "1",
                    "name": "Osh Bazaar",
                    "address_name": "Bishkek",
                    "point": {"lat": 42.87, "lon": 74.58},
                }
            ]
        }
    }
    async_client_cm, client = _build_async_client(response=response)

    with patch("app.integrations.twogis_client.httpx.AsyncClient", return_value=async_client_cm):
        places = await TwoGISClient().search_place("Osh Bazaar Bishkek", 74.5698, 42.8746)

    assert places == [
        {
            "id": "1",
            "name": "Osh Bazaar",
            "address_name": "Bishkek",
            "lat": 42.87,
            "lon": 74.58,
        }
    ]
    client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_place_returns_empty_list_on_403() -> None:
    request = httpx.Request("GET", "https://catalog.api.2gis.com/3.0/items")
    response = Mock()
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "forbidden",
        request=request,
        response=httpx.Response(403, request=request),
    )
    async_client_cm, _ = _build_async_client(response=response)

    with patch("app.integrations.twogis_client.httpx.AsyncClient", return_value=async_client_cm):
        places = await TwoGISClient().search_place("Osh Bazaar Bishkek", 74.5698, 42.8746)

    assert places == []


@pytest.mark.asyncio
async def test_search_place_returns_empty_list_on_timeout() -> None:
    async_client_cm, _ = _build_async_client(exception=httpx.TimeoutException("timeout"))

    with patch("app.integrations.twogis_client.httpx.AsyncClient", return_value=async_client_cm):
        places = await TwoGISClient().search_place("Osh Bazaar Bishkek", 74.5698, 42.8746)

    assert places == []


@pytest.mark.asyncio
async def test_get_route_info_returns_distance_m_and_duration_s_on_200() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "result": [
            {
                "total_distance": 1200,
                "total_duration": 300,
            }
        ]
    }
    async_client_cm, client = _build_async_client(response=response)

    with patch("app.integrations.twogis_client.httpx.AsyncClient", return_value=async_client_cm):
        route = await TwoGISClient().get_route_info(74.56, 42.87, 74.59, 42.88)

    assert route == {"distance_m": 1200, "duration_s": 300}
    client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_route_info_returns_none_on_5xx() -> None:
    request = httpx.Request("POST", "https://routing.api.2gis.com/routing/7.0.0/global")
    response = Mock()
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "server error",
        request=request,
        response=httpx.Response(503, request=request),
    )
    async_client_cm, _ = _build_async_client(response=response)

    with patch("app.integrations.twogis_client.httpx.AsyncClient", return_value=async_client_cm):
        route = await TwoGISClient().get_route_info(74.56, 42.87, 74.59, 42.88)

    assert route is None

