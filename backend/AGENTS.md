# Backend context

This is a FastAPI application with SQLAlchemy models and repositories, Alembic migrations, PostgreSQL, and external Groq, Google Maps, and Pexels integrations. `app/api/router.py` mounts versioned routes under `/api/v1`; `/health` and `/docs` are unversioned. Keep HTTP validation and response handling in `app/api`, business orchestration in `app/services`, provider calls in `app/integrations`, storage access in `app/repositories`, and API contracts in `app/schemas`.

## Trip lifecycle

`POST /api/v1/trips/generate` calls `trip_service.generate_trip`: AI generation, normalization, place candidates, catalog, routing, images, sponsored injection, persistence, and initial chat messages. Chat changes run through `trip_message_service`; preserve unchanged days where possible and refresh changed route/media data. Authenticated trips, guest sync, limits, and business analytics depend on this contract. Changes to the itinerary JSON must be checked against `frontend/src/entities/trip/model/types.ts` and both consumers.

## Current geographic boundary

`app/utils/prompt_builder.py` forces Kyrgyzstan and a fixed city list. `trip_service.py` has Kyrgyzstan specific defaults, city normalization, and mock fallback. Catalog, candidate search, route provider queries, sponsored matching, and business place validation may also assume Kyrgyzstan. A multi-country change needs explicit destination fields throughout the request, trip model, prompts, persisted itinerary, edits, and enrichment. Preserve existing Kyrgyzstan trips while migrating data. Do not claim country coverage solely because an AI prompt accepts a country name.

## Route quality

Store source, license, geographic scope, update date, and verification status for curated route knowledge. Validate place coordinates, opening/seasonal constraints, travel times, and day pacing. Distinguish curated routes from AI suggestions. Never copy private guide itineraries or import scraped content without usage rights. See `../docs/EXPANSION_PLAN.md`.

## Local checks

`docker compose up --build -d` in this directory starts PostgreSQL and the API using `backend/.env`; run `docker compose exec app alembic upgrade head` for migrations. Check `http://localhost:8000/health` and `/docs`. Alternatively install `requirements.txt` in a Python 3.11+ virtual environment, point `DATABASE_URL` at a reachable PostgreSQL instance, then run `python -m uvicorn app.main:app --reload`. Run `python -m pytest -q` and `python -m ruff check app` before merging; CI installs `requirements-ci.txt` and runs both.
