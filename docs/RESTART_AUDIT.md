# Restart audit (2026-10-24)

This is a local development snapshot, not proof that external AI, maps, images, email, or all authenticated user flows work with production credentials.

## Verified

- The traveler frontend production build succeeds and its Vite development server returns HTTP 200.
- The business panel production build succeeds after declaring its missing `react-is` dependency; its Vite development server returns HTTP 200.
- The backend Docker image builds. With the isolated `nomadai` compose project, PostgreSQL uses host port 5433 by default and the API uses host port 8000. Alembic upgrades to the current head, `/health` returns `{"status":"ok"}`, and `/docs` returns HTTP 200.
- The full backend suite passes (108 tests), including persisted trip generation and HTTP contract checks. Branch coverage across production code is 65% with test files excluded.
- Backend Ruff passes on `app/`. The traveler frontend and business panel both pass lint, tests, and production builds.
- Three GitHub Actions workflows run only when their application directory or their own workflow file changes on a PR to `dev`.

## Known gaps

- Traveler frontend tests exercise trip form validation and the guest generation navigation flow. Whole-source line coverage is 13.78% (10 tests); the business panel covers 3.10% (8 tests), including login form validation. These are low baselines, not sufficient confidence for all application flows.
- Both frontend builds warn about large bundles. The traveler build also warns about deprecated Sass color helpers.
- The business panel's npm install reports dependency audit findings. Review with `npm audit` before a production release rather than applying automated major upgrades blindly.
- Live trip generation, paid flow, provider quotas, and country expansion were not tested. They require valid credentials and end to end data checks.

## Next engineering checks

1. Raise frontend and business-panel coverage with browser-level tests for guest sync, editing an itinerary, subscriptions, and sponsored place workflows using a disposable database. Do not increase gates by excluding untested production code.
2. Exercise a real authenticated trip and sponsored place workflow with test credentials.
3. Work through [EXPANSION_PLAN.md](EXPANSION_PLAN.md) after the hackathon requirements arrive.
