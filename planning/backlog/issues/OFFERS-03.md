## Context

Offers need a traveler-facing experience that shows the price source and freshness honestly and hands the user to the supplier for booking. They must not be conflated with itinerary costs or sponsored place cards.

## Goal

Let travelers review read-only flight and stay offers from the approved backend API and continue to the supplier with accurate price/availability context.

## Scope

- Add a distinct offers section/workflow that asks for the inputs supported by the provider (dates, route, passengers/guests, rooms, budget/filters).
- Display total price, currency, relevant conditions, provider, last-checked time, and supplier handoff link.
- Show loading, empty, unsupported market, provider unavailable, and stale offer states.
- Refresh or revalidate before handoff if provider terms/API support it; otherwise warn that supplier price/availability can change.
- Track offer impressions/click-throughs as separate events from sponsored placement and trip-route analytics; minimize personal search data.
- Keep offers separate from AI-generated itinerary facts and never let the model invent/alter prices.

## Acceptance criteria

- User can search, compare, and open a supplier deeplink for supported offers.
- Every result displays source and retrieval time; price currency and key exclusions are visible.
- No-results/error/stale states do not leave a false current price on screen.
- A supplier change is explained, and the booking handoff remains external for the MVP.
- Offer click tracking is clearly named and not counted as a sponsored interaction.
- Existing guest and authenticated trip planning still work if offers are disabled or unavailable.

## Technical touchpoints

- `frontend/src/features/` and `frontend/src/entities/` offer API/domain layer
- `frontend/src/pages/trip/` or a clearly scoped trip planning section
- `backend/app/schemas/` offer response contract
- analytics storage/API only if required by the pilot measurement plan

## Dependencies and research

- Depends on OFFERS-02 API contract.
- Display copy must follow chosen provider's required attribution and price language.

## Out of scope

- Taking payment or booking inside NomadAI.
- Claiming the cheapest price in the market.

## Verification

Cover search form validation, offers, provider error/no results, stale prices, outbound deeplink behavior, and separation from sponsored analytics.
