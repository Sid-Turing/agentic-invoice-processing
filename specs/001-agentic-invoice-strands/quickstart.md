# Quickstart: Agentic Invoice Processing (Strands)

**Feature**: `001-agentic-invoice-strands` | Local run + smoke test

## Prerequisites

- Python 3.11+
- **PostgreSQL** (local is fine, e.g. `docker run -e POSTGRES_USER=invoice -e POSTGRES_PASSWORD=invoice -e POSTGRES_DB=invoices -p 5432:5432 postgres:16`)
- `poppler` (system dependency for `pdf2image`) — macOS: `brew install poppler`;
  Debian/Ubuntu: `apt-get install poppler-utils`
- An **OpenAI API key** (orchestrator) and a **Google Gemini API key** (extraction)

## Setup

```bash
cd agentic-invoice-processing
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # installs strands-agents[openai,gemini], fastapi, sqlalchemy, ...

cp .env.example .env             # then edit:
#   OPENAI_API_KEY=sk-...
#   GEMINI_API_KEY=...
#   OPENAI_MODEL_ID=gpt-4o-mini                                   (optional)
#   GEMINI_MODEL_ID=gemini-2.0-flash                              (optional)
#   DATABASE_URL=postgresql+psycopg2://invoice:invoice@localhost:5432/invoices
#   TAX_RATE=0.09125  SUPPORTED_CURRENCIES=USD                    (optional)
```

## Create the schema (Alembic) + seed

```bash
alembic upgrade head             # creates the 4 tables from scratch in DATABASE_URL
```

The three PO CSVs (`purchase_orders_data.csv`, `po_vendors_data.csv`,
`purchase_order_line_items_data.csv`) ship under `data/` and seed the reference
tables on first startup (skipped if rows already exist). Swapping databases is
env-only — point `DATABASE_URL` elsewhere and re-run `alembic upgrade head`.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

`GET /health` should return `{"status":"ok","providers":{"openai":true,"gemini":true},"database":true}`.

## Smoke test the flow

**1. Invoice with a PO already on file (lookup path)** — the seeded data includes
`PO-54872`. Upload an invoice that references it:

```bash
curl -s -X POST http://localhost:8000/chat \
  -F "message=Please process this invoice." \
  -F "invoice=@samples/invoice_po54872.pdf" | jq
```
Expect `decision.verdict` = `APPROVED` (or `NEEDS_REVIEW` with a reason if you
tampered with a total), `decision.matched_po.source` = `"database"`, and a natural
-language `message`. Note the returned `conversation_id`.

**2. Upload a PO in the same turn (upload → write path)**:

```bash
curl -s -X POST http://localhost:8000/chat \
  -F "message=Here is the invoice and its PO." \
  -F "invoice=@samples/invoice_new.pdf" \
  -F "po=@samples/po_new.pdf" | jq '.decision.matched_po.source'   # -> "uploaded"
```
The uploaded PO is extracted and persisted; re-running `lookup` for that PO number
now finds it.

**3. Multi-turn refinement (PO arrives later)** — reuse the `conversation_id`:

```bash
# turn 1: invoice only, no PO number resolvable -> reconciliation skipped
curl -s -X POST http://localhost:8000/chat \
  -F "message=Process this." -F "invoice=@samples/invoice_nopo.pdf" | jq '.conversation_id, .decision.verdict'

# turn 2: supply the PO; agent reconciles the earlier invoice without re-upload
curl -s -X POST http://localhost:8000/chat \
  -F "conversation_id=<from turn 1>" \
  -F "message=Here's the PO for that invoice." -F "po=@samples/po_match.pdf" | jq '.decision'

# turn 3: plain-text follow-up, no attachment
curl -s -X POST http://localhost:8000/chat \
  -F "conversation_id=<same>" -F "message=Why did it need review?" | jq '.message, .decision'  # decision == null
```

## Validate

```bash
# import / startup check (VAL-001)
python -c "import app.main"

# tests + coverage (VAL-003/004) — providers stubbed; schema on in-memory SQLite
# (portable ORM types), or set TEST_DATABASE_URL for a real Postgres test DB
pytest --cov=app --cov-report=term-missing
```

Integration tests cover: single-turn PO-on-file, single-turn uploaded-PO,
multi-turn PO-arrives-later, a non-processing message, and `/health` — using
fixture documents, a seeded test DB, and a deterministic fake agent injected via
the `AGENT_FACTORY` seam (no live provider calls in CI).
