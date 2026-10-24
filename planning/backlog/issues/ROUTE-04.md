## Context

NomadAI needs route knowledge that can be attributed, reviewed, refreshed, and withdrawn. The existing place and route data structures are not a complete provenance/review lifecycle. ROUTE-01 must approve the source and usage terms before content is imported.

## Goal

Provide a minimal source and review model for selected route/POI facts so the API can distinguish AI suggestions, provider listings, partner/community submissions, and editorially reviewed facts.

## Scope

- Model source/provider identity, source URL or record ID, fact type, geographic scope, license/contract basis, attribution, retrieval/check date, freshness policy, and verification status.
- Associate provenance with individual claims/facts where mixed sources are possible; avoid one blanket `verified` boolean for an entire place.
- Add admin review/update/withdrawal workflow for the first approved dataset/source.
- Expose provenance fields through API contracts and display permitted attribution/status in the itinerary.
- Define what happens when a source expires, a place changes, a license is revoked, or an admin rejects an update.
- Keep AI suggestion and sponsored status separate from editorial review.

## Acceptance criteria

- A stop can have multiple independently sourced facts, each with source and check date.
- Admin can approve, reject, update, and withdraw reviewed facts, with an audit trail.
- The traveler UI accurately labels suggestion/provider/review/sponsored status and shows attribution when required.
- Stale or withdrawn content is hidden, downgraded, or flagged according to the documented freshness policy.
- No route is called guide-verified without documented qualified review evidence and scope.

## Technical touchpoints

- `backend/app/models/place.py`, `route_segment.py`, new provenance models and Alembic migration
- `backend/app/schemas/places.py`, `route_segment.py`
- Admin APIs and `businessPanel/src/features/admin/`
- `frontend/src/entities/trip/model/types.ts`
- `frontend/src/widgets/trip-day-card/` and attribution UI

## Dependencies and research

- Depends on ROUTE-01 approved source terms and ROUTE-02's claim-oriented itinerary contract.
- Avoid adding bulk external data persistence until the selected provider's terms allow it.

## Out of scope

- A global route encyclopedia at launch.
- Automatic AI approval of imported routes.

## Verification

Cover provenance persistence, moderation transitions, stale/withdrawn records, attribution output, legacy trips without provenance, and clear separation of sponsored and reviewed items.
