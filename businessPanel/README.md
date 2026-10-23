# NomadAI business and admin panel

React, TypeScript, and Vite app for business profiles, sponsored places, analytics, moderation, user roles, and subscription plans. See [AGENTS.md](AGENTS.md) for architecture and ownership.

## Run locally

```bash
cp .env.example .env
npm ci
npm run dev
```

Set `VITE_API_BASE_URL` to the backend origin, such as `http://127.0.0.1:8000`. Configure the Google Maps browser key and map ID when testing the sponsored place picker. Run `npm run build` and `npm run lint` before merging changes.

The current sponsored place form assumes Kyrgyzstan. See [the expansion plan](../docs/EXPANSION_PLAN.md) before enabling businesses in additional countries.
