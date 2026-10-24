## Context

After OFFERS-01 confirms an accessible production provider, NomadAI needs a backend boundary that keeps credentials private and separates dynamic commercial offers from AI-generated itinerary data.

## Goal

Add a read-only offers service and API for the approved pilot provider, with normalized search inputs/results and clear freshness/error semantics.

## Scope

- Implement a provider adapter behind `backend/app/integrations/` and orchestration in a service layer; keep credentials server-side and feature-gate by environment/market.
- Normalize provider search inputs and results for supported flight and/or stay searches while retaining provider IDs, deeplinks, currency, total amount, conditions, and `fetched_at`.
- Validate dates, destinations, traveler counts, and supported markets; use the selected country code but distinguish trip destination from flight origin.
- Apply timeout, quota/rate limiting, cache behavior only as permitted by the provider, and structured unavailable/no-results errors.
- Do not place dynamic prices in AI prompts or persist provider payloads beyond allowed retention.
- Provide configuration in `.env.example` without adding secrets.

## Acceptance criteria

- API returns only results from the selected approved provider and supported market.
- Response includes provider, fetch time, currency, total price, important conditions, availability status, and supplier handoff URL.
- Expired/stale data are never represented as freshly checked; provider errors and empty results have distinct response states.
- Provider tokens never reach the browser, logs, trip JSON, or source control.
- Disabled feature flag prevents calls and gives a clear unavailable response.
- Pricing is descriptive; no discount claim is made without provider-supplied comparable reference data.

## Technical touchpoints

- `backend/app/integrations/`
- `backend/app/services/`
- `backend/app/api/v1/` and schemas
- backend settings and `.env.example`
- focused provider boundary tests

## Dependencies and research

- Blocked on OFFERS-01 provider/access decision.
- Follow the chosen provider's rate-limit, caching, retention, attribution, and deeplink requirements.

## Out of scope

- UI (OFFERS-03).
- Booking, payment, cancellations, or price-alert subscriptions.
- Unapproved provider fallback that returns a different market's prices.

## Verification

Mock provider success, empty search, invalid request, timeout, quota exhaustion, expired result, and configuration-disabled behavior. Verify secrets and provider payloads are not leaked or over-persisted.
