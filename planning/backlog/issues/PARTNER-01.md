## Context

The current sponsored-place form and location utilities assume Kyrgyzstan. Phase 2 makes the records and matching country-aware; this issue adds the rollout process needed to enable business partners market by market.

## Goal

Define and implement per-country partner enablement so businesses can submit and moderate locations only in markets with operational support.

## Scope

- Add a country/market readiness configuration and expose which markets accept partner submissions.
- Define required country-specific business details (address, contact format, supported language/currency as applicable) without a one-size-fits-all phone or payment rule.
- Add market-level onboarding/moderation guidance and admin visibility for country, region, verification status, and operating language.
- Ensure sponsored matching, impression and interaction analytics, and reporting remain country-scoped.
- Keep unsupported markets closed to public sponsored placement while allowing a clear draft/request-access state if product wants it.
- Document an operational checklist for partner support, advertising restrictions, payment/commission capability, privacy, and escalation ownership before enabling each market.

## Acceptance criteria

- Market enablement is explicit and can be changed without deployment of a new frontend country list.
- Business forms guide users according to enabled market configuration; backend rejects unsupported market submissions.
- Admin can moderate by country and see required location verification context.
- Current Kyrgyzstan businesses, approval state, analytics, and links remain valid.
- Sponsored placements are never matched across countries and remain visibly labeled.
- A new country cannot be opened until the documented operational and legal checklist is approved.

## Technical touchpoints

- `backend/app/models/business.py`, `sponsored_place.py`, country config, and migrations
- business/admin API schemas and services
- `businessPanel/src/features/business/` onboarding and location picker
- `businessPanel/src/features/admin/` moderation and analytics
- `docs/business/PARTNER_MODEL_EXPANSION.md`

## Dependencies and research

- Depends on GEO-02 for country-aware place schema/validation and DEST-02 for enabled destinations.
- Research local advertising and onboarding requirements for each proposed pilot country; do not assume affiliate offer approval implies sponsored-business eligibility.

## Out of scope

- A global self-serve ad marketplace, auction, or billing system.
- Activating every country by default.

## Verification

Cover unsupported-market rejection, enabled-market submission, KG migration, country-scoped moderation, analytics, and role/ownership controls.
