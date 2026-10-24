# NomadAI Development Goals

**Status:** Product plan, not a description of fully implemented functionality.  
**Basis:** Repository review and current internal plans, October 24, 2026.

## Where We're Taking the Product

NomadAI should help travelers go from choosing a destination to having a clear, actionable travel plan: pick a country and places, see a day-by-day breakdown, understand travel between stops and constraints, and if desired, compare current offers for transport and accommodation.

## Current State (as of codebase)

- **Trip generation (Kyrgyzstan-focused):** The app generates day-by-day itineraries for Kyrgyzstan with a structured `itinerary_json`. Some flows use mock/fallback data if AI providers fail.
- **Chat editing:** Users can refine saved trips through a chat interface with context about the trip.
- **Saved trips and accounts:** Guest generation with account sync, saved trips.
- **Sponsored places:** Monetization layer for placing sponsored objects in itineraries.
- **Business/Admin panels:** Separate panel for partners/businesses and administrators.

## Goals for Development

1. **Multi-country support** — Extend beyond Kyrgyzstan. Add explicit country/destination selection, update data models, prompts, enrichment, and UI. Preserve backward compatibility for existing Kyrgyzstan trips.
2. **Improved route quality** — Make routes more meaningful and verifiable. Research and connect legally usable, attributed route data. Treat AI and third-party place data as suggestions until verified; do not label routes as "guide-verified" without evidence.
3. **Flights and stays** — Gradually integrate price offers for transport and accommodation (affiliate/provider model) without making hotel fields in the current route schema falsely imply booking integration.
4. **Partner model expansion** — Scale sponsored/partner placements to other countries with a safe moderation and billing model.
5. **Reliability and transparency** — Clearly distinguish real vs mock/fallback responses, improve error handling, document integration status.

## Constraints and Principles

- **Code-first:** Behavior is defined by code. Documentation reflects it or states what is proposed.
- **Safety:** Do not silently replace a failed provider response with a plausible itinerary in production — surface degraded/mock behavior clearly.
- **Legal and licensing:** For any third-party data (routes, POIs, maps), verify license terms before import/use.
- **Incremental rollout:** Add countries one by one after validating coverage and operational readiness. "All countries" is a direction, not a first-release commitment.
- **Preserve existing flows:** Guest generation, account sync, saved trips, chat edits, subscriptions, sponsored places, and business/admin workflows must be preserved during expansion.
