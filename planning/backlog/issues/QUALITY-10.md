## Context

The development mock itinerary currently uses Kyrgyzstan locations directly. If a non-Kyrgyzstan destination is selected and AI generation fails, the fallback could describe a trip in the wrong place.

## Goal

Ensure development fallback content is valid for the selected destination or is clearly identified as unavailable for that destination.

## Acceptance criteria

- The mock/fallback generation path receives the selected destination context.
- It does not return hard-coded Kyrgyzstan locations for another selected destination.
- If no safe mock content exists for a destination, the app shows a clear degraded/unavailable state rather than plausible but incorrect locations.
- Existing Kyrgyzstan development fallback behavior remains available and visibly marked as mock/degraded.
- The fallback remains covered by focused tests for Kyrgyzstan and at least one other supported destination or unsupported-destination case.

## Verification

Simulate AI failure for the current Kyrgyzstan destination and another supported destination. Confirm the resulting content and generation status are accurate.
