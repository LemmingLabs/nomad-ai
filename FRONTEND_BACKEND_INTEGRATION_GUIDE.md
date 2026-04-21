# NomadAI — Frontend ↔ Backend Integration Guide

> Based on actual backend code. Last updated: April 2026.

---

## 1. Project Overview

NomadAI is an AI-powered trip planning backend. It generates multi-day travel itineraries for Kyrgyzstan, enriches them with real catalog data, routing info, and stock photos.

### Core Entities

| Entity | Description |
|---|---|
| `Trip` | Main entity. Contains itinerary JSON, budget, interests, travel style. Can be guest or user-owned. |
| `TripMessage` | Chat history between user and AI. Role: `user` or `assistant`. |
| `Hotel` | Catalog hotel entries matched by city and budget. |
| `Place` | Catalog places (restaurants, attractions) matched by city. |

### Generation Pipeline (in order)

```
POST /trips/generate
  → AI generation (Groq LLM)
  → city normalization
  → catalog enrichment  (hotel + recommended_places per day)
  → routing enrichment  (route_from_previous per day, via 2GIS)
  → image enrichment    (images.hero per day, via Pexels)
  → save to DB
```

All enrichment layers write directly into `itinerary_json`. The frontend receives the final enriched object.

---

## 2. Base API Info

```
Base URL: /api/v1
Content-Type: application/json
```

### Authentication

JWT Bearer token. Attach to every protected request:

```
Authorization: Bearer <access_token>
```

### Endpoint Auth Requirements

| Endpoint | Auth Required |
|---|---|
| `POST /auth/register` | No |
| `POST /auth/login` | No |
| `GET /auth/me` | Yes |
| `POST /trips/generate` | Optional (guest trips supported) |
| `GET /trips` | Yes |
| `GET /trips/{id}` | Yes |
| `DELETE /trips/{id}` | Yes |
| `POST /trips/sync-guest` | Yes |
| `POST /trips/{id}/messages` | Yes |
| `GET /trips/{id}/messages` | Yes |

---

## 3. Authentication Endpoints

### `POST /api/v1/auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-04-21T07:00:00Z"
}
```

**Errors:**
- `400` — email already registered

---

### `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1
}
```

**Errors:**
- `401` — Invalid credentials

---

### `GET /api/v1/auth/me`

No body. Returns current user.

**Response `200`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-04-21T07:00:00Z"
}
```

**Errors:**
- `401` — Missing or invalid token

---

## 4. Trip Endpoints

---

### `POST /api/v1/trips/generate`

**Purpose:** Generate a new AI trip. Auth is optional — works for guests too.

**Auth:** Optional

**Request Body:**

```json
{
  "budget": "medium",
  "days": 5,
  "interests": ["nature", "culture", "food"],
  "travel_style": "relaxed",
  "prompt": "We prefer less hiking. Romantic trip for two."
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `budget` | `string` | Yes | `"low"`, `"medium"`, `"high"` |
| `days` | `integer` | Yes | Number of trip days |
| `interests` | `string[]` | Yes | User interest tags |
| `travel_style` | `string` | Yes | E.g. `"relaxed"`, `"adventure"` |
| `prompt` | `string` | No | Free-text user preferences, max 1000 chars |

**Response `201`:** Full `TripResponse` (see Section 6)

**Errors:**
- `400` — Validation error
- `422` — Malformed request

---

### `GET /api/v1/trips`

**Purpose:** List all trips for the authenticated user. Includes `last_message_preview`.

**Auth:** Required

**Response `200`:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "5-Day Bishkek & Issyk-Kul Adventure",
      "days": 5,
      "created_at": "2026-04-20T10:00:00Z",
      "updated_at": "2026-04-21T07:30:00Z",
      "last_message_preview": "Can you add a rest day on Day 3?"
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | `int` | Trip ID |
| `title` | `string` | AI-generated title |
| `days` | `int` | Number of days |
| `created_at` | `datetime` | ISO 8601, UTC |
| `updated_at` | `datetime` | ISO 8601, UTC |
| `last_message_preview` | `string \| null` | Last chat message. May be `null` if no chat yet. |

**Errors:**
- `401` — Unauthorized

---

### `GET /api/v1/trips/{trip_id}`

**Purpose:** Get full trip detail including enriched itinerary and initial chat messages.

**Auth:** Required

**Response `200`:**
```json
{
  "trip": { ...TripResponse },
  "messages": {
    "total": 2,
    "limit": 50,
    "offset": 0,
    "items": [ ...TripMessageResponse ]
  }
}
```

The `messages` block here is the first page (default limit 50, offset 0).  
This is the **only endpoint that returns both trip + messages together.** Use it for the initial page load.

**Errors:**
- `401` — Unauthorized
- `404` — Trip not found or doesn't belong to user

---

### `DELETE /api/v1/trips/{trip_id}`

**Purpose:** Delete a trip owned by the current user.

**Auth:** Required

**Response:** `204 No Content`

**Errors:**
- `401` — Unauthorized
- `404` — Not found

---

### `POST /api/v1/trips/sync-guest`

**Purpose:** Claim a guest-generated trip and link it to the logged-in user account.

**Auth:** Required

**Request:**
```json
{
  "trip_id": 42
}
```

**Response `200`:** Full `TripResponse`

**Errors:**
- `400` — Trip already owned / doesn't exist
- `401` — Unauthorized

---

## 5. Trip Message / Chat Endpoints

---

### `POST /api/v1/trips/{trip_id}/messages`

**Purpose:** Send a user message. AI responds and may update the itinerary.

**Auth:** Required

**Request Body:**
```json
{
  "content": "Can you replace Day 3 with a lake day at Issyk-Kul?"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `content` | `string` | Yes | Min 1, max 2000 chars. Must be non-empty after trimming. |

**Response `200`:**
```json
{
  "message": {
    "id": 12,
    "trip_id": 1,
    "role": "assistant",
    "content": "Sure! I've updated Day 3 to be a Issyk-Kul lake day.",
    "created_at": "2026-04-21T07:45:00Z"
  },
  "updated_itinerary": { ...full enriched itinerary or null }
}
```

| Field | Type | Notes |
|---|---|---|
| `message` | `TripMessageResponse` | The AI assistant's reply |
| `updated_itinerary` | `dict \| null` | Non-null when AI changed the itinerary. Frontend should replace the local trip's `itinerary_json` with this value. |

> **Frontend rule:** Always check `updated_itinerary`. If it's not `null`, update your local trip state with the new itinerary.

**Errors:**
- `401` — Unauthorized
- `404` — Trip not found

---

### `GET /api/v1/trips/{trip_id}/messages`

**Purpose:** Paginated message history for a trip.

**Auth:** Required

**Query Params:**

| Param | Default | Range | Notes |
|---|---|---|---|
| `limit` | 50 | 1–100 | Number of messages to return |
| `offset` | 0 | ≥ 0 | How many messages to skip |

**Response `200`:**
```json
{
  "total": 10,
  "limit": 50,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "trip_id": 1,
      "role": "user",
      "content": "Can you add a rest day?",
      "created_at": "2026-04-21T07:40:00Z"
    },
    {
      "id": 2,
      "trip_id": 1,
      "role": "assistant",
      "content": "Done! I've added a rest day on Day 4.",
      "created_at": "2026-04-21T07:41:00Z"
    }
  ]
}
```

Messages are returned in **ascending chronological order** (oldest first).  
`role` is either `"user"` or `"assistant"`.

**Errors:**
- `401` — Unauthorized
- `404` — Trip not found

---

## 6. Full Trip Object Structure

### `TripResponse`

```json
{
  "id": 1,
  "title": "5-Day Bishkek & Issyk-Kul Adventure",
  "budget": "medium",
  "days": 5,
  "interests": ["nature", "culture"],
  "travel_style": "relaxed",
  "itinerary_json": { ...see below },
  "created_at": "2026-04-20T10:00:00Z",
  "updated_at": "2026-04-21T07:30:00Z"
}
```

---

### `itinerary_json` Structure

```json
{
  "summary": "A 5-day mix of city culture and mountain air in Kyrgyzstan.",
  "total_days": 5,
  "interests": ["nature", "culture"],
  "travel_style": "relaxed",
  "days": [ ...DayObject ]
}
```

| Field | Type | Notes |
|---|---|---|
| `summary` | `string` | AI-generated trip summary |
| `total_days` | `int` | Total number of days |
| `interests` | `string[]` | Interests from request |
| `travel_style` | `string` | Travel style from request |
| `days` | `DayObject[]` | One per day |

---

### `DayObject`

```json
{
  "day": 1,
  "title": "Bishkek City Exploration",
  "city": "Bishkek",
  "location": "Ala-Too Square",
  "routing_location": "Площадь Ала-Тоо Бишкек",
  "activities": [ ...ActivityObject ],
  "hotel": { ...HotelObject or null },
  "recommended_places": [ ...PlaceObject ],
  "route_from_previous": { ...RouteSegment or null },
  "images": {
    "hero": { ...HeroImageObject or null },
    "gallery": []
  }
}
```

| Field | Type | Optional | Notes |
|---|---|---|---|
| `day` | `int` | No | Day number (1-indexed) |
| `title` | `string` | No | AI-generated day title |
| `city` | `string` | No | City for that day |
| `location` | `string` | No | User-facing location name (English) |
| `routing_location` | `string` | Yes | Backend-only routing query (Russian-friendly for 2GIS). **Do not display to users.** |
| `activities` | `ActivityObject[]` | No | Schedule for the day |
| `hotel` | `HotelObject \| null` | Yes | Best matching hotel from catalog |
| `recommended_places` | `PlaceObject[]` | Yes | Up to 2 suggested places (food + attraction) |
| `route_from_previous` | `RouteSegment \| null` | Yes | Routing from previous day. Always `null` for Day 1. |
| `images` | `{ hero, gallery }` | Yes | Hero image from Pexels. Max 3 days enriched per trip. |

---

### `ActivityObject`

```json
{
  "time": "09:00",
  "description": "Visit the State Historical Museum",
  "type": "culture"
}
```

| Field | Type | Notes |
|---|---|---|
| `time` | `string` | Suggested time (HH:MM format) |
| `description` | `string` | What to do |
| `type` | `string` | Activity type: `"culture"`, `"food"`, `"nature"`, `"adventure"`, `"rest"`, `"shopping"`, `"transport"` |

---

### `HotelObject`

```json
{
  "id": 5,
  "name": "Hyatt Regency Bishkek",
  "city": "Bishkek",
  "rating": 4.7,
  "price_level": "high",
  "price_from": 150.0,
  "address": "542 Sovietskaya St, Bishkek",
  "image_url": "https://..."
}
```

| Field | Type | Optional | Notes |
|---|---|---|---|
| `id` | `int` | No | DB id |
| `name` | `string` | No | |
| `city` | `string` | No | |
| `rating` | `float` | Yes | May be `null` |
| `price_level` | `string` | Yes | `"low"`, `"medium"`, `"high"` |
| `price_from` | `float` | Yes | Nightly price (KGS or USD, depends on catalog data) |
| `address` | `string` | Yes | |
| `image_url` | `string` | Yes | May be `null` |

---

### `PlaceObject` (recommended_places item)

```json
{
  "id": 12,
  "name": "Navat Restaurant",
  "city": "Bishkek",
  "rating": 4.5,
  "type": "restaurant",
  "price_level": "medium",
  "address": "123 Chui Ave, Bishkek",
  "image_url": "https://..."
}
```

| Field | Type | Optional | Notes |
|---|---|---|---|
| `id` | `int` | No | |
| `name` | `string` | No | |
| `city` | `string` | No | |
| `rating` | `float` | Yes | |
| `type` | `string` | No | `"restaurant"`, `"cafe"`, `"attraction"`, `"activity"` |
| `price_level` | `string` | Yes | |
| `address` | `string` | Yes | |
| `image_url` | `string` | Yes | May be `null` |

---

### `RouteSegment` (route_from_previous)

```json
{
  "origin": "Bishkek",
  "destination": "Cholpon-Ata",
  "distance_km": 248.5,
  "duration_mins": 185,
  "estimated_cost": 3062.0,
  "transport_type": "taxi"
}
```

| Field | Type | Optional | Notes |
|---|---|---|---|
| `origin` | `string` | No | Previous day's location name |
| `destination` | `string` | No | Current day's location name |
| `distance_km` | `float` | No | May be `0.0` on 2GIS failure |
| `duration_mins` | `int` | No | May be `0` on 2GIS failure |
| `estimated_cost` | `float \| null` | Yes | KGS for taxi. `null` for walking or unknown. |
| `transport_type` | `string` | No | Currently always `"taxi"`. May be `"unknown"` on failure. |

> **Note:** Day 1 always has `route_from_previous: null`. All subsequent days should have a segment, but may have zeroed values if the 2GIS API was unreachable.

---

### `HeroImageObject` (images.hero)

```json
{
  "source": "pexels",
  "photo_id": "3573383",
  "url": "https://images.pexels.com/photos/3573383/pexels-photo-3573383.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
  "photographer": "Taryn Elliott",
  "photographer_url": "https://www.pexels.com/@taryn-elliott",
  "alt": "Mountains of Kyrgyzstan at sunrise",
  "search_query": "Ala-Archa National Park Kyrgyzstan"
}
```

| Field | Type | Optional | Notes |
|---|---|---|---|
| `source` | `string` | No | Always `"pexels"` |
| `photo_id` | `string` | No | Pexels photo ID |
| `url` | `string` | No | Direct image URL (large size) |
| `photographer` | `string` | Yes | Attribution name |
| `photographer_url` | `string` | Yes | Attribution link |
| `alt` | `string` | Yes | Alt text |
| `search_query` | `string` | No | Query used to find this image |

---

## 7. Frontend Usage Recommendations

### Sidebar / Trip List

- Call `GET /api/v1/trips` to populate the sidebar.
- Use `last_message_preview` as the subtitle under the trip title.
- If `last_message_preview` is `null`, show a placeholder like *"No messages yet"*.
- Sort by `updated_at` descending (backend returns in that order implicitly).

### Opening a Trip

- On trip click, call `GET /api/v1/trips/{trip_id}`.
- This returns **both** the trip and the first page of messages in one call — use it.
- Cache the returned `itinerary_json` locally in your state.
- Do not call `GET /trips` again just to refresh a single trip.

### Chat History / Load More

- On initial open, messages come embedded in `GET /trips/{trip_id}`.
- For "load more" / infinite scroll, call `GET /trips/{trip_id}/messages?offset=N&limit=50` separately.
- Messages are oldest-first. For bottom-up chat UI, reverse the list.

### Sending a Message

1. Optimistically push the user message into local state.
2. Call `POST /api/v1/trips/{trip_id}/messages`.
3. Append `response.message` (the AI reply) to the chat.
4. If `response.updated_itinerary !== null` → replace local `trip.itinerary_json` with it.
5. Do **not** re-fetch the full trip — use the response directly.

### Handling `updated_itinerary`

```ts
if (response.updated_itinerary) {
  setTrip(prev => ({ ...prev, itinerary_json: response.updated_itinerary }));
}
```

### Displaying Route (`route_from_previous`)

- Day 1: no route, don't render any routing UI.
- Days 2+: render route between cities.
- If `distance_km === 0` and `duration_mins === 0` → 2GIS failed. Show fallback: *"Route info unavailable"*.
- If `transport_type === "unknown"` → same fallback.
- Never hide the day just because routing failed.

### Handling Missing Images

- `images` key may be absent on some days (only up to 3 days per trip get images).
- Always check: `day.images?.hero?.url` before rendering.
- For days without images, show a generic placeholder or a gradient card.
- Do **not** make extra API calls to fetch images — they are embedded in `itinerary_json`.

### Displaying Hotel / Places

- `hotel` may be `null` if no matching hotel was found in the catalog for that city.
- `recommended_places` may be empty `[]`.
- `image_url` inside hotel or place may be `null` — use a placeholder.
- `rating` may be `null` — hide stars rather than showing `0`.

---

## 8. Suggested Frontend Data Flow

```
App Start
  → GET /auth/me    (check if logged in)

Sidebar
  → GET /api/v1/trips
  → display items with title + last_message_preview

User clicks a trip
  → GET /api/v1/trips/{trip_id}
  → render itinerary_json.days
  → render messages.items as chat history

User sends a message
  → POST /api/v1/trips/{trip_id}/messages  { content }
  → append message to chat
  → if updated_itinerary → update local trip state

User scrolls up in chat
  → GET /api/v1/trips/{trip_id}/messages?offset=50&limit=50
  → prepend older messages to chat list

User generates a new trip (not logged in)
  → POST /api/v1/trips/generate  (no auth needed)
  → save trip.id locally (localStorage/cookie)

User logs in after guest generation
  → POST /api/v1/auth/login
  → POST /api/v1/trips/sync-guest  { trip_id }
  → trip now belongs to user account
```

---

## 9. Known Backend Behaviors / Important Notes

| Behavior | Note |
|---|---|
| **Routing may fail** | If 2GIS is unavailable, `route_from_previous` will have `distance_km: 0`, `duration_mins: 0`, `transport_type: "unknown"`. Frontend must handle gracefully. |
| **Images are partial** | Only up to **3 days** per trip receive a hero image. Never assume all days have images. |
| **`routing_location` is internal** | Used by backend to resolve locations in 2GIS. It may be in Russian. **Never display it to users.** Always use `location` for UI. |
| **`hotel` and `recommended_places` depend on catalog** | If the catalog doesn't have data for a city, these fields will be `null` or `[]`. |
| **Guest trips** | Trips created without auth are valid. They have `user_id: null` in the DB. Use `sync-guest` to claim them. |
| **AI may not always update itinerary** | `updated_itinerary` in chat continuation can be `null` — this is normal when the AI only replies without changing the plan. |
| **`image_url` in hotel/place can be null** | Always add placeholder fallback. |
| **Messages are filtered by ownership** | You cannot access another user's trip messages — 404 will be returned. |
| **`prompt` field is optional** | If sent, it's injected into the AI prompt to personalize the trip. |

---

## 10. Ready-to-Use JSON Examples

### Trip Generation Request

```json
POST /api/v1/trips/generate
{
  "budget": "medium",
  "days": 5,
  "interests": ["nature", "culture", "food"],
  "travel_style": "relaxed",
  "prompt": "We prefer less hiking. Looking for a romantic trip."
}
```

---

### Trip List Response

```json
GET /api/v1/trips
{
  "items": [
    {
      "id": 1,
      "title": "5-Day Bishkek & Issyk-Kul Adventure",
      "days": 5,
      "created_at": "2026-04-20T10:00:00Z",
      "updated_at": "2026-04-21T07:30:00Z",
      "last_message_preview": "Can you add a rest day on Day 3?"
    },
    {
      "id": 2,
      "title": "3-Day Karakol Mountains Escape",
      "days": 3,
      "created_at": "2026-04-18T09:00:00Z",
      "updated_at": "2026-04-18T09:00:00Z",
      "last_message_preview": null
    }
  ]
}
```

---

### Trip Detail Response (abbreviated)

```json
GET /api/v1/trips/1
{
  "trip": {
    "id": 1,
    "title": "5-Day Bishkek & Issyk-Kul Adventure",
    "budget": "medium",
    "days": 5,
    "interests": ["nature", "culture"],
    "travel_style": "relaxed",
    "itinerary_json": {
      "summary": "A 5-day journey through Bishkek and Issyk-Kul.",
      "total_days": 5,
      "interests": ["nature", "culture"],
      "travel_style": "relaxed",
      "days": [
        {
          "day": 1,
          "title": "Bishkek City Exploration",
          "city": "Bishkek",
          "location": "Ala-Too Square",
          "routing_location": "Площадь Ала-Тоо Бишкек",
          "activities": [
            { "time": "09:00", "description": "Visit Ala-Too Square", "type": "culture" },
            { "time": "12:00", "description": "Lunch at Osh Bazaar", "type": "food" }
          ],
          "hotel": {
            "id": 5,
            "name": "Hyatt Regency Bishkek",
            "city": "Bishkek",
            "rating": 4.7,
            "price_level": "high",
            "price_from": 150.0,
            "address": "542 Sovietskaya St",
            "image_url": "https://..."
          },
          "recommended_places": [
            {
              "id": 12,
              "name": "Navat Restaurant",
              "city": "Bishkek",
              "rating": 4.5,
              "type": "restaurant",
              "price_level": "medium",
              "address": "123 Chui Ave",
              "image_url": null
            }
          ],
          "route_from_previous": null,
          "images": {
            "hero": {
              "source": "pexels",
              "photo_id": "3573383",
              "url": "https://images.pexels.com/photos/3573383/...",
              "photographer": "Taryn Elliott",
              "photographer_url": "https://www.pexels.com/@taryn-elliott",
              "alt": "Bishkek city square",
              "search_query": "Ala-Too Square Bishkek Kyrgyzstan"
            },
            "gallery": []
          }
        },
        {
          "day": 2,
          "title": "Drive to Issyk-Kul",
          "city": "Cholpon-Ata",
          "location": "Issyk-Kul Lakefront",
          "routing_location": "Чолпон-Ата Иссык-Куль",
          "activities": [
            { "time": "08:00", "description": "Drive to Cholpon-Ata", "type": "transport" },
            { "time": "14:00", "description": "Relax at the lake beach", "type": "nature" }
          ],
          "hotel": { "id": 8, "name": "Ak-Bura Hotel", "city": "Cholpon-Ata", "rating": 4.2, "price_level": "medium", "price_from": 80.0, "address": "Lake Rd 1", "image_url": null },
          "recommended_places": [],
          "route_from_previous": {
            "origin": "Bishkek",
            "destination": "Cholpon-Ata",
            "distance_km": 248.5,
            "duration_mins": 185,
            "estimated_cost": 3062.0,
            "transport_type": "taxi"
          },
          "images": null
        }
      ]
    },
    "created_at": "2026-04-20T10:00:00Z",
    "updated_at": "2026-04-21T07:30:00Z"
  },
  "messages": {
    "total": 2,
    "limit": 50,
    "offset": 0,
    "items": [
      {
        "id": 1,
        "trip_id": 1,
        "role": "user",
        "content": "Can you add a rest day?",
        "created_at": "2026-04-21T07:40:00Z"
      },
      {
        "id": 2,
        "trip_id": 1,
        "role": "assistant",
        "content": "Done! I've made Day 4 a rest and relaxation day.",
        "created_at": "2026-04-21T07:41:00Z"
      }
    ]
  }
}
```

---

### Messages List Response

```json
GET /api/v1/trips/1/messages?limit=50&offset=0
{
  "total": 4,
  "limit": 50,
  "offset": 0,
  "items": [
    { "id": 1, "trip_id": 1, "role": "user", "content": "Hello!", "created_at": "2026-04-21T07:00:00Z" },
    { "id": 2, "trip_id": 1, "role": "assistant", "content": "Hi! How can I improve your trip?", "created_at": "2026-04-21T07:01:00Z" },
    { "id": 3, "trip_id": 1, "role": "user", "content": "Add a rest day on Day 4.", "created_at": "2026-04-21T07:40:00Z" },
    { "id": 4, "trip_id": 1, "role": "assistant", "content": "Done! Day 4 is now a rest day.", "created_at": "2026-04-21T07:41:00Z" }
  ]
}
```

---

### Chat Continuation Response

```json
POST /api/v1/trips/1/messages
{
  "content": "Replace Day 3 with a trip to Ala-Archa."
}

Response 200:
{
  "message": {
    "id": 5,
    "trip_id": 1,
    "role": "assistant",
    "content": "Done! Day 3 is now a visit to Ala-Archa National Park.",
    "created_at": "2026-04-21T08:00:00Z"
  },
  "updated_itinerary": {
    "summary": "...",
    "total_days": 5,
    "days": [ ... ]
  }
}
```

If the AI only replied without changing the plan:

```json
{
  "message": { ... },
  "updated_itinerary": null
}
```
