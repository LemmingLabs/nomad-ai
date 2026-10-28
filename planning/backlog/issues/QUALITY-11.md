## Context

The itinerary is currently presented inside an interactive split-screen workspace. There is no print action or print layout, which makes the plan awkward to keep as a paper copy or browser-generated PDF for offline reference.

## Goal

Let travelers print or save a readable copy of the current itinerary using the browser's native print dialog.

## Acceptance criteria

- The itinerary has an accessible print action available when an itinerary exists.
- Print output includes the trip title and context, day headings, activities, route details when present, and relevant attributions.
- Estimate, degraded-generation, sponsored-placement, and source-review disclosures remain visible and legible.
- Chat, sidebar, jump controls, focus controls, and other interactive actions are excluded from print output.
- Printed pages avoid splitting a day heading from its first content where practical and work with long activity names and narrow paper sizes.
- Printing does not require a backend PDF service or claim that suggestions are verified logistics.

## Dependencies

- None.

## Verification

Use browser print preview with a normal and degraded itinerary, missing route data, sponsored content, and long day/activity text. Check desktop and narrow paper output, links/attributions, and keyboard access to the print action.
