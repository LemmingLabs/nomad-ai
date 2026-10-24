# International Partner Model

## Starting Point

Currently, sponsored offers and business cabinets are built around cities and places in Kyrgyzstan: a place has a city and coordinates, forms/validation restrict location to Kyrgyzstan borders, matching is based on the trip day, and moderation controls placement. This model needs to be extended to multiple countries without losing existing partners.

## Goal

Create a scalable partner model that works for different countries while keeping the current Kyrgyzstan logic intact. Key requirements:

- **Geographic flexibility:** Support countries beyond Kyrgyzstan. Replace hard "Kyrgyzstan only" constraints with country-level configuration.
- **Entity structure:** A place/business must be linked to a country (and optionally region/city). Coordinates remain, but validation uses country boundaries/config.
- **Matching:** Extend day/route-based matching to consider destination country/context. Keep backward compatibility with existing Kyrgyzstan data.
- **Moderation and cabinet:** Business panel must support multi-country partners. Need to consider different markets, languages, and moderation rules.
- **Monetization:** Sponsored placements must scale by market. Current cap (2 per trip) should be configurable or preserved with clear policy.

## Implementation Plan

### 1) Data Model
- Add `country_code` (ISO 3166-1 alpha-2 or similar) to relevant entities: `sponsored_places`, business profiles, places/catalog if used.
- Add country reference where places are tied to location. Migrate existing records to `KG`.
- Add country-level settings (boundaries, currency, supported, moderation policy).

### 2) API/Validation
- Replace Kyrgyzstan-only checks with country-aware validation. For partner onboarding/editing, validate against selected country's rules.
- Update business panel forms to select country/region/city from available lists.
- Keep existing Kyrgyzstan partners working without changes.

### 3) Generation & Matching
- When generating/matching sponsored places, filter by trip destination country(ies).
- Ensure injector logic is country-aware. Do not show KG-specific partners in other countries unless explicitly allowed.
- Preserve current behavior for Kyrgyzstan trips.

### 4) Migration
- Alembic migration to add `country_code` with default `KG`, backfill, add indexes.
- Update existing data and tests.
- Ensure backward compatibility in API responses.

## Open Questions
- How to define supported countries list (config vs DB)?
- Do we need per-country pricing/billing?
- How to handle multi-destination trips across countries?
- Legal/regional requirements for advertising by country?

**Note:** See `MONETIZATION_AND_SPONSORED_SYSTEM.md` for current implementation details (caps, timing of injection, media attachment). Those must be preserved during migration.
