# Destination and route quality expansion

This is planned work, not a description of shipped coverage. The current application plans Kyrgyzstan trips and has country specific assumptions in prompts, fallback data, catalog enrichment, and the business panel.

## Phase 1: define the destination contract

Choose a small initial set of countries based on provider coverage and available route data. Give each country a stable code and display name. Add explicit country and destination fields to generation requests, trip persistence, API responses, and chat context. Define currency, locale, timezone, and cross border behavior. Migrate existing trips to Kyrgyzstan without rewriting their itineraries. Keep old clients compatible during the transition.

## Phase 2: make planning country aware

Replace hardcoded supported cities and Kyrgyzstan wording in initial and continuation prompts with destination scoped data. Make city normalization, candidate search, catalog enrichment, routing, images, and fallback behavior country aware. Validate that route stops belong to the selected destination and that travel time fits each day. Return an explicit error or clearly marked draft when evidence is insufficient. Cover initial generation, chat edits, guest sync, and historical trips in tests.

## Phase 3: build trusted route knowledge

Investigate official tourism datasets, parks and trail authorities, open mapping data, public guide contributions, and partner submissions. For each source record the URL, owner, license, permitted reuse, last checked date, area, season, access requirements, and confidence. Obtain permission for guide owned routes. Do not equate public visibility with a right to copy or republish. Start with a small reviewed set of routes and compare generated itineraries against it for geography, pace, accessibility, safety, and traveler interest.

## Phase 4: expose evidence in the product

Show selected country clearly in the generation form and saved trips. Distinguish verified route segments, community or partner recommendations, AI suggested stops, and sponsored places. Let users inspect sources where licensing permits. Add admin review for route updates and stale information, and monitor user corrections.

## Acceptance checks

- A traveler can select a supported country and generate, save, reopen, and edit a trip in that country.
- Existing Kyrgyzstan trips and guest sync continue to work.
- Every stop has a resolvable location or a clear unresolved state; route times and distances have a known provider or source.
- Sponsored matching and business location validation use country context.
- Curated route claims have documented provenance and rights to use the data.
