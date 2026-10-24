# Implementation backlog

This backlog turns the product direction into four delivery phases. Each phase is represented in GitHub as a milestone and an `[Epic]` issue; the larger implementation issues are linked from that epic. The issue definitions in [`planning/backlog/`](../../planning/backlog/README.md) are the source of truth for issue context and can be synchronized with `scripts/sync-backlog-to-github.sh`.

## Recommended order

| Phase | Epic | Outcome | Depends on |
|---|---|---|---|
| 1 | Destination contract | Country selection flows through the API, trip persistence, prompts, saved trips, chat edits, and guest sync while Kyrgyzstan data stays intact. | Existing Kyrgyzstan behavior and database migrations |
| 2 | Country-aware data and partners | Place search, enrichment, routing, sponsored matching, and business moderation respect the selected country. | Phase 1 contract |
| 3 | Itinerary quality and trust | Days explain what to do and how long; routes are feasible; evidence, provenance, and degraded behavior are visible. | Phase 1 contract; Phase 2 provider/country context; source-rights review before imports |
| 4 | Offers and international scale | Read-only flight/stay offers and additional partner markets are added only where production access, economics, and operational readiness are confirmed. | Destination readiness; provider and legal research |

## Planning and delivery rules

- Treat each phase as a milestone and an epic issue. The epic tracks an outcome, dependencies, and its child issues; it should not duplicate implementation detail from those issues.
- Keep one issue large enough to deliver an end-to-end capability. Avoid cosmetic one-line work items. Split only when ownership, review, or a dependency creates a real boundary.
- Write the acceptance criteria before implementation. Include API and persistence contracts, affected consumers, migration/backward compatibility, error states, and focused verification where relevant.
- Record research outcomes in an issue comment and in the corresponding source/rights or integration document before choosing a provider or importing content.
- Do not infer country support from model output. Start with Kyrgyzstan as the compatibility baseline and add one pilot country only after coverage and operations are verified.
- Build and sync the local issue definitions before implementation begins; update both the issue and its local Markdown source when scope changes.

## First work to pick up

Start with **DEST-01** (destination contract and persistence migration), **DEST-02** (supported destination catalogue and traveler selection), and **DEST-03** (carry the selected country through generation, chat, saved trips, and guest sync). These establish the shared contract that later phases depend on. Work on source/provider discovery can proceed in parallel as a research issue, but do not import or present new-country content before the corresponding review is complete.

## Phase outcomes

1. **Destination contract:** stable country/destination identifiers, safe migration of existing trips, explicit supported destinations, and a complete traveler request path.
2. **Country-aware data and partners:** every lookup/match is scoped to the selected country; current businesses remain valid in Kyrgyzstan; unsupported coverage is explicit.
3. **Itinerary quality and trust:** useful day plans, realistic time/route checks, provenance labels, source attribution, and transparent provider/mock failures.
4. **Offers and scale:** live offers are timestamped and linked to suppliers; partner expansion is enabled per market with country-aware moderation and analytics.
