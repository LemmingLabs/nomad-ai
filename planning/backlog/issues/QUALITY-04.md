## Context

The form currently shows dollar ranges even though the trip contract only carries qualitative `low`, `medium`, and `high` preferences. The backend uses these levels to guide AI output and catalogue price-level matching; it does not calculate a trip total or a per-traveler estimate.

## Goal

Explain what the budget choices mean without presenting unsupported currency or trip-cost estimates.

## Acceptance criteria

- Budget tiers do not show ungrounded currency amounts.
- The form explains that tiers are relative price-level preferences, not a currency amount, per-traveler estimate, or trip total.
- The selected preference remains available to generation and is shown with a human-readable label in the trip summary.
- If numeric budget estimates are added later, their currency, per-person/group scope, and included costs are explicit and supported by the request contract.
- The copy does not claim price accuracy that the current development app cannot support.

## Verification

Review the form and generated trip summary. Confirm the submitted preference remains compatible with the current API contract and no unsupported amount is implied.
