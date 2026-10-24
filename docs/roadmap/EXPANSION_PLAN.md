# Destination and Route Quality Expansion

This is planned work, not a description of shipped coverage. The current application plans Kyrgyzstan trips and has country-specific assumptions in prompts, fallback data, catalog enrichment, and the business panel.

## Phase 1: Define the Destination Contract

Choose a small initial set of countries based on provider coverage and available route data. Give each country a stable code and display name. Add explicit country and destination fields to generation requests, trip persistence, API responses, and chat context. Define currency, locale, timezone, and cross-border behavior. Migrate existing trips to Kyrgyzstan without rewriting their itineraries. Keep old clients compatible during the transition.

**Key tasks:**
- [ ] Define country registry (code, name, supported, config)
- [ ] Extend request/response schemas
- [ ] DB migration to add country fields with defaults
- [ ] Update prompts to be country-aware
- [ ] UI: country/destination selection

## Phase 2: Extend Data, Enrichment, and Matching

Make enrichment and sponsored matching country-aware. Replace Kyrgyzstan-only validations with country-aware rules. Update fallback data structure to be country-keyed. Research and connect at least one legally usable route/POI source per initial country (or a cross-country source) following license checks.

**Key tasks:**
- [ ] Country-keyed fallback catalogs
- [ ] Country-aware sponsored injection/matching
- [ ] License review for chosen sources
- [ ] Enrichment pipeline updates
- [ ] Tests for multi-country cases

## Phase 3: Improve Route Quality

Implement the target itinerary model from `architecture/ITINERARY_QUALITY.md`: better timing, travel logic, clustering, validation. Mark suggestions vs verified. Add attribution where required. Improve error handling to not silently substitute plausible itineraries.

**Key tasks:**
- [ ] Enrich itinerary schema (times, transport, types)
- [ ] Route feasibility checks
- [ ] Suggestion/verification flags
- [ ] Attribution display
- [ ] Degraded mode UI indicators

## Phase 4: Flights, Stays, and Partner Scaling

Add read-only price offers for flights/stays (affiliate) separated from itinerary. Scale partner model per `business/INTERNATIONAL_PARTNER_MODEL.md`. Expand to more countries as coverage improves.

**Key tasks:**
- [ ] Offer integration abstraction
- [ ] Affiliate flows
- [ ] Multi-country business panel
- [ ] Per-country policies/moderation
- [ ] Expand country list

## Success Criteria
- Existing Kyrgyzstan trips continue to work unchanged.
- New country trips generate with country-appropriate data.
- Routes are more realistic and clearly marked as suggestions when unverified.
- No silent replacement of failed AI responses with plausible itineraries.
- Legal/licensing compliance for any imported data.

## Dependencies
- Provider coverage for target countries
- Route/POI data with acceptable licenses
- Operational support for new markets
- Partner onboarding capacity
