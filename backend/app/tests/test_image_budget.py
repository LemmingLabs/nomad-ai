from unittest.mock import Mock

import httpx
import pytest

from app.integrations.pexels_client import PexelsClient
from app.services import image_enrichment_service as images


def itinerary(count):
    return {"days": [{"location": f"Place {i}", "city": "City"} for i in range(count)]}


@pytest.mark.parametrize("count", [1, 7, 14])
@pytest.mark.parametrize("outcome", ["success", "miss", "timeout"])
def test_image_request_budget_and_elapsed_time(monkeypatch, count, outcome):
    # A controlled clock makes the comparison reproducible without network or sleeping.
    clock = [0.0]
    monkeypatch.setattr(images.time, "monotonic", lambda: clock[0])
    service = images.ImageEnrichmentService()
    client = Mock(unavailable=False)
    calls = []

    def search(query):
        calls.append(query)
        clock[0] += 2.0
        if outcome == "timeout":
            client.unavailable = True
            return None
        if outcome == "success":
            return {"photo_id": str(len(calls)), "url": "https://example.test/image"}
        return None

    client.search_photo.side_effect = search
    service.client = client
    result = service.enrich_trip_with_images(itinerary(count))
    assert len(calls) <= images.MAX_IMAGE_REQUESTS
    assert clock[0] <= images.IMAGE_SEARCH_BUDGET_SECONDS
    assert len(calls) == (1 if outcome == "timeout" else min(count, 3) if outcome == "success" else min(count * 2, 4))
    assert len(result["days"]) == count


def test_selective_refresh_clears_stale_images_even_after_budget_exhaustion():
    service = images.ImageEnrichmentService()
    service.client = Mock(unavailable=False)
    service.client.search_photo.return_value = None
    trip = itinerary(5)
    for day in trip["days"]:
        day["images"] = {"hero": {"photo_id": day["location"]}}
    service.enrich_trip_with_images(trip, changed_day_indexes={0, 1, 2, 3})
    assert all("images" not in day for day in trip["days"][:4])
    assert trip["days"][4]["images"]["hero"]["photo_id"] == "Place 4"
    assert service.client.search_photo.call_count == images.MAX_IMAGE_REQUESTS


def test_provider_timeout_stops_future_requests_without_logging_query(monkeypatch, caplog):
    client = PexelsClient()
    client.api_key = "secret"
    client.unavailable = False
    request = httpx.Request("GET", "https://api.pexels.com/v1/search?query=private")
    mocked = Mock()
    mocked.__enter__ = Mock(return_value=mocked)
    mocked.__exit__ = Mock(return_value=False)
    mocked.get.side_effect = httpx.ReadTimeout("private", request=request)
    factory = Mock(return_value=mocked)
    monkeypatch.setattr(httpx, "Client", factory)
    assert client.search_photo("private") is None
    assert client.unavailable
    assert factory.call_args.kwargs["timeout"].read == 2.0
    assert "private" not in caplog.text
