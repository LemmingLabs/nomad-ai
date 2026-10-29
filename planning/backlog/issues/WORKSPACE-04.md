## Context

Chat edits read an itinerary, perform AI/enrichment work and commit the result. Concurrent requests from separate tabs may merge from an older snapshot and overwrite a newer edit; this risk needs a deterministic reproduction.

## Acceptance criteria

- Reproduce overlapping edits and choose a documented concurrency strategy, such as an itinerary revision with conflict detection. Avoid holding a database lock across external provider calls.
- Never silently replace a newer itinerary with an older edit; return an actionable conflict and preserve the committed version and associated messages.
- Define retry/idempotency and usage accounting so a failed/conflicting request is not charged twice. Preserve ownership and guest/account boundaries.
- If persistence changes, add a new Alembic migration and update contracts and both consumers as needed.

## Verification

Use independent database sessions and controlled concurrent provider responses; cover conflict, retry, normal update, failure rollback and usage accounting.
