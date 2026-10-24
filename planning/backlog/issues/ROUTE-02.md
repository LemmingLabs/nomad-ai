## Context

Current itinerary days render activities and place cards, but the plan does not consistently explain what to do at a location or whether a stop represents a short visit or half/full day. See `docs/architecture/ITINERARY_QUALITY.md`, `backend/app/schemas/`, `frontend/src/entities/trip/model/types.ts`, and `frontend/src/widgets/trip-day-card/`.

## Goal

Expand the day/stop contract and traveler UI so a trip explains activities, duration, practical details, and transitions at a useful level without breaking older saved trips.

## Scope

- Agree on a backward-compatible activity/stop shape: stop identity, duration, approximate time window, specific activities, and optional practical details.
- Update AI generation and continuation prompts to produce useful actions rather than only place names; model output remains a suggestion unless backed by evidence.
- Keep provider-sourced facts separate from generated narrative and attach source/status metadata when available.
- Update backend normalization/response schemas and frontend domain types together.
- Render daily schedule and stop details with explicit unknown/estimated labels; old itinerary objects with missing fields must continue to render.
- Ensure chat edits can change one day without erasing details on unchanged days.

## Acceptance criteria

- A generated day communicates what to do at each selected stop and an estimated visit duration or an explicit unknown state.
- Travel transitions, meals/rest, and optional alternatives can be represented without pretending to be confirmed bookings or opening times.
- Prompt-generated facts are not displayed as verified provider facts.
- Legacy saved trips and guest trips still render with graceful fallbacks.
- Chat edits preserve valid details in unchanged days and update changed-day data coherently.

## Technical touchpoints

- `backend/app/utils/prompt_builder.py`
- `backend/app/services/ai_service.py`, `trip_service.py`, `trip_message_service.py`
- `backend/app/schemas/trip_schema.py`
- `frontend/src/entities/trip/model/types.ts`
- `frontend/src/widgets/trip-day-card/`
- `frontend/src/widgets/trip-route-block/`

## Dependencies and research

- Depends on DEST-01 for country context.
- Use source decisions from ROUTE-01 where the UI presents externally sourced access, season, opening hours, or similar factual information.

## Out of scope

- A new provider ingestion pipeline (ROUTE-04).
- A live booking calendar or guaranteed schedule.

## Verification

Add focused contract and rendering checks for detailed new days, missing optional fields, legacy saved trips, and chat edits that touch one day only.
