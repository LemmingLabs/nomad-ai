## Context

Budget tiers display dollar amounts, but the form does not define the currency, whether the amount is per traveler or group total, or which trip costs the estimate covers.

## Goal

Explain what budget choices mean so travelers can provide useful constraints and interpret the generated plan consistently.

## Acceptance criteria

- The UI states the currency used by the displayed ranges.
- The UI states whether the range is per traveler or total for the trip and its party.
- The UI explains whether the range is a planning preference or an estimated trip cost, including any major exclusions.
- The selected budget meaning is available to generation and visible in an appropriate trip summary.
- The copy does not claim price accuracy that the current development app cannot support.

## Verification

Review the form and generated trip summary for a solo traveler and a group. Confirm the submitted budget constraint remains compatible with the current API contract.
