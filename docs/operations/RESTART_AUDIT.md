# Restart Audit (2026-10-24)

This is a local development snapshot, not proof that external AI, maps, images, email, or all authenticated user flows work with production credentials.

## Verified

- The traveler frontend production build succeeds and its Vite development server returns HTTP 200.
- The business panel production build succeeds after declaring its missing `react-is` dependency; its Vite development server returns HTTP 200.
- Backend dependencies are likely installed in the local environment; tests/lint not yet fully verified.
- Documentation structure reorganized (this document moved to `operations/`).

## Known Issues / Gaps

- Missing credentials for external providers (AI, maps, email, storage) may cause fallbacks/mock responses.
- Some migrations may need to be applied for full functionality.
- Frontend/backend integration tests not systematically run.
- There is no systematic lint/test report for all packages.

## Recommendations
- Create `.env` files from `.env.example` for backend/frontend/businessPanel.
- Run migrations: `alembic upgrade head` from backend.
- Verify external provider availability before demo.
- Run focused tests/lint for changed packages.

## Startup Commands (suggested)
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`
- Business panel: `npm run dev`

## Notes
- The original Russian documents moved from `docs/` root to appropriate subfolders. New structure follows `docs/README.md`.
- Screenshots moved to `docs/assets/screenshots/`.
- Certificate moved to `docs/assets/`.
- MONETIZATION_AND_SPONSORED_SYSTEM.md remains in `business/` as is (English) — it describes current implementation details.
