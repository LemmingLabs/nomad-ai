## Quick Start

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec app alembic upgrade head
curl http://localhost:8000/health
```

The API documentation is at `http://localhost:8000/docs`; application routes use `/api/v1`. Configure real secrets and provider keys in `.env`. See [AGENTS.md](AGENTS.md) for the code map and current geographic constraints.

For a local Python setup, use Python 3.11+, install `requirements.txt` in a virtual environment, configure `DATABASE_URL` for a reachable PostgreSQL instance, run `alembic upgrade head`, then start `python -m uvicorn app.main:app --reload`.
