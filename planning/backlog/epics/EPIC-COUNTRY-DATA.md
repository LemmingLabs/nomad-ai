## Outcome

Every location lookup, enrichment step, route estimate, sponsored match, and business location review is scoped to the trip's country. The existing Kyrgyzstan trip and partner workflows remain valid.

## Why this phase follows the destination contract

The current country assumptions exist in backend prompts and defaults, catalog/place enrichment, routing, and the business panel. These services need one canonical destination context from Phase 1; otherwise different parts of one trip can silently resolve to different countries.

## Completion means

- Place candidates and internal catalog entries are resolved in the selected country or explicitly left unresolved.
- Routing does not accept a same-named place from another country.
- Sponsored recommendations match country and geography, and business/admin workflows can review locations in enabled countries.
- Unsupported provider coverage is surfaced clearly instead of being filled with plausible unrelated data.

## Guardrails

- Preserve approved status and visible sponsored labels.
- Keep provider terms and storage policies attached to the source decision.
- Roll out one reviewed pilot country at a time; do not expand the list without measured provider and operational readiness.
