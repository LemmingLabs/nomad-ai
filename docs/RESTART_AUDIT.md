# Restart audit (2026-10-24)

This is a local development snapshot, not proof that external AI, maps, images, email, or all authenticated user flows work with production credentials.

## Verified

- The traveler frontend production build succeeds and its Vite development server returns HTTP 200.
- The business panel production build succeeds after declaring its missing `react-is` dependency; its Vite development server returns HTTP 200.
- The backend Docker image builds. With the isolated `nomadai` compose project, PostgreSQL uses host port 5433 by default and the API uses host port 8000. Alembic upgrades to the current head, `/health` returns `{"status":"ok"}`, and `/docs` returns HTTP 200.
- The backend sponsored injection tests pass (6 tests), and the routing endpoint tests pass after the provider failure fix (3 tests).

## Known gaps

- The full backend test run cannot collect three legacy files: two 2GIS tests import the removed `app.integrations.twogis_client`, and `test_routing_schema.py` imports the removed `RouteResponse` schema. With those files excluded, 87 tests passed and five failed before the routing exception fix. Four failures assert removed 2GIS settings or patch the removed 2GIS routing client; the fifth showed that the routing estimate endpoint propagated provider exceptions. The endpoint now returns an empty estimate on a provider failure. Review or replace the legacy tests against the current Google routing implementation before relying on the full suite.
- The business panel lint command currently reports 10 errors and 6 warnings, mostly React hook/effect and Fast Refresh rules. The traveler frontend lint command passed after a small type and mutation callback cleanup.
- Both frontend builds warn about large bundles. The traveler build also warns about deprecated Sass color helpers.
- The business panel's npm install reports dependency audit findings. Review with `npm audit` before a production release rather than applying automated major upgrades blindly.
- Live trip generation, paid flow, provider quotas, and country expansion were not tested. They require valid credentials and end to end data checks.

## Next engineering checks

1. Replace stale backend tests and run the full suite in the Docker image.
2. Resolve business panel lint failures, then keep lint and builds in CI.
3. Exercise a real authenticated trip and sponsored place workflow with test credentials and a disposable database.
4. Work through [EXPANSION_PLAN.md](EXPANSION_PLAN.md) after the hackathon requirements arrive.
