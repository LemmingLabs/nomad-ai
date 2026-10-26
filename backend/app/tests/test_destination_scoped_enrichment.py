from unittest.mock import Mock

import pytest

from app.services.catalog_service import CatalogService
from app.services.image_enrichment_service import ImageEnrichmentService
from app.services.place_candidate_service import PlaceCandidateService


def _google_place(place_id, name, country_code, *, location=None):
    return {
        "id": place_id,
        "displayName": {"text": name},
        "formattedAddress": name,
        "addressComponents": [
            {"shortText": country_code, "types": ["country"]},
        ],
        "location": (
            {"latitude": 42.87, "longitude": 74.58}
            if location is None
            else location
        ),
        "types": ["museum"],
        "rating": 4.5,
    }


def test_place_candidates_reject_other_countries_and_missing_coordinates():
    service = PlaceCandidateService(api_key="test-key")
    search = Mock(
        return_value=[
            _google_place("kg-place", "History Museum", "KG"),
            _google_place("kz-place", "History Museum KZ", "KZ"),
            _google_place("no-coordinates", "History Museum Unknown", "KG", location={}),
        ]
    )
    service._text_search = search

    candidates = service._retrieve_candidates(
        "Bishkek", ["culture"], 10, country_code="KG", country_name="Kyrgyzstan"
    )

    assert [candidate["place_id"] for candidate in candidates] == ["kg-place"]
    assert search.call_args.kwargs["country_code"] == "KG"
    assert "Kyrgyzstan" in search.call_args.args[0]


def test_catalog_does_not_attach_kg_records_to_other_country_itineraries():
    itinerary = {"days": [{"city": "Bishkek", "location": "Old Town"}]}

    result = CatalogService(db=object()).enrich_itinerary_with_catalog(
        itinerary, "medium", country_code="US"
    )

    assert result == itinerary
    assert result is not itinerary


def test_image_search_uses_country_context_without_kg_overrides():
    service = ImageEnrichmentService()
    day = {"city": "Washington", "location": "Ala-Too Square"}

    queries = service._build_search_queries(day, {}, "United States", "US")

    assert all("Kyrgyzstan" not in query for query in queries)
    assert all("United States" in query for query in queries)


@pytest.mark.asyncio
async def test_routing_rejects_geocodes_outside_selected_country():
    from unittest.mock import AsyncMock

    from app.services.routing_service import RoutingService

    client = AsyncMock()
    client.search_place.side_effect = [
        [{"name": "A", "lat": 42.87, "lon": 74.56, "country_code": "KZ"}],
        [{"name": "B", "lat": 42.88, "lon": 74.57, "country_code": "KG"}],
    ]
    service = RoutingService(client=client, country_code="KG")

    segments = await service.enrich_itinerary(["A", "B"])

    assert len(segments) == 1
    assert segments[0].status == "unavailable"
    client.get_route_info.assert_not_awaited()
    assert all(call.kwargs["country_code"] == "KG" for call in client.search_place.await_args_list)
