## Context

At the mobile breakpoint `ResizableLayout.module.scss` hides the itinerary pane. The focus and print actions are inside that pane, so a traveler may only see chat.

## Acceptance criteria

- Provide a discoverable, keyboard-accessible mobile switch between itinerary and chat with a visible selected state and meaningful labels.
- Both panes and itinerary actions are reachable for guest and signed-in trips; switching retains content and in-progress input.
- Maintain desktop resize and focus behavior, print disclosures, long text and loading/error/empty states.
- Test at narrow widths and 200% zoom, including keyboard and screen reader semantics.

## Verification

Add interaction coverage for switching both ways, guest and authenticated states, and preservation of draft input. Review a populated itinerary and print action on a phone viewport.
