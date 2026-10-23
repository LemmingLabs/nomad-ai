# Traveler frontend context

This Vite, React, and TypeScript app is the traveler experience. It uses Feature-Sliced Design under `src/`: `app` for providers, routes, and global styles; `pages` for screens; `widgets` for composed page sections; `features` for user actions; `entities` for domain data and API access; and `shared` for reusable infrastructure and UI. Preserve this direction when adding functionality. Higher layers may compose lower layers; avoid importing page or widget code into entities or shared code.

## Existing flows

- Home generation form: `src/widgets/generate-trip-form`, with validation in `src/features/trip/generate-trip/model/schema.ts` and API calls in that feature.
- Trip workspace: `src/pages/trip`, chat widget, itinerary preview, day cards, routes, and trip entities.
- Auth and guest transfer: auth features, `src/app/providers/AppBootstrap.tsx`, and the trip sync feature. Preserve the guest to account transition.
- Subscriptions and usage: subscription and limit entities, related features and widgets.
- API client: `src/shared/api/client.ts`; its base URL comes from `VITE_API_BASE_URL`.

Zustand owns client state, TanStack Query owns server state, React Hook Form and Zod own forms, and SCSS Modules style components. Reuse existing conventions and public slice exports. `FRONTEND_ARCHITECTURE.md` contains earlier design notes; inspect current code where it differs.

## Destination expansion

The current form does not have a country field, and the backend request contract has no country field. Add an explicit destination selection only with the matching backend contract and persistence work. Avoid inferring country from free text or changing the UI alone. Show route provenance or verification labels only when the API supplies evidence. Keep missing photos, hotels, places, and routes safe to render.

## Local checks

Use `npm ci`, `npm run build`, and `npm run lint`; start with `npm run dev -- --host 127.0.0.1`. The app expects `frontend/.env` based on `.env.example` and a backend at the configured URL. Do not commit `.env` or generated `dist/` files.
