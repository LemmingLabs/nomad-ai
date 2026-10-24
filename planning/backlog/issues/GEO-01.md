## Context

The current itinerary pipeline runs place-candidate lookup, catalog enrichment, routing, and image enrichment. Several stages contain Kyrgyzstan defaults or rely on city text without a country boundary. See `backend/app/services/trip_service.py`, `catalog_service.py`, `place_candidate_service.py`, `routing_service.py`, and provider integration clients.

## Goal

Make each enrichment stage consume the explicit trip country and avoid attaching a place, route, or image from the wrong country.

## Scope

- Trace country/destination context through candidate lookup, internal catalog selection, routing, and image enrichment.
- Replace the fixed Kyrgyzstan city normalization/default assumptions with destination-scoped configuration.
- Define provider query boundaries and ambiguity handling for cities/places with duplicate names.
- Validate returned place coordinates against the selected destination or its explicitly allowed itinerary area.
- Keep unresolved places visible as unresolved; do not synthesize a plausible location or route after provider failure.
- Expose provider/source and failure status needed by route provenance work.
- Keep Kyrgyzstan behavior and current provider attribution/retention requirements intact.

## Acceptance criteria

- Every enrichment call is scoped by a stable country/destination context.
- A same-named place from another country is rejected or disambiguated.
- Candidate/route results with missing or out-of-scope coordinates do not silently become the selected stop.
- Provider failures return explicit unavailable/unresolved status and do not create fabricated routes.
- Existing Kyrgyzstan enrichment and chat-edit refresh behavior remain functional.

## Technical touchpoints

- `backend/app/services/trip_service.py`
- `backend/app/services/catalog_service.py`
- `backend/app/services/place_candidate_service.py`
- `backend/app/services/routing_service.py`
- `backend/app/services/image_enrichment_service.py`
- `backend/app/integrations/google_maps_client.py`
- `backend/app/models/place.py`, `hotel.py`, and related schemas

## Dependencies and research

- Depends on DEST-01 for the canonical country context.
- Use only providers permitted for the use case. Confirm cross-country coverage and data storage/attribution rules before persistent caching.
- Non-KG production coverage depends on provider validation for the chosen pilot.

## Out of scope

- Business location forms and sponsored matching (GEO-02).
- Full curated route knowledge ingestion (ROUTE-01/04).

## Verification

Use mocked provider-boundary tests for at least Kyrgyzstan and one selected pilot country, including duplicate city names, wrong-country coordinates, empty responses, provider errors, and chat refresh.
