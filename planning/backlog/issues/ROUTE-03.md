## Context

The backend currently falls back to `build_mock_itinerary` if AI generation fails. Routing enrichment can also fail independently. A plausible fallback can be mistaken for a real provider result, especially after adding countries or harder-to-reach places.

## Goal

Validate that generated schedules fit the available day and make AI/provider failures and mock/degraded results explicit to the traveler.

## Scope

- Define generation status values for complete, partial/degraded, and failed outcomes, and return structured reasons that are safe for the UI.
- Do not silently replace provider failure with an unmarked plausible itinerary in production; keep development mocks explicitly identified.
- Validate duration budget, ordering, transition time, excessive backtracking, day boundaries, and missing critical location data.
- Use selected-country context to reject or flag stops and transitions outside the allowed destination area.
- Provide a partial draft only when its limitations are explicit; otherwise return a useful error instead of false certainty.
- Update chat-edit pipeline so refresh failures preserve unaffected days and visibly mark stale/uncomputed route details.

## Acceptance criteria

- AI generation failure is returned as a clear error or explicitly marked mock/degraded draft; it is never presented as successful live generation without a status.
- Route timing conflicts and missing route evidence are flagged in the response and UI.
- Unsupported/high-risk remote routes are not converted into precise directions without source evidence.
- Provider failure does not erase a valid unaffected day during a chat edit.
- Guest and authenticated flows show consistent degraded states.

## Technical touchpoints

- `backend/app/services/trip_service.py` and `trip_message_service.py`
- `backend/app/services/routing_service.py`
- `backend/app/schemas/trip.py` and response models
- `frontend/src/entities/trip/model/types.ts`
- `frontend/src/pages/trip/`, day cards, route blocks, and chat panel

## Dependencies and research

- Depends on DEST-01 for destination boundaries and ROUTE-02 for duration fields.
- Decide which route constraints can be checked from current data and label heuristics as warnings rather than guarantees.

## Out of scope

- Making route directions guide-verified.
- Solving every local safety or emergency-information problem.

## Verification

Cover AI timeout/failure, routing timeout, partial generation, mock mode, infeasible schedule, out-of-country stop, and chat edit refresh failure at provider boundaries and in the traveler UI.
