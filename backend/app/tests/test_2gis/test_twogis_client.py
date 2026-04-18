import asyncio
from unittest.mock import patch, AsyncMock

import httpx
import pytest

from app.integrations.twogis_client import TwoGISClient
from app.exceptions import (
    TwoGISAuthError,
    TwoGISRateLimitError,
    TwoGISServerError,
    TwoGISTimeoutError,
)


@pytest.mark.asyncio
async def test_search_place_200():
    """search_place returns correctly parsed list when API responds 200."""
    def handler(request: httpx.Request):
        return httpx.Response(200, json={
            "result": {
                "items": [
                    {
                        "id": "123",
                        "name": "Bazaar",
                        "geometry": {"centroid": "POINT(74.58 42.87)"}
                    }
                ]
            }
        })

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()  # Close the original real client
    client.client = httpx.AsyncClient(transport=transport)

    try:
        result = await client.search_place("query", (74.58, 42.87))
        assert result == [{"id": "123", "name": "Bazaar", "lat": 42.87, "lon": 74.58}]
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_search_place_empty_items():
    """search_place returns empty list when result.items is empty."""
    def handler(request: httpx.Request):
        return httpx.Response(200, json={"result": {"items": []}})

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        result = await client.search_place("query", (74.58, 42.87))
        assert result == []
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_get_route_info_200():
    """get_route_info returns correct distance_km and duration_min on 200."""
    def handler(request: httpx.Request):
        return httpx.Response(200, json={
            "result": [{"total_distance": 1500, "total_duration": 300}]
        })

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        result = await client.get_route_info((1.0, 1.0), (2.0, 2.0), "taxi")
        assert result == {"distance_km": 1.5, "duration_min": 5.0}
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_get_dist_matrix_200():
    """get_dist_matrix returns correct list of dicts on 200."""
    def handler(request: httpx.Request):
        return httpx.Response(200, json={
            "routes": [
                {"distance": 2000, "duration": 600},
                {"distance": 3500, "duration": 1200},
            ]
        })

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        result = await client.get_dist_matrix(
            [(1.0, 1.0)], [(2.0, 2.0), (3.0, 3.0)], "taxi"
        )
        assert result == [
            {"distance_km": 2.0, "duration_min": 10.0},
            {"distance_km": 3.5, "duration_min": 20.0},
        ]
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_403_raises_auth_error():
    """403 response raises TwoGISAuthError."""
    def handler(request: httpx.Request):
        return httpx.Response(403)

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        with pytest.raises(TwoGISAuthError):
            await client.search_place("query", (1.0, 1.0))
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
@patch("app.integrations.twogis_client.asyncio.sleep", new_callable=AsyncMock)
async def test_429_raises_rate_limit_after_3_retries(mock_sleep):
    """429 response raises TwoGISRateLimitError after 3 retries."""
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        return httpx.Response(429)

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        with pytest.raises(TwoGISRateLimitError):
            await client.search_place("query", (1.0, 1.0))
    finally:
        await client.client.aclose()

    assert len(calls) == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
@patch("app.integrations.twogis_client.asyncio.sleep", new_callable=AsyncMock)
async def test_500_raises_server_error_after_3_retries(mock_sleep):
    """500 response raises TwoGISServerError after 3 retries."""
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        return httpx.Response(500)

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        with pytest.raises(TwoGISServerError):
            await client.search_place("query", (1.0, 1.0))
    finally:
        await client.client.aclose()

    assert len(calls) == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_timeout_raises_timeout_error():
    """httpx.TimeoutException raises TwoGISTimeoutError."""
    def handler(request: httpx.Request):
        raise httpx.TimeoutException("mock timeout")

    transport = httpx.MockTransport(handler)

    client = TwoGISClient()
    await client.client.aclose()
    client.client = httpx.AsyncClient(transport=transport)

    try:
        with pytest.raises(TwoGISTimeoutError):
            await client.search_place("query", (1.0, 1.0))
    finally:
        await client.client.aclose()


# ============================= test session starts ==============================
# platform linux -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0 -- /home/baki/VS Code projects/NomadAI/nomad-ai/backend/.venv/bin/python
# cachedir: .pytest_cache
# rootdir: /home/baki/VS Code projects/NomadAI/nomad-ai/backend
# plugins: anyio-4.13.0, asyncio-1.3.0
# asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
# collecting ... collected 8 items

# app/tests/test_2gis/test_twogis_client.py::test_search_place_200 PASSED  [ 12%]
# app/tests/test_2gis/test_twogis_client.py::test_search_place_empty_items PASSED [ 25%]
# app/tests/test_2gis/test_twogis_client.py::test_get_route_info_200 PASSED [ 37%]
# app/tests/test_2gis/test_twogis_client.py::test_get_dist_matrix_200 PASSED [ 50%]
# app/tests/test_2gis/test_twogis_client.py::test_403_raises_auth_error PASSED [ 62%]
# app/tests/test_2gis/test_twogis_client.py::test_429_raises_rate_limit_after_3_retries PASSED [ 75%]
# app/tests/test_2gis/test_twogis_client.py::test_500_raises_server_error_after_3_retries PASSED [ 87%]
# app/tests/test_2gis/test_twogis_client.py::test_timeout_raises_timeout_error PASSED [100%]

# ============================== 8 passed in 0.16s ===============================
