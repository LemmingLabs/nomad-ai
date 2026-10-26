# Data Sources, Licenses, and Access

**Checked:** October 26, 2026. This is a technical source review, not legal advice or permission to import data.

## ROUTE-01 Source Decision (2026-10-26)

**Research owner:** Zhanbolot Kydyraliev (GitHub assignee for [ROUTE-01](https://github.com/LemmingLabs/nomad-ai/issues/65)).

**Current supported destination:** Kyrgyzstan only. The backend destination registry currently enables `KG`; do not present another country as shipped.

**Candidate for the first non-KG pilot:** Almaty city and its nearby mountain routes in Kazakhstan (`KZ`), as a research candidate only. The official Kazakhstan tourism portal lists city attractions and nearby trekking destinations including Big Almaty Lake, Kok-Jailau, Charyn Canyon, Medeu, and Shymbulak. The Almaty tourism route catalogue exposes concrete trail samples. This is enough to justify further provider and operations review, but not enough to enable the destination or import its content.

### Source comparison

| Source and owner | Terms and commercial reuse | Attribution, storage, and withdrawal | Coverage and sample checked | Decision |
|---|---|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/copyright), maintained by the OpenStreetMap Foundation and volunteer contributors | The [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) permits copying, adapting, and commercial use subject to the license ([use-case guidance](https://wiki.openstreetmap.org/wiki/License/Use_Cases)). A derivative database may trigger share-alike duties; the boundary between a combined NomadAI fact store, generated text, and a produced work needs qualified review. The ODbL also says other rights may apply to database contents. | Show OpenStreetMap contributor credit and link to ODbL wherever its data is used. Store source object IDs, retrieval/check time, and license version if later approved. Object edits/deletions require a refresh and removal process; no source-side SLA was identified. Data is free to access, but self-hosting/refresh has infrastructure cost. OSM public [tile servers](https://operations.osmfoundation.org/policies/tiles/) are donation-funded and prohibit bulk/prefetch use; the [editing API](https://operations.osmfoundation.org/policies/api/) is not intended for read-only apps. Endpoint-specific quotas apply, so production access requires selecting a permitted provider or self-hosting. | Secondary OSM-derived pages identify [Big Almaty Lake, relation 3427772](https://mapcarta.com/Big_Almaty_Lake_R3427772) in the candidate KZ pilot and [Ala-Archa path, way 26137929](https://kg.geoview.info/osm_way_26137929%2C26137929w) in current KG coverage. Each page identifies the corresponding [OSM relation](https://www.openstreetmap.org/relation/3427772) or [OSM way](https://www.openstreetmap.org/way/26137929); the Ala-Archa page reports hiking/path and dirt-surface tags. These secondary records show place/path presence, not current access, permits, trail condition, duration, or safety. | **Conditional candidate, not approved for ingestion.** Ask counsel to assess ODbL implications for the intended product and decide whether a separate data boundary or attribution/offer mechanism is required. Never infer route verification from OSM presence. |
| [Visit Almaty mountain routes](https://nta.visitalmaty.kz/en/trails), a storefront using the Visit Almaty brand | The listing says routes are “from open data” but does not name the upstream dataset/license. The [Terms of Service (updated 2026-09-04)](https://nta.visitalmaty.kz/en/terms) say the platform is provided by ТОО «Turismo» (БИН 200140007319), while the Visit Almaty brand is licensed from ТОО «Бюро по туризму Алматы» (БИН 120440000454). The terms prohibit scraping at scale. They do not grant NomadAI commercial reuse of route facts or underlying records. User-posted content remains with its creator and is licensed to the platform for hosting/display there. | The public listing page has no published API or bulk-access quota, price, refresh schedule, or correction/removal SLA. The terms state no external reuse grant or separate cache/redistribution permission. They do not identify the upstream route-data owner. The operator lists `roorsayan@gmail.com`; the brand owner is separate from the platform operator. | Sampled NTA-105 (Medeu–Butakovsky Waterfall): 6.3 km, 780 m climb, 6 h 30 min; NTA-106 (Medeu–Butakovsky Pass): 8.9 km, 1,316 m climb, 14 h; NTA-217 (Alpiyskaya Roza–Big Almaty Gorge loop): 6.7 km, 420 m climb, 3 h. The page itself advises checking weather and the pass. The catalogue does not establish current closures, permits, or access conditions. | **Strong coverage lead, no reuse approval.** Ask the operator to identify each upstream dataset/rightsholder and provide written permission, attribution, API/bulk access, refresh, correction, and withdrawal terms; obtain rights from the upstream owner as needed. Do not scrape or copy user-posted content. |
| [Kazakhstan.travel Almaty guide](https://www.kazakhstan.travel/en/regions/almaty), national tourism portal | The sampled page displays “© 2026 Kazakhstan.travel. All rights reserved”; no reuse license or API terms were found in the reviewed page. | No reuse, caching, redistribution, API quota, or fee schedule identified in the reviewed page. Its page does not state a refresh cadence or removal channel for extracted facts. | Names Panfilov Park, Ascension Cathedral, Green Bazaar, Kok Tobe, Medeu, Shymbulak, Big Almaty Lake, Kok-Jailau, and Charyn Canyon. It provides destination discovery, not route geometry, operating conditions, or route facts. | **Reference/link-out only** unless the rights holder gives written permission or publishes applicable reuse terms. |
| [Google Maps Platform](https://cloud.google.com/maps-platform/terms), Google | Current terms grant use inside customer applications subject to payment and service-specific terms. They prohibit scraping/exporting Maps Content, using it outside the services, generally caching it, and creating content from it (including AI model use). | Keep results in the permitted Google surface and render required attribution. Do not persist Places/directions facts into NomadAI’s own route database or prompts. Service-specific pricing, quotas, and availability are account/product dependent; no company credentials or billing project were reviewed. Corrections/removals follow Google’s service processes, not a NomadAI-controlled data refresh. | The service can provide operational place/directions results, but this review did not test company credentials, Kazakhstan quotas, or a representative production response. It is not a reusable source for an independent route-knowledge corpus under the reviewed default terms. | **Runtime map/routing candidate only**, subject to account, pricing, product, and terms review. Not approved as a source for stored claims or AI-generated route knowledge. |
| Guide, community, or partner contributions | No specific contributor or dataset with a written grant was identified in the repository. A public post or volunteered GPX file does not itself establish permission to commercialize, adapt, or redistribute it. | Require a written contributor agreement defining commercial use, adaptations, attribution, source of the contributor’s rights, retrieval/check date, correction and withdrawal contact, and rights after withdrawal. Strip personal/location metadata not needed for the route. | No route contribution was imported or used as a sample. This path could supply the practical details missing from map data if guides or park authorities agree to review and license a small set. | **Promising manual-review path**, pending contributor and qualified reviewer agreements. |

### Coverage and quality sample

The candidate KZ page has real, named routes and includes distance, climb, time, grade, and distance from town for many entries. The selected examples show useful variation (6.3 km/6.5 h to 8.9 km/14 h) and missing fields on other catalogue entries. The national tourism portal independently lists several destinations in the same region. OSM-derived samples show a place relation near Big Almaty Lake and a mapped hiking path in Ala-Archa, Kyrgyzstan.

This is a coverage check only. It does not verify geometry end to end, route safety, trail surface along the full route, opening hours, seasonality, permits, current closures, transport, or whether the NTA catalogue's underlying records may be reused. A public Overpass sample query could not be completed because the public service was at capacity; no automated or bulk query was attempted. The sample should be rechecked with the source owner or a licensed provider before implementation.

### Decision and next steps

**No external source is approved for importing route/POI facts today.** Keep AI output and provider listings labelled as suggestions. For the first non-KG data pilot, investigate Almaty, Kazakhstan, but leave it disabled until the destination is approved and rights, operational coverage, and field accuracy are confirmed.

### Provenance review workflow

The application provides an admin-only source and fact register for future, individually reviewed content. Registering a source or claim does not publish it: both start pending. A source needs a documented rights basis, allowed use, attribution, geographic scope, freshness period, terms URL, and approval evidence before an admin can approve it. Editing approved source terms returns the source to pending review. Facts can be approved only against an approved source, within its country scope, with a source record ID or URL and a current check date.

Approved facts appear only while both fact and source remain approved and the fact is fresh. Withdrawal, rejection, source withdrawal, or expiry removes a claim from traveler output. Fact changes are recorded in admin audit history and return approved claims to pending review. Traveler output carries source name, link, attribution, check date, and a `reviewed` status; this records the source review workflow and does not imply that a guide verified a route.

Place facts use the provider and place ID (for example, `google_places:PLACE_ID`). Route facts use `COUNTRY:normalized-origin->normalized-destination`. No source records or factual claims were seeded or imported with this workflow. The source decisions above remain unchanged: no external source has approval for route or POI fact ingestion.

Admins must record and review actual source terms and evidence before adding facts. Provider search results and model-generated itinerary text remain suggestions and are not converted into approved knowledge automatically.

1. Ask the Visit Almaty storefront operator (ТОО «Turismo») and brand owner (ТОО «Бюро по туризму Алматы») to identify the NTA route dataset owner and provide source-by-source license or contract, commercial reuse, attribution, API/bulk access, caching, refresh, correction, and withdrawal terms. Request records for NTA-105, NTA-106, and NTA-217 as representative samples; ask the city Tourism Department or relevant park authority to validate operational facts separately.
2. Ask qualified counsel to review ODbL application to the planned use of OSM paths/POIs in a commercial itinerary and the distinction between displayed maps, stored facts, and generated summaries.
3. For any selected source, independently validate the sample's current access/seasonality/permit facts with the responsible park/operator or qualified local reviewer. Require review evidence before using a “reviewed” label.
4. If permission is unavailable or unresolved, start only with a small manually reviewed dataset whose contributors and fact-level rights are documented, or postpone the non-KG route-data pilot. Do not scrape guide sites or convert their narratives into NomadAI route records.

**Unresolved:** written permissions, counsel review, attribution placement for the chosen content, API/provider costs and limits, route-source refresh cadence, and the first KZ dataset's removal contact. This decision should be revisited when the destination pilot and operating owner are confirmed.

## Registry of Sources to Review

For each specific source before connecting/importing, record:

- **Name and URL**
- **License/terms of use** (link, type: ODbL, CC, proprietary, etc.)
- **Allowed use** (API vs bulk download, attribution required, commercial use allowed?)
- **Coverage** (countries/regions, POIs/routes/tracks)
- **Freshness/updates**
- **Restrictions** (rate limits, redistribution, caching)
- **Contact/notes**

## Additional candidates not assessed in ROUTE-01

The following sources remain unreviewed for this pilot; the table is a research queue, not an approval or a substitute for checking current terms.

| Source | Type | Notes |
|---|---|---|
| [OpenRouteService](https://maps.openrouteservice.org/) | Routing, isochrones | Has free/paid tiers, terms of use apply. |
| [GraphHopper](https://www.graphhopper.com/) | Routing | Check license/hosting options. |
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
