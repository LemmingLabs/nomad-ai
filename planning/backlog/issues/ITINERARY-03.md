## Context

Image enrichment can fall back to broad city or theme searches; a photo search result may not depict the exact stop. A failed image URL currently has no explicit day-hero recovery.

## Acceptance criteria

- Render a designed, readable fallback when an image is absent or fails to load, retaining day title, location and keyboard access.
- Label broadly sourced/unverified imagery as inspiration, retain photographer and source attribution where available, and avoid asserting a precise location without evidence.
- Preserve meaningful alt text and contrast on photos, with no broken image icon; ensure print and screen-reader output remain useful.
- Handle old saved itineraries with incomplete metadata without migration or broken layout.

## Verification

Test absent URL, failed image, missing attribution and broad search metadata; review a long day title and bright/dark photos on mobile and desktop.
