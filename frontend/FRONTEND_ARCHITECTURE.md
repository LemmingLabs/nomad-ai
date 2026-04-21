# NomadAI Frontend Architecture

> Last updated: April 2026  
> Purpose: Define frontend architecture, stack, design system, and UI principles for AI Trip Planner

---

## 1. Project Overview

NomadAI frontend is a **React-based AI travel planning interface**.

Core idea:
- User interacts with AI via chat
- AI generates and updates a structured trip
- UI displays **chat + live itinerary simultaneously**

### Main UX Concept

```

Sidebar | Chat Panel | Trip Itinerary Preview

```

- Left → trips & navigation
- Center → AI chat
- Right → generated trip (rich UI)

This is NOT just a chat app — it's a **real-time trip builder interface**.

---

## 2. Tech Stack

### Core

- React + TypeScript
- Vite
- SCSS Modules

### State Management

- Zustand → UI / client state
- React Query (@tanstack/react-query) → server state

### API

- Axios

### Forms

- React Hook Form
- Zod
- @hookform/resolvers

### Routing

- React Router

### UI / Utils

- classnames
- lucide-react (icons)
- react-markdown + remark-gfm
- react-toastify

---

## 3. Project Architecture (FSD)

We use **Feature-Sliced Design (FSD)**.

```

src/
app/
pages/
widgets/
features/
entities/
shared/

```

---

## 4. Folder Structure

### app/

Global app setup

```

app/
providers/
router/
query-client/
store/
theme/
styles/
globals.scss
variables.scss
mixins.scss
reset.scss

```

---

### pages/

Application screens

```

pages/
home/
auth/
login/
register/
trip/
not-found/

```

---

### widgets/

Large UI blocks

```

widgets/
sidebar/
chat-panel/
trip-preview/
trip-day-card/
trip-route-block/
trip-header/
generate-trip-form/
auth-form/

```

---

### features/

User actions

```

features/
auth/
login-by-email/
register-by-email/
logout/

trip/
generate-trip/
send-trip-message/
sync-guest-trip/
delete-trip/
select-trip/

ui/
toggle-theme/
open-sidebar/

```

---

### entities/

Domain models

```

entities/
user/
trip/
message/
hotel/
place/
route/

```

Each entity contains:
- model (types, store logic)
- api (requests)
- ui (small reusable parts)

---

### shared/

Reusable layer

```

shared/
api/
config/
lib/
hooks/
types/
ui/
assets/

```

---

## 5. UI Layout

### Desktop Layout

```

---

| Sidebar | Chat Panel              | Trip Preview       |
|         |                         |                    |
| Trips   | messages                | title              |
| history | input                   | day cards          |
| profile | send button             | routes             |
|         |                         | hotels/places      |
----------------------------------------------------------

```

### Column Sizes

- Sidebar: ~260–280px
- Chat: ~400–450px
- Preview: flexible (main area)

---

### Mobile Layout

Use tab-based navigation:

- Chat
- Trip
- My Trips

---

## 6. Design System

### Style Direction

**Minimal premium travel + AI**

Focus:
- clean UI
- large typography
- soft cards
- rich content (images, routes, cards)
- lots of whitespace

---

### Font

Primary font:

```

Manrope

```

Fallback:
```

Inter

```

---

### Color System (Light Theme)

- Background: `#F7F7F3`
- Cards: `#FFFFFF`
- Border: `#E7E5E4`
- Text: `#1F2937`
- Accent: `#14B8A6` (teal)

---

### Future

- Dark mode support (optional later)

---

## 7. Shared UI Components

```

shared/ui/
button/
input/
textarea/
typography/
container/
card/
badge/
chip/
icon-button/
avatar/
divider/
skeleton/
spinner/
modal/
dropdown/

```

---

## 8. Core Entities

### Trip

- id
- title
- budget
- days
- interests
- travel_style
- itinerary_json

---

### Itinerary

Contains:

- summary
- total_days
- days[]

---

### Day Object

- title
- city
- location
- activities
- hotel
- recommended_places
- route_from_previous
- images

---

### Message

- role: user | assistant
- content
- created_at

---

## 9. Data Flow

### App Start

```

GET /auth/me

```

---

### Load Trips

```

GET /trips

```

---

### Open Trip

```

GET /trips/{id}
→ returns trip + messages

```

---

### Send Message

```

POST /trips/{id}/messages

```

Important rule:

```

if (updated_itinerary !== null)
→ replace local itinerary

```

---

## 10. Key Frontend Rules

### 1. Do NOT refetch trip after message

Use response directly.

---

### 2. Handle missing data

- images may be missing
- hotel may be null
- places may be empty
- route may fail

---

### 3. Never show `routing_location`

Use only `location`.

---

### 4. Defensive UI

Always check:

```

day.images?.hero?.url
day.hotel
day.recommended_places.length

````

---

## 11. Key Widgets

### Sidebar

- trips list
- active trip
- user

---

### Chat Panel

- message list
- markdown rendering
- input
- send button

---

### Trip Preview

- summary
- list of days

---

### Day Card

- title
- image
- activities
- hotel
- places
- route

---

### Route Block

- distance
- duration
- cost
- fallback if unavailable

---

## 12. Installation

```bash
npm install axios classnames lucide-react react-hook-form react-imask react-markdown react-router-dom react-toastify remark-gfm zod zustand @tanstack/react-query @hookform/resolvers

npm install -D sass husky lint-staged eslint prettier
````

---

## 13. Development Plan

### Phase 1 — Foundation

* project setup
* styles
* API client
* routing
* state setup

---

### Phase 2 — Architecture

* FSD structure
* entities
* types

---

### Phase 3 — Layout

* sidebar
* chat panel
* trip preview

---

### Phase 4 — Features

* auth
* generate trip
* trip details
* chat updates

---

## 14. Final Vision

NomadAI frontend should feel like:

* AI assistant
* travel designer
* interactive product

NOT:

* simple chat
* plain dashboard

---

### Core Principle

> Chat drives the experience
> Itinerary visualizes the result
