# Business and admin panel context

This Vite, React, and TypeScript app is separate from the traveler frontend. `src/app` defines providers, layouts, and routes; `src/pages` maps routes to screens; `src/features/business` and `src/features/admin` own workflows; `src/shared` contains API, config, UI, and utilities. Follow these existing boundaries when extending the panel.

## Existing workflows

- `src/app/router/routes.tsx` protects admin and business routes with auth and role guards.
- Business screens manage profile, media, sponsored places, and analytics.
- Admin screens manage users, businesses, subscription plans, sponsored moderation, and analytics.
- `src/shared/api/client.ts` handles the base URL and access token. Feature API modules own endpoint calls. `VITE_API_BASE_URL` points to the FastAPI host; Google Maps UI uses the keys in `.env.example`.

## Destination expansion

The sponsored place form and location utilities currently validate Kyrgyzstan coordinates and phone input. Do not broaden the traveler destination list without revisiting the business location model, moderation, country aware matching, and form validation. Keep role checks and approval status intact. Sponsored content must remain visibly distinguishable from curated or organically selected route stops.

## Local checks

Use Node 24.12+ and run `npm ci`, `npm run lint`, `npm test`, and `npm run build`; start with `npm run dev -- --host 127.0.0.1`. Vitest tests live in `tests/` grouped by domain and include all production `src` modules in coverage. Test business and admin workflows through rendered forms and routes as coverage grows. The panel needs `businessPanel/.env` based on `.env.example` and a reachable backend for authenticated workflows. Do not commit `.env`, generated `dist/`, or `coverage/` files.
