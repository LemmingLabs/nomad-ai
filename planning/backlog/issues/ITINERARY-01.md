## Context

The itinerary has day links and textual transfers, but no overview of how day locations relate spatially. A place candidate may include coordinates; coordinates and route data can also be missing or stale.

## Acceptance criteria

- Provide an optional, responsive overview using only available, valid coordinates and an equivalent ordered text list. Select a day to reach its existing detail.
- Clearly label locations as suggested and connectors as schematic; do not imply a straight line is a verified driving route. Show missing/stale locations and routes without fabricating them.
- Provide loading, no-data, partial-data, offline/provider-failure and keyboard-accessible states. Keep printing and itinerary use independent of a map.
- Before adding a map library, tiles or geometry, document source terms, attribution, coverage, network/privacy behavior and costs. No provider contract or new backend is required for a first text/schematic version.

## Verification

Test a multi-day itinerary with complete, missing, duplicate and invalid coordinates and unavailable routes. Review desktop/mobile and keyboard navigation.
