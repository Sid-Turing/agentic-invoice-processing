# Agentic Invoice Processing

A Strands agent (OpenAI orchestrator + Gemini vision) behind a chat API, with a
React UI. Upload an invoice (and optionally a PO); the agent extracts it, resolves
the PO (uploaded or from the DB), validates and reconciles, persists the result,
and replies **APPROVED** / **NEEDS_REVIEW**. A read layer adds history, a
dashboard, and PO/vendor browsers.

```
backend/    FastAPI + SQLAlchemy/PostgreSQL (Alembic) — agent, tools, read APIs, tests
frontend/   React + Vite — chat (with live dashboard rail), history, dashboard, PO/vendors
specs/      Spec-Kit artifacts (spec, plan, tasks) for each feature
```

## The agent

One **orchestrator agent** (OpenAI model) runs each chat turn: it reasons over the
message, decides which tools to call, and performs the validation and invoice↔PO
reconciliation itself (not hardcoded steps). It uses **5 tools**:

| Tool | Purpose |
|---|---|
| `extract_document` | read an uploaded invoice/PO into structured data (Gemini vision) |
| `lookup_purchase_order` | fetch a PO (+ vendor, line items) from the DB by number |
| `store_purchase_order` | persist an uploaded PO (upsert by number) |
| `store_decision` | persist the final decision (verdict, reasons, check trace) |
| `calculate` | exact arithmetic for line-item / tax / total checks |

## Quick start (Docker)

```bash
export OPENAI_API_KEY=sk-...  GEMINI_API_KEY=...   # or put them in a .env beside docker-compose.yml
docker compose up --build
```

Frontend → http://localhost:5173 · backend → http://localhost:8010 · Postgres → `:5434`.
The backend container runs `alembic upgrade head` (creates the schema) then seeds PO
reference data on boot.

## Local dev

Requires **poppler** for PDF rendering (`brew install poppler` / `apt-get install poppler-utils`).

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # OPENAI_API_KEY, GEMINI_API_KEY, DATABASE_URL
docker run -d --name aip-pg -e POSTGRES_USER=invoice -e POSTGRES_PASSWORD=invoice \
  -e POSTGRES_DB=invoices -p 5434:5432 postgres:16
alembic upgrade head            # create tables
uvicorn app.main:app --port 8010
pytest
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173 (VITE_API_BASE defaults to :8010)
```

## API

| Endpoint | Purpose |
|---|---|
| `POST /chat` | multipart (`message`, optional `conversation_id`, `invoice`, `po`) → reply + structured decision |
| `POST /chat/stream` | same inputs, streamed as SSE (`tool` / `tool_result` / `token` / `decision`) |
| `GET /health` | liveness + provider/DB status |
| `GET /invoices`, `/invoices/{id}` | processed-invoice history + detail |
| `GET /summary` | dashboard metrics (counts, aging, priority) |
| `GET /purchase-orders`, `/purchase-orders/{no}`, `/vendors` | reference data |

See `backend/README.md` and `frontend/README.md` for details, `specs/` for design.
