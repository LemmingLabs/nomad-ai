# Restart audit (2026-10-24)

This is a local development snapshot, not proof that external AI, maps, images, email, or all authenticated user flows work with production credentials.

## Verified

- The traveler frontend production build succeeds and its Vite development server returns HTTP 200.
- The business panel production build succeeds after declaring its missing `react-is` dependency; its Vite development server returns HTTP 200.
- The backend Docker image builds. With the isolated `nomadai` compose project, PostgreSQL uses host port 5433 by default and the API uses host port 8000. Alembic upgrades to the current head, `/health` returns `{"status":"ok"}`, and `/docs` returns HTTP 200.
- The full backend suite passes (99 tests) after replacing obsolete 2GIS tests with Google Maps and current routing tests.
- Backend Ruff passes on `app/`. The traveler frontend and business panel both pass lint, tests, and production builds.
- Three GitHub Actions workflows run only when their application directory or their own workflow file changes on a PR to `dev` or a push to `dev`.

## Known gaps

- The new React tests cover selected pure business logic and validation; they do not yet exercise rendered screens or browser interactions.
- Both frontend builds warn about large bundles. The traveler build also warns about deprecated Sass color helpers.
- The business panel's npm install reports dependency audit findings. Review with `npm audit` before a production release rather than applying automated major upgrades blindly.
- Live trip generation, paid flow, provider quotas, and country expansion were not tested. They require valid credentials and end to end data checks.

## Next engineering checks

1. Add browser-level tests for trip generation, guest sync, and sponsored place workflows using a disposable database.
2. Exercise a real authenticated trip and sponsored place workflow with test credentials.
3. Work through [EXPANSION_PLAN.md](EXPANSION_PLAN.md) after the hackathon requirements arrive.
