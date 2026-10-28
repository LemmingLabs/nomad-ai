## Context

The empty chat rotates example requests as animated text, but the examples are not actionable. After an itinerary is generated, travelers rely on a blank free-form input to discover how to refine it.

## Goal

Make common trip refinements discoverable and easy to submit through the existing chat edit flow.

## Acceptance criteria

- Show a concise set of refinement actions in an appropriate chat state, including after an itinerary is available.
- Suggestions are relevant to the current itinerary where data allows and use plain language (for example, shorten long transfers or add a slower-paced day).
- Selecting an action submits its text through the existing `onSend` path; it does not bypass authentication, usage limits, loading, or error handling.
- Suggestions cannot be submitted while chat is disabled or an edit is pending, and provide visible keyboard focus and accessible names.
- The panel remains usable on mobile and does not crowd out the conversation or input.
- Empty-state animated examples remain non-interactive only if kept; they must not be announced as controls.

## Dependencies

- None.

## Verification

Check first-use, existing-conversation, pending, unauthenticated, limit-reached, and API-error states. Verify a selected suggestion appears as a user message and the updated itinerary follows the same flow as typed input.
