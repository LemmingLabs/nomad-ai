## Context

Selecting a destination at generation time is incomplete unless the same context survives persistence, AI continuation, edits, and guest-to-account transfer. The current lifecycle crosses `trip_service`, `trip_message_service`, `guest_sync_service`, and frontend bootstrap/sync code.

## Goal

Carry the country and destination consistently through initial generation, AI prompt construction, chat edits, saved trips, and guest sync.

## Scope

- Pass the persisted destination to initial and continuation prompt builders; remove assumptions that the model may choose a different country.
- Ensure chat edits retain or intentionally update destination context and validate any requested destination change.
- Include destination context in guest payloads and authenticated guest-sync persistence.
- Preserve destination when listing, opening, exporting, and updating saved trips.
- Define behavior for historical guest payloads without country fields.
- Return explicit errors or a clearly marked draft if the selected country cannot be served; no silent switch to a different country.

## Acceptance criteria

- Generated trip, prompt context, saved record, chat response, and guest-synced record all agree on one destination.
- Editing a trip does not drop country context or move stops to an unrelated country.
- Legacy guest trips without destination context are migrated to the documented Kyrgyzstan default.
- Guest generation, account sync, reopen, chat edit, and export continue to work for Kyrgyzstan.
- Unsupported coverage is surfaced without presenting a plausible unrelated itinerary as a successful result.

## Technical touchpoints

- `backend/app/services/trip_service.py`
- `backend/app/services/trip_message_service.py`
- `backend/app/services/guest_sync_service.py`
- `backend/app/utils/prompt_builder.py`
- `frontend/src/app/providers/AppBootstrap.tsx`
- `frontend/src/features/trip/` guest sync and chat edit flows

## Dependencies

- DEST-01 and DEST-02.

## Out of scope

- Provider-specific country coverage (GEO-01).
- New route evidence or itinerary scheduling fields (Phase 3).

## Verification

Add focused tests for initial prompts, chat edits, guest transfer, legacy guest payloads, and destination persistence. Verify unchanged days and trip identity remain intact during chat edits.
