## Context

The trip creation form presents destination, budget, duration, interests, style, and a free-form brief as a long vertical stack. The form may feel lengthy, especially on mobile.

## Goal

Reduce the effort needed to create a useful first itinerary while retaining the existing planning controls.

## Acceptance criteria

- The required choices are easy to complete without excessive scrolling on a phone.
- Optional interests and free-form preferences can be skipped without implying they are required.
- The form clearly communicates progress or grouping if multiple steps are introduced.
- Previously entered values survive navigation between steps and validation errors.
- Existing submit, loading, limit, and destination failure states remain clear.

## Dependencies

- QUALITY-03 defines accessible control behavior.
- QUALITY-04 defines budget meaning and copy.

## Verification

Compare the current and revised flow on phone and desktop using a typical traveler task. Confirm a valid trip can be generated with only required choices.
