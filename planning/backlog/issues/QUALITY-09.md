## Context

The traveler app uses shared SCSS design tokens and UI components. The business/admin app has a separate Tailwind-based shell and styling. The two surfaces may drift in typography, spacing, controls, focus, and empty states.

## Goal

Align the most visible interface patterns across the traveler and business/admin apps without coupling their feature architectures.

## Acceptance criteria

- Typography, spacing, button behavior, form fields, focus rings, and empty/error states are reviewed side by side.
- A small shared set of tokens or documented values is adopted where it reduces visible inconsistency.
- Existing feature-specific layouts and accessibility behavior are preserved.
- Shared patterns remain responsive in both applications.

## Verification

Compare representative home, form, dashboard, list-empty, and error states in both apps at desktop and mobile widths.
