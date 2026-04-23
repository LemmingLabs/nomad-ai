# NomadAI — Monetization & Sponsored System

Production-level technical documentation for the **sponsored places monetization layer** in **NomadAI (AI Trip Planner)**.

This document targets:
- Backend engineers (data model, services, API contracts)
- Frontend engineers (JSON payload shape, interaction logging)
- Hackathon reviewers (product fit, safety controls, measurable impact)

---

## 1. Overview

NomadAI monetizes trip planning through **native sponsored recommendations** that are embedded into the trip itinerary as part of the user experience.

### Why monetization exists
- Trip planning surfaces high-intent users (they are actively choosing where to eat / what to do / where to stay).
- Businesses can promote relevant places at the exact moment the user is planning or consuming an itinerary.

### How monetization is embedded into the product
- Sponsored content is injected into each itinerary day as `day.sponsored`.
- The injection is limited to **max 1 sponsored recommendation per day** and only from **approved + active** sponsored places.

### Why this is “native advertising” (not banners)
- Sponsored places are delivered as a **place recommendation object** inside the itinerary day data model.
- The UI renders it like a normal recommendation card with a small badge (e.g. `"Partner Pick"`), rather than a separate ad unit.
- The same UX primitives apply: title, description, images, CTA, contact, website.

---

## 2. Architecture

### High-level generation flow

1) AI generates trip draft  
2) Google Places enriches real locations (place candidates)  
3) Catalog enrichment runs (internal content layer)  
4) Routing enrichment runs (distance/time between days)  
5) Images are added (Pexels)  
6) **Trip is persisted**  
7) **SponsoredInjectionService injects sponsored places and logs impressions**  
8) Updated trip is returned to frontend

### Where injection happens
- Injection is performed in the trip generation pipeline **after the trip is created** (so `trip_id` exists).
- The itinerary JSON stored in the `trips` table is updated after injection.

### Where analytics is logged
- **Impressions** are written during injection (when a sponsored place is attached to a day).
- **Interactions** are written when the frontend calls `POST /api/v1/sponsored/interactions`.

---

## 3. Data Models

Below are the core tables used by the sponsored monetization system.

### SponsoredPlace (`sponsored_places`)
Represents a business-controlled sponsored recommendation that can be injected into itineraries.

Key fields:
- `id` (int, PK)
- `business_id` (int, FK → `businesses.id`)
- `title` (string)
- `description` (text)
- `city` (string)
- `lat` (float)
- `lng` (float)
- `google_place_id` (string, nullable)
- `address` (string)
- `category` (string; examples: `restaurant`, `attraction`, `hotel`, `tour`)
- `cta_text` (string, nullable)
- `contact_phone` (string, nullable)
- `website_url` (string, nullable)
- `is_active` (bool)
- `is_approved` (bool)
- `created_at` (datetime)

Rules:
- Only `is_active = true` AND `is_approved = true` can be injected.
- New sponsored places created by a business user start with `is_approved = false`.

### Business (`businesses`)
Represents a business profile owned by a user with the `business` role.

Key fields:
- `id` (int, PK)
- `owner_id` (int, FK → `users.id`)
- `name` (string)
- `description` (text, nullable)
- `contact_phone` (string, nullable)
- `website_url` (string, nullable)
- `is_active` (bool)
- `created_at` (datetime)
- `updated_at` (datetime)

### BusinessMedia (`business_media`)
Business-owned media items for brand and sponsored place presentation.

Key fields:
- `id` (int, PK)
- `business_id` (int, FK → `businesses.id`)
- `type` (enum string): `image` | `logo`
- `url` (string)
- `created_at` (datetime)

Usage in sponsored injection:
- Only media items with `type = "image"` are currently included in `day.sponsored.place.images`.

### SponsoredImpression (`sponsored_impressions`)
Represents one “show” event when a sponsored place is injected into a specific day of a trip itinerary.

Key fields:
- `id` (int, PK)
- `trip_id` (int, FK → `trips.id`, nullable)
- `sponsored_place_id` (int, FK → `sponsored_places.id`)
- `business_id` (int, FK → `businesses.id`)
- `day_number` (int, nullable)
- `city` (string)
- `created_at` (datetime)

### SponsoredInteraction (`sponsored_interactions`)
Represents a user action taken on a sponsored recommendation.

Key fields:
- `id` (int, PK)
- `trip_id` (int, FK → `trips.id`, nullable)
- `sponsored_place_id` (int, FK → `sponsored_places.id`)
- `business_id` (int, FK → `businesses.id`)
- `interaction_type` (enum string):
  - `click`
  - `open_website`
  - `open_map`
  - `call`
  - `save`
- `created_at` (datetime)

### UserUsageStat (`user_usage_stats`)
Tracks user usage against subscription limits.

Key fields:
- `user_id` (int, FK → `users.id`)
- `date` (date)
- `trip_generations_count` (int)
- `chat_edits_count` (int)

---

## 4. Sponsored Injection Logic

### Goal
For each day in the itinerary, attach at most one sponsored recommendation:
- relevant to the day’s city and intent
- not spammy
- safe (approved + active)
- measurable (impression event logged)

### Eligibility constraints
A sponsored place is eligible only if:
- `is_active = true`
- `is_approved = true`
- city matches the day’s city (case-insensitive, trimmed)

### Category inference (from itinerary day intent)
The injection service inspects `day.activities[*].type`:
- If the day contains a `meal` activity → desired category intent is `"restaurant"`
- If the day contains a `sightseeing` activity → desired category intent is `"attraction"`
- Otherwise → no category intent is applied (fallback to city match only)

### Category matching (normalized + alias-aware)
The service normalizes categories (lowercase, whitespace normalization, underscores → spaces) and applies:
- Exact match boost
- Substring/alias match boost

Supported alias behavior includes:
- `restaurant` matches strings containing: `restaurants`, `cafe`, `coffee`, `coffee shop`, `bar`, `bakery`, `food`, `dining`
- `attraction` matches strings containing: `tourist attraction`, `activity`, `tour`, `museum`, `park`, `landmark`, `sightseeing`

### Proximity scoring (Haversine)
If the day has coordinates from Google Places (`day.place_candidate.lat/lng`), the service computes distance using the **Haversine formula**:
- closer sponsored places are preferred
- distance is used as a ranking signal (category relevance is still prioritized)

### Duplicate avoidance
Within a single itinerary injection run:
- A sponsored place ID is used at most once across all days.

### Best-candidate selection
Candidates are scored and the max score wins:
1) Category match score (exact/alias/none)
2) Distance (closer is better, if day coords exist)
3) Newer places as a deterministic tie-breaker (`id`)

---

## 5. API Endpoints

All endpoints are served under `/api/v1`.

### Auth & roles
Access is controlled via JWT auth and role-based dependencies:
- Business endpoints require a user with role `business`
- Admin endpoints require a user with role `admin`
- Sponsored interaction logging requires any authenticated user

---

### Business API (self-service)

#### Business profile
- `GET /api/v1/business/me` — get own business profile
- `POST /api/v1/business/me` — create own business profile (only if missing)
- `PATCH /api/v1/business/me` — update own business profile

#### Business media
- `GET /api/v1/business/me/media` — list own business media
- `POST /api/v1/business/me/media` — add media item (URL-based)
- `DELETE /api/v1/business/me/media/{media_id}` — delete own media item

#### Sponsored places (CRUD, scoped to own business)
- `GET /api/v1/business/me/sponsored-places` — list sponsored places owned by the business
- `POST /api/v1/business/me/sponsored-places` — create sponsored place (`is_approved = false`)
- `GET /api/v1/business/me/sponsored-places/{place_id}` — get one owned sponsored place
- `PATCH /api/v1/business/me/sponsored-places/{place_id}` — update one owned sponsored place
- `DELETE /api/v1/business/me/sponsored-places/{place_id}` — soft delete (sets `is_active = false`)

#### Business analytics
- `GET /api/v1/business/me/analytics/overview`
  - returns `impressions_count`, `interactions_count`, and `interactions_by_type`
- `GET /api/v1/business/me/analytics/sponsored-places/{place_id}`
  - same metrics, scoped to one sponsored place

---

### Admin API (moderation + read access)

#### Businesses
- `GET /api/v1/admin/businesses` — list all business profiles
- `GET /api/v1/admin/businesses/{business_id}` — get one business profile

#### Sponsored places
- `GET /api/v1/admin/sponsored-places`
  - filters:
    - `pending=true` (maps to `is_approved=false`)
    - `approved=true|false`
    - `active=true|false`
- `GET /api/v1/admin/sponsored-places/{place_id}` — get one sponsored place
- `PATCH /api/v1/admin/sponsored-places/{place_id}/approve` — set `is_approved=true`
- `PATCH /api/v1/admin/sponsored-places/{place_id}/reject` — set `is_approved=false` and `is_active=false`
- `PATCH /api/v1/admin/sponsored-places/{place_id}/activate` — set `is_active=true`
- `PATCH /api/v1/admin/sponsored-places/{place_id}/deactivate` — set `is_active=false`

#### Admin analytics
- `GET /api/v1/admin/analytics/businesses/{business_id}`
- `GET /api/v1/admin/analytics/sponsored-places/{place_id}`

Both endpoints return:
- `impressions_count`
- `interactions_count`
- `interactions_by_type`

---

### Interaction API (event logging)

#### Log interaction
- `POST /api/v1/sponsored/interactions`

Request body example:
```json
{
  "trip_id": 123,
  "sponsored_place_id": 45,
  "business_id": 9,
  "interaction_type": "open_website"
}
```

Validation rules:
- `interaction_type` is validated against the enum values listed in **SponsoredInteraction**
- the backend verifies that `business_id` matches the owner business of `sponsored_place_id`

---

## 6. Sponsored Block in Trip JSON

Sponsored content is attached per day as `day.sponsored`.

Example payload:
```json
{
  "is_sponsored": true,
  "badge": "Partner Pick",
  "place": {
    "id": 12,
    "business_id": 5,
    "title": "Authentic Kyrgyz Cuisine",
    "description": "Family-owned restaurant with traditional dishes.",
    "cta": "Get 10% discount",
    "images": [
      "https://cdn.example.com/photo-1.jpg",
      "https://cdn.example.com/photo-2.jpg"
    ],
    "contact": "+996700000000",
    "website": "https://example.com",
    "category": "restaurant",
    "address": "123 Main St, Bishkek"
  }
}
```

Field rationale (frontend usage):
- `is_sponsored`: enables consistent rendering rules and analytics gating
- `badge`: small label for trust and transparency (“Partner Pick”)
- `place.id`: sponsored place identifier (required for analytics and deep links)
- `place.business_id`: required for interaction logging ownership validation
- `place.title` / `place.description`: content for card UI
- `place.cta`: CTA label for a button or highlight strip
- `place.images`: gallery/hero images (from BusinessMedia of type `image`)
- `place.contact`: “Call” CTA
- `place.website`: “Open website” CTA
- `place.category`: used to theme icons/labels and to explain why it was recommended
- `place.address`: displayed in details UI and used for map actions

---

## 7. Analytics Flow

### 1) Impression logging (injection time)
When a sponsored place is injected into a day:
- a `SponsoredImpression` row is added to the DB session
- the event contains:
  - `trip_id`
  - `sponsored_place_id`
  - `business_id`
  - `day_number`
  - `city`

### 2) Interaction logging (user action time)
When a user interacts with the sponsored card:
- frontend sends `POST /api/v1/sponsored/interactions`
- backend creates a `SponsoredInteraction` row

### 3) Reporting outputs
Backend reporting endpoints return:
- `impressions_count` (count of `SponsoredImpression`)
- `interactions_count` (count of `SponsoredInteraction`)
- `interactions_by_type` (grouped counts by `interaction_type`)

CTR & engagement:
- The backend exposes counts required to compute CTR.
- CTR is computed as `interactions_count / impressions_count` at the consumer layer (dashboard/frontend).

---

## 8. Limits & Subscription

NomadAI enforces usage limits based on the user’s effective subscription plan.

### How limits work
- Each user has an effective plan (active subscription if present, otherwise the Free plan).
- Limits are enforced per UTC day via `UserUsageStat`.

Current enforced limits:
- Trip generation (`trip_limit_per_day`)
- AI chat edits (`chat_edit_limit_per_day`)

### Where access is checked
- Trip generation checks `LimitService.can_generate_trip(user_id)` before creating a trip.
- Usage increments are applied via `UsageService.increment_trip_generation(user_id)` after successful trip creation.

---

## 9. Future Improvements

### Ranking & performance optimization
- Rank sponsored places by historical CTR and engagement, using impressions + interactions as signals.
- Add decay/recency weighting so new campaigns can compete.

### Personalization
- User interest alignment (food/culture/nature) as an additional ranking factor.
- Contextual matching using itinerary text embeddings.

### Auction & pricing
- Auction-based sponsored placement with configurable bid strategies.
- Dynamic pricing per city/category and seasonal demand.

### Geo targeting
- Radius targeting around day coordinates (geo-fenced campaigns).
- City/region overrides (e.g., metro area mapping, tourism clusters).

### Advanced analytics
- Per-day breakdown reporting endpoints (day_number, city).
- Funnel metrics (impression → open → conversion) when conversion events exist.
- Fraud and anomaly detection (click spam, bot patterns).

