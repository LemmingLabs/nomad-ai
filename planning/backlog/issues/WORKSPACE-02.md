## Context

`TripPage` holds message and itinerary overrides locally while its `tripId` changes. React can reuse the page component during sidebar navigation, and a pending request may finish after the traveler moves to another trip.

## Acceptance criteria

- Reproduce navigation between two distinct trips after editing the first, then isolate all displayed messages, itinerary and pending/error state by trip ID.
- A delayed success or error for trip A cannot update trip B's visible content or store entry; returning to A reflects its actual result.
- Preserve guest/local and signed-in behavior, query cache and sidebar data.

## Verification

Use two trip fixtures with different days and messages; cover navigation before and after an edit, delayed response, error, and switching back.
