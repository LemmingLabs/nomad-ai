## Context

Several trip form selections expose their active state visually through `data-active` but do not announce the selected state to assistive technology. The trip-length stepper uses icon-only buttons without accessible names.

## Goal

Make all trip form selections and stepper actions understandable and operable with keyboard and assistive technology.

## Acceptance criteria

- Budget and travel style expose single-choice semantics and selected state.
- Interest chips expose toggle state and can be toggled using the keyboard.
- Decrease/increase trip-length controls have descriptive accessible names and announce the current value appropriately.
- Keyboard focus is visible, and selected/focus states are distinguishable without relying on color alone.
- Existing form validation and generated values are unchanged.

## Verification

Use keyboard-only navigation and an accessibility tree or screen reader to check budget, style, interests, trip length, custom interests, validation errors, and submit.
