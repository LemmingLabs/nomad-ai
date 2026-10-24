## Context

NomadAI does not yet search live airfares or accommodation inventory. `docs/integrations/FLIGHTS_AND_STAYS.md` and `docs/research/DATA_SOURCES_AND_RIGHTS.md` identify candidate approaches, but production access, market coverage, API terms, and price display rules must be confirmed before implementation.

## Goal

Recommend one production-capable provider path for read-only flight and/or accommodation offers for a deliberately limited pilot market.

## Research scope

- Confirm markets/dates/passenger scenarios users need, including target routes reachable from the pilot destination.
- Compare available providers on production onboarding, legal entity/market eligibility, route/property coverage, live price/availability, fare/room conditions, deeplinks, commission, cost, quotas, caching, data retention, attribution, support, and test environment.
- Include direct airline/hotel inventory and affiliate/metasearch alternatives when available; document rejected candidates.
- Test sandbox or partner sample calls for representative searches. A sandbox result is not evidence of production access.
- Define what counts as a comparable price and which supplier fields must be shown before calling an offer discounted.
- Get written clarification for ambiguous contractual permissions and record any legal review needed.

## Deliverable

Update `docs/integrations/FLIGHTS_AND_STAYS.md` with a provider decision, supported pilot markets, API/contract references, offer freshness/display rules, costs/limits, fallback behavior, and unresolved risks. If production access is unavailable, recommend a narrower pilot or defer feature work.

## Acceptance criteria

- Provider has a plausible production onboarding path for the company's actual market.
- Coverage and price conditions were sampled for representative pilot routes/dates and accommodations.
- Redirect/affiliate and data display/cache terms are documented.
- Team agrees to a read-only, supplier-handoff MVP; no in-app ticket or hotel booking is implied.
- No credentials or personal data are committed in this issue or repository.

## Dependencies

- DEST-02 selects supported destinations.
- Use current primary provider documentation and signed partner terms, not search-engine summaries alone.

## Out of scope

- Building provider integrations before access and terms are confirmed.
- Promising lowest market price or user price alerts.
- Taking payment, issuing tickets, or managing refunds.

## Verification

Product/engineering review the comparison table and approve a provider plus a defined pilot scope before OFFERS-02 starts.
