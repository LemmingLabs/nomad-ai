# Flights and Stays: Price Offer Integration Plan

**Status:** Research plan. The current application has no full search or booking of tickets/hotels with dates and prices. Hotel fields in the route should not be taken as such an integration.

## Proposed User Scenario

1. User specifies departure/destination cities/airports, dates or date flexibility, passengers, and budget.
2. NomadAI gets offers from a contracted provider or affiliate API.
3. User sees comparable options (price, duration/route, conditions), can go to partner site for booking (affiliate link) or book directly.
4. Options are shown separately from the generated itinerary (or as suggestions) without breaking the itinerary structure.

## What Exists Today vs What’s Needed

**Today:**
- Itinerary contains place/stay-related fields in structure, but no real price search.
- Sponsored system exists for places, not for flights/hotels with live pricing.

**Needed:**
- Integration layer for flight/hotel providers (abstraction/interface).
- Search request/response models, caching, rate limits.
- Affiliate tracking if using partner programs.
- UI components to display offers.
- Clear separation: "offers" vs "itinerary".

## Candidate Approaches

- **Affiliate aggregators** (e.g. Aviasales/Travelpayouts, Skyscanner Travel APIs, Booking.com affiliate, etc.) — faster to start, commission-based, less control over booking.
- **Direct provider APIs** — more control, contracts required, more complex.
- **Hybrid** — different providers by region/country.

**Requirement:** Research actual availability and terms for target countries before integration.

## Architecture Ideas

- `backend/app/integrations/flights/` and `.../stays/` with provider interface.
- Service layer to normalize offers to common schema.
- Caching by search params (short TTL).
- Feature flag to enable/disable per environment.
- Do not store sensitive payment data — redirect to partner.

## Risks

- Legal/affiliate terms, price display requirements.
- API costs/rate limits.
- UX complexity (dates, passengers, baggage).
- Mixing with AI itinerary could confuse users.

## Next Steps

1. Collect provider options for first target countries (after multi-country expansion start).
2. Define minimal offer schema.
3. Prototype with affiliate links (read-only).
4. Add UI toggle/section separate from itinerary.
5. Document status in this doc and update README.
