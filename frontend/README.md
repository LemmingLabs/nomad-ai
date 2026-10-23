# NomadAI traveler frontend

React, TypeScript, and Vite app for generating, viewing, saving, and editing trips. The code follows Feature-Sliced Design; see [AGENTS.md](AGENTS.md) for ownership rules and [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) for earlier design notes.

## Run locally

```bash
cp .env.example .env
npm ci
npm run dev
```

Set `VITE_API_BASE_URL` to the backend origin, such as `http://127.0.0.1:8000`. API calls use the `/api/v1` route prefix. Run `npm run build` for the production build and `npm run lint` for static checks.

Destination selection beyond Kyrgyzstan is planned in [the expansion plan](../docs/EXPANSION_PLAN.md) and is not yet implemented.
