# Agentic Invoice Processing

A monorepo for an agentic invoice-processing tool: a Strands-based agent behind a
chat API, with a React web UI. Upload an invoice (and optionally a purchase order);
the agent extracts, validates, reconciles against the PO, and returns an
`APPROVED` / `NEEDS_REVIEW` decision.

```
backend/    FastAPI + Strands agent, SQLAlchemy/PostgreSQL (Alembic), tests
frontend/   React (Vite) chat UI calling the backend's POST /chat
specs/      Spec-Kit artifacts (spec, plan, research, data-model, contracts, tasks)
```

## Run with Docker (all three services)

```bash
# provide model keys (or put them in a .env next to docker-compose.yml)
export OPENAI_API_KEY=sk-...  GEMINI_API_KEY=...
docker compose up --build
```

- Postgres → `localhost:5434`, backend → `http://localhost:8010`, frontend → `http://localhost:5173`.
- The backend image runs `alembic upgrade head` on start (creates the schema), then seeds the PO reference data.
- Each service also has its own `Dockerfile` (`backend/Dockerfile`, `frontend/Dockerfile`) if you prefer to build/run them individually. The frontend bakes `VITE_API_BASE` at build time (build arg, default `http://localhost:8010`).

## Backend (local, without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                 # set OPENAI_API_KEY, GEMINI_API_KEY, DATABASE_URL

# Postgres (local Docker) + schema
docker run -d --name aip-pg -e POSTGRES_USER=invoice -e POSTGRES_PASSWORD=invoice \
  -e POSTGRES_DB=invoices -p 5434:5432 postgres:16
alembic upgrade head                 # creates the 4 tables

uvicorn app.main:app --port 8010     # seeds PO reference data on startup
pytest                               # 36 tests, ~90% coverage
```

Endpoints: `POST /chat` (multipart: `message`, optional `conversation_id`,
`invoice`, `po`) → natural-language reply + structured decision; `GET /health`.
CORS is enabled for the local frontend.

## Frontend

```bash
cd frontend
npm install
cp .env.example .env                 # optional: VITE_API_BASE (default http://localhost:8010)
npm run dev                          # http://localhost:5173
```

See `backend/README.md` and `frontend/README.md` for details, and
`specs/001-agentic-invoice-strands/` for the full design.
