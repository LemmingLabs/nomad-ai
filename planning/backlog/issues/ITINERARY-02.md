## Context

Quality warnings already include day numbers but are listed at the top of `TripPreview`, separated from the day they describe.

## Acceptance criteria

- Group existing day-specific warnings with the corresponding day and offer a concise linked overview. Keep global, unmatched and route-degraded warnings visible.
- Preserve wording and uncertainty: warnings are prompts for review, not confirmed unsafe or safe routes. Do not infer missing logistics.
- Support keyboard navigation, long/multiple warnings, mobile layout and printing without duplicate or missing disclosures.

## Verification

Test warnings for multiple days, unknown day, no warnings, stale routes and print content; verify links land on the correct day.
