# Agentic Invoice Processing

A single-user backend service that reworks a legacy multi-service invoice pipeline
into one **Strands Agents** flow behind a ChatGPT-style multimodal chat API. You
chat with an orchestrator agent; it extracts an invoice, resolves the matching
purchase order (uploaded or from the database), validates and reconciles, persists
the result, and replies with a decision.

- **Orchestrator agent** (OpenAI) + five tools: `extract_document` (Gemini vision),
  `lookup_purchase_order` (DB read), `store_purchase_order` + `store_decision`
  (DB write), `calculate` (deterministic math). Validation/reconciliation are done
  by the agent's reasoning, not hardcoded steps.
- **PostgreSQL** via SQLAlchemy 2.0; schema created from scratch with **Alembic**;
  connection from `DATABASE_URL` (swappable).
- No email service, no auth. This is the **backend** of the monorepo; the web UI is
  the React app in `../frontend`, which calls the non-streaming `POST /chat`
  endpoint (CORS is enabled for local dev).

See `specs/001-agentic-invoice-strands/` for the full spec, plan, and contracts.

## Prerequisites

- Python 3.11+
- PostgreSQL (local Docker is fine)
- `poppler` (for `pdf2image`) — macOS `brew install poppler`; Debian `apt-get install poppler-utils`
- An OpenAI API key and a Google Gemini API key

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # fill in OPENAI_API_KEY, GEMINI_API_KEY, DATABASE_URL
```

Start Postgres and create the schema:

```bash
docker run -d --name aip-pg -e POSTGRES_USER=invoice -e POSTGRES_PASSWORD=invoice \
  -e POSTGRES_DB=invoices -p 5432:5432 postgres:16
alembic upgrade head        # creates the 4 tables from scratch
```

## Run

```bash
uvicorn app.main:app --reload --port 8000   # seeds PO reference data on startup
curl -s localhost:8000/health               # {"status":"ok","database":true,...}
```

## Chat

`POST /chat` (multipart): `message` (text), `conversation_id` (optional), `invoice`
and/or `po` file parts. Returns a natural-language `message` plus a structured
`decision` on processing turns.

```bash
# invoice whose PO is on file (seeded PO-54872)
curl -s -X POST localhost:8000/chat \
  -F "message=Please process this invoice." \
  -F "invoice=@samples/invoice.pdf" | jq

# invoice + uploaded PO (extracted and stored)
curl -s -X POST localhost:8000/chat \
  -F "invoice=@samples/invoice.pdf" -F "po=@samples/po.pdf" | jq '.decision.matched_po.source'

# multi-turn: send invoice, then the PO in a later turn (reuse conversation_id)
```

`NEEDS_REVIEW` is a `200` outcome; `503` is a transient (provider/DB) failure.

## Test

```bash
pytest                       # in-memory SQLite; providers stubbed via AGENT_FACTORY
# or against a real Postgres test DB:
TEST_DATABASE_URL=postgresql+psycopg2://... pytest
```

## Layout

```
app/
  api/            # thin FastAPI handlers: /chat, /health
  agent/
    orchestrator.py   # builds the OpenAI agent + tools (AGENT_FACTORY test seam)
    conversation.py   # per-conversation agent registry + request-scoped context
    prompts.py        # ALL prompt text (orchestrator + extraction prompts)
    tools/            # extract_document, po_lookup, persistence, math
  services/       # pdf_service, extraction_service (Gemini), decision_service
  db/             # database, models, repository, seed
alembic/          # migrations (0001_initial creates the schema)
data/             # seed CSVs (POs, vendors, line items)
tests/            # unit + integration (fake agent, no live providers)
```
