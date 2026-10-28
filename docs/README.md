# NomadAI Documentation

This folder describes the current state of the product and the agreed development plan. Implemented features are separated from proposals and future work.

## Navigation

| Section | Documents |
|---|---|
| [Product](product/) | [Goals and Scope](product/PRODUCT_VISION.md); [Interactive Home Globe Plan](product/HOME_GLOBE_EXPERIENCE_PLAN.md) |
| [Roadmap](roadmap/) | [Destination Expansion and Route Quality](roadmap/EXPANSION_PLAN.md); [Epic order and implementation backlog](roadmap/IMPLEMENTATION_BACKLOG.md); [local issues and GitHub sync](../planning/backlog/README.md) |
| [Architecture](architecture/) | [Meaningful and Verifiable Itinerary](architecture/ITINERARY_QUALITY.md) |
| [Reviews](reviews/) | [Product quality audit (2026-10-27)](reviews/PRODUCT_QUALITY_AUDIT_2026-10-27.md); [Product feature audit (2026-10-29)](reviews/PRODUCT_FEATURE_AUDIT_2026-10-29.md) |
| [Integrations](integrations/) | [Flights, Stays, and Price Offers](integrations/FLIGHTS_AND_STAYS.md) |
| [Business Model](business/) | [International Partners](business/INTERNATIONAL_PARTNER_MODEL.md); [Current Sponsored System](business/MONETIZATION_AND_SPONSORED_SYSTEM.md) |
| [Research](research/) | [Data Sources, Licenses, and Access](research/DATA_SOURCES_AND_RIGHTS.md) |
| [Operations](operations/) | [Local Startup Audit](operations/RESTART_AUDIT.md) |
| [Assets](assets/) | [Home globe image sources and credits](assets/HOME_GLOBE_ASSETS.md); screenshots and certificate |

## How to Read This Plan

- **Now** — behavior observed in the codebase as of the document date.
- **Proposed** — target behavior; this is not a claim of a ready feature.
- Stages progress from a safe data model and route quality to external pricing and scaling of the partner network.
- Countries are added gradually after verifying data coverage, providers, and operational support. The phrase "all countries" reflects a development direction, not a promise of equal quality in every country from the first release.

## Maintaining Documents

When changing APIs, trip schema, data sources, or integration status, update the corresponding document and links in this table of contents. Do not commit keys or user `.env` files to documentation.
