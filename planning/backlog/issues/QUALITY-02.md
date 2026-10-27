## Context

Guest travelers currently receive sign-in guidance inside the chat panel and another sign-in prompt directly below it on the trip page.

## Goal

Give a guest one clear sign-in action that explains how signing in affects the current trip.

## Acceptance criteria

- The guest trip page shows one sign-in prompt for the disabled chat.
- The prompt explains that signing in allows chat edits and syncs the guest trip to the account.
- The guest itinerary remains available through the sign-in flow and is synced according to the existing behavior.
- Authenticated chat and error/limit notices continue to work as before.

## Verification

Walk through a guest generated trip, sign in from the prompt, and confirm the trip is retained. Check authenticated, chat-unavailable, and chat-limit states.
