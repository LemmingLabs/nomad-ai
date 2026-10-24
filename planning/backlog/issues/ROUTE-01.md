## Context

`docs/research/DATA_SOURCES_AND_RIGHTS.md` lists source candidates, but it is not yet an approval to ingest any source. Source coverage and reuse conditions vary by country and by data type (map, POI, route narrative, opening hours, image).

## Goal

Choose a defensible initial set of route/POI sources for the selected pilot destination(s), with documented coverage, rights, refresh needs, and operational gaps.

## Research scope

- Select one candidate non-KG pilot only after Phase 1 confirms a supported destination request path.
- Compare official tourism/parks sources, appropriately licensed open data, community/guide contributions with permission, and commercial APIs.
- For each source, check owner, exact license/contract, commercial reuse, derivative database and ShareAlike duties, attribution placement, caching/retention, coverage, language, update cadence, cost, rate limits, and removal process.
- Sample real target places/routes and measure whether the source provides the facts the itinerary needs: coordinates, access, seasonality, duration, surface/grade, permits, and closure status.
- Ask for provider clarification or legal review where terms are ambiguous; public availability alone is not reuse permission.
- Record rejected sources and reasons so the team does not repeat the research.

## Deliverable

Update `docs/research/DATA_SOURCES_AND_RIGHTS.md` with a source decision table and a recommendation for the first pilot. Include evidence links, date checked, named owner, and unresolved legal/provider questions. If no source meets the bar, explicitly recommend a narrow manually reviewed dataset or postponing the pilot rather than scraping.

## Acceptance criteria

- At least one candidate has specific written terms reviewed for the intended NomadAI commercial use, or the issue documents why no source is currently approved.
- The selected data scope and attribution behavior are explicit.
- The source's real coverage has been checked on a sample of actual routes/places in the pilot destination.
- Storage, refresh, and removal rules are clear enough to implement safely.
- No third-party content has been imported as part of this research issue.

## Dependencies

- DEST-02 identifies the destinations in scope.
- Use official primary sources for license/API claims; involve counsel for unclear commercial or database-rights questions.

## Out of scope

- Building a bulk scraper or importing guide-owned routes.
- Claiming a route is verified based on AI output or a provider listing.

## Verification

Review the updated source register with engineering and product; capture any permissions or correspondence in the approved company source of record rather than committing private credentials or contracts to the repository.
