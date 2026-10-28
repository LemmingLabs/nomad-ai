## Context

Signed-in travelers can delete saved trips from the sidebar, but cannot rename one. The trip model already stores a title; the current trip API has no title-update operation.

## Goal

Allow a signed-in traveler to give an owned saved trip a memorable title.

## Acceptance criteria

- A rename action is discoverable from a saved-trip action menu or trip header without replacing the existing delete confirmation.
- The edit flow supports keyboard use, trims whitespace, rejects an empty title, and respects the model's maximum title length.
- The API updates a title only when the authenticated user owns the trip; missing or foreign trips return the established not-found behavior.
- On success, the sidebar and open trip header update without a full-page reload.
- Pending and failure states are clear, and a failed update leaves the prior title visible.
- Guest trip generation and account sync continue to work; do not expose an unauthenticated title-update route.
- No database schema migration is required.

## Dependencies

- None.

## Verification

Cover successful rename, blank/oversized input, API failure, missing trip, and attempts by another user to rename the trip. Confirm updated names survive reload and guest-to-account sync behavior is unchanged.
