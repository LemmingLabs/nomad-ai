# NomadAI project context

NomadAI is a travel planning workspace. A traveler gives constraints, receives a structured day by day itinerary, and can refine a saved trip through chat. This repository contains three applications: `backend/` (FastAPI and PostgreSQL), `frontend/` (traveler React app), and `businessPanel/` (business and admin React app).

## Product state and direction

- The implemented planning flow is currently Kyrgyzstan specific. Do not describe worldwide trip planning as shipped.
- The next product goal is to let travelers select destinations across multiple countries. Keep Kyrgyzstan working while adding explicit country and destination data through the API, persistence, prompts, enrichment, and UI.
- Another goal is to improve route quality with legally usable, attributed route knowledge. Research source availability and license terms before importing content. Treat AI output and third party place results as suggestions until validated; never label a route as guide verified without evidence.
- Preserve guest generation and account sync, saved trips, chat edits, subscriptions, sponsored places, and business/admin workflows as the product expands.
- The hackathon brief and judging requirements have not been supplied yet. Incorporate them when available rather than assuming requirements.

## Repository map

- `frontend/AGENTS.md`: traveler app architecture and boundaries.
- `backend/AGENTS.md`: API, data, and itinerary pipeline.
- `businessPanel/AGENTS.md`: business and admin panel.
- `docs/EXPANSION_PLAN.md`: staged destination and route quality work.
- `docs/RESTART_AUDIT.md`: verified startup state and known test or lint gaps.
- `README.md`: product overview; some examples may reflect the original Kyrgyzstan scope. Check code before relying on an endpoint or data model claim.

## Working agreements

- Make changes in the component that owns the behavior, then update API contracts and consumers together.
- Keep user owned environment files and secrets out of commits. Use the checked in `.env.example` files to document required variables.
- Do not silently replace a failed provider response with a plausible itinerary in production; surface degraded or mock behavior clearly.
- Check existing migrations and add an Alembic migration for persistent schema changes. Do not edit an applied migration.
- Run focused verification for touched code and record any missing credentials, unavailable services, or pre-existing failures honestly.
