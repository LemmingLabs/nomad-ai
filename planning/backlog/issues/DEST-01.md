## Context

NomadAI persists trips in `backend/app/models/trip.py` with an `itinerary_json` field. Generation schemas, routes, prompts, chat edits, and guest sync currently lack one canonical country/destination contract. See `backend/AGENTS.md` and `docs/roadmap/EXPANSION_PLAN.md`.

## Goal

Define and persist a backwards-compatible trip destination contract so downstream backend and frontend work can rely on stable country and destination identifiers.

## Scope

- Define the minimum country/destination fields and normalization rules (stable country code, destination identifier/name, enabled state); document how multi-city and cross-border trips are represented.
- Add request/response schema support and persist the selected destination on trips with a safe default for existing Kyrgyzstan records.
- Add an Alembic migration; preserve historical itinerary JSON and saved-trip behavior.
- Keep requests from old clients that omit the new field mapped to the established Kyrgyzstan default during the compatibility window.
- Document API compatibility and country/destination validation errors.

## Acceptance criteria

- New and historical trip records can be represented with an explicit country code; historical records resolve to `KG` without itinerary rewrites.
- API schemas validate country/destination input and return the chosen context consistently.
- Invalid or disabled destination IDs return a clear validation error.
- Migration upgrades an existing database without data loss and is reversible where the schema permits.
- Existing generation contract remains usable when destination is omitted during the compatibility period.

## Technical touchpoints

- `backend/app/models/trip.py`
- `backend/app/schemas/trip.py`, `backend/app/schemas/trip_schema.py`
- `backend/app/api/v1/trips.py`
- `backend/app/services/trip_service.py`
- `backend/alembic/versions/`
- `frontend/src/entities/trip/model/types.ts`

## Out of scope

- Choosing every country to support.
- Broad provider or sponsored-place changes (Phase 2).
- Building the traveler destination selector (DEST-02).

## Verification

Add focused backend migration and API contract coverage for new, legacy, invalid, and disabled destinations. Confirm current Kyrgyzstan trip responses still validate in the frontend contract.
