# Data Sources, Licenses, and Access

**Checked:** October 24, 2026. This is a primary technical review for selecting sources, not legal advice and not permission to import data.

## Registry of Sources to Review

For each specific source before connecting/importing, record:

- **Name and URL**
- **License/terms of use** (link, type: ODbL, CC, proprietary, etc.)
- **Allowed use** (API vs bulk download, attribution required, commercial use allowed?)
- **Coverage** (countries/regions, POIs/routes/tracks)
- **Freshness/updates**
- **Restrictions** (rate limits, redistribution, caching)
- **Contact/notes**

## Candidate Sources (to research)

| Source | Type | Notes |
|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/) | POIs, roads, routes | ODbL — attribution required, share-alike considerations for derived datasets. Check current practices. |
| [OpenRouteService](https://maps.openrouteservice.org/) | Routing, isochrones | Has free/paid tiers, terms of use apply. |
| [GraphHopper](https://www.graphhopper.com/) | Routing | Check license/hosting options. |
| [Overpass API](https://overpass-turbo.eu/) | OSM queries | OSM data under ODbL. |
| [Wikivoyage](https://www.wikivoyage.org/) | Travel guides | CC BY-SA — attribution required, share-alike. |
| [Wikidata](https://www.wikidata.org/) | Structured data | CC0 mostly, but linked content may have different licenses. |
| [Natural Earth](https://www.naturalearthdata.com/) | Boundaries/admin | Public domain. |
| [GeoNames](https://www.geonames.org/) | POIs | Check license per use. |
| [Transitland](https://www.transit.land/) | Public transit | Mixed licenses per feed. |

*This list is not exhaustive and not a recommendation to import all of them.*

## Principles

- **Verify before import:** Never bulk-import third-party data without checking license for the intended use (internal enrichment vs redistribution).
- **Attribution:** If required, implement attribution in UI where data is shown.
- **Respect terms:** Follow API terms (caching, rate limits, commercial restrictions).
- **AI suggestions ≠ verified:** Treat AI and third-party results as suggestions until validated.
- **No "guide-verified" without evidence:** Do not label routes as guide-verified without documented source/proof.
- **User data:** Respect privacy; don't send unnecessary user data to third-party APIs.

## Action Plan

1. For first target countries (from expansion plan), shortlist 1-2 sources with clear commercial/usage terms.
2. Create a license checklist per source and get approval if uncertain.
3. Design enrichment to be source-agnostic with attribution metadata.
4. Document decisions in this file.

## Legal Note
This document is technical guidance for the team, not legal advice. When in doubt, consult appropriate counsel.
