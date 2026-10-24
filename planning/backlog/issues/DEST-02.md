## Context

The traveler form currently has no country selector. A global free-text destination is not enough to scope provider searches or constrain generation. This issue follows the trip contract in DEST-01.

## Goal

Expose a curated list of enabled countries and destinations from the backend and let travelers choose an unambiguous destination before generating a trip.

## Scope

- Define a small catalogue response with stable IDs/country codes, display names, destination options, and availability state.
- Add an API endpoint to return enabled destinations; do not hard-code the same catalogue independently in backend and UI.
- Add country/destination selection and validation to the traveler generation form.
- Include the selected destination in the generation request and show it in the saved-trip context/header.
- Make empty, loading, API error, and no-enabled-destinations states usable; do not silently submit a different default when the chosen destination fails validation.
- Start with Kyrgyzstan and add a second country only when the team identifies it as an enabled pilot with sufficient data coverage.

## Acceptance criteria

- The form choices come from the backend enabled-destination response.
- A traveler can select an enabled destination and the generation request contains its stable identifier.
- Unsupported/disabled destination IDs cannot be submitted, and service errors are visible.
- Saved trip presentation identifies the country/destination after generation and reopening.
- The default/legacy user flow remains functional for existing clients as defined by DEST-01.

## Technical touchpoints

- `backend/app/api/v1/` and `backend/app/schemas/`
- `frontend/src/widgets/generate-trip-form/`
- `frontend/src/features/trip/generate-trip/`
- `frontend/src/entities/trip/model/types.ts`
- `frontend/src/widgets/trip-header/`

## Dependencies and research

- Blocked on DEST-01 contract decisions.
- The initial non-KG destination must be selected through a provider/data coverage review; do not add arbitrary countries solely to exercise the control.

## Out of scope

- Country-specific POI/routing behavior (GEO-01).
- Cross-border itinerary generation.

## Verification

Cover catalogue API behavior, form selection/validation, loading/error states, and saved-trip country display with focused backend and frontend checks.
