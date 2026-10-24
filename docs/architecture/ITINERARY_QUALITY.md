# Quality and Detailed Travel Plan

**Status:** Target model. Current API and `itinerary_json` structure already contain days, activities, places, and route info, but this document proposes expanding them to a meaningful daily schedule.

## What the Traveler Should Understand

For each day and stop, the following should be clear:

- **Purpose of the day:** Theme/goal (arrival, sightseeing, rest, transfer).
- **Timing:** Start/end times or approximate intervals for key activities.
- **Places:** Name, description, location, why it's included.
- **Route/movement:** How to move between points (transport type, approximate time/distance), with reasonable logistics.
- **Meals/rest:** Where/when reasonable, or marked as flexible.
- **Pragmatic details:** Opening hours, tickets/reservations if relevant, weather/season notes, budget estimates.
- **Alternatives:** Options in case of bad weather/time pressure.

## Current State vs Target

**Current (from code):**
- Days with activities/places, basic route info exists.
- Generation is Kyrgyzstan-focused with prompts and fallback data.
- Quality varies; some places may be generic.

**Target:**
- Coherent daily schedule with logical order (geographic/logical grouping).
- Realistic timing considering travel and breaks.
- Verifiable places where possible, with sources/attribution.
- Graceful degradation with clear notes.

## Improvement Directions

1. **Structure:** Enrich `itinerary_json` schema (times, duration, transport, coordinates, type: activity/meal/transfer/rest). Keep backward compatible.
2. **Route logic:** Better clustering by location, minimize backtracking, consider opening hours.
3. **Data quality:** Prefer verifiable POIs; mark unverified suggestions. Research legally usable route/POI sources (see `research/DATA_SOURCES_AND_RIGHTS.md`).
4. **Prompting:** Make prompts country-aware, require realistic schedules, ask for justification.
5. **Validation:** Post-generation checks (timing conflicts, travel feasibility, missing info).
6. **Attribution:** If using third-party data, show attribution where required.

## Principles

- **Suggestions until verified:** AI output and third-party place results are suggestions until validated.
- **No false claims:** Never label a route as "guide-verified" without evidence.
- **Transparency:** If using mock/fallback data, indicate it.
- **Pragmatic:** Better a shorter realistic plan than an unrealistic packed one.

## Related Docs
- [Expansion Plan](../roadmap/EXPANSION_PLAN.md)
- [Data Sources and Rights](../research/DATA_SOURCES_AND_RIGHTS.md)
