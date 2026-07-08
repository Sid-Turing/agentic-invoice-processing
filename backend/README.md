# Backend — Agentic Invoice Processing

FastAPI service. A single **orchestrator agent** (OpenAI) drives every chat turn
with five tools: `extract_document` (Gemini vision), `lookup_purchase_order` (DB
read), `store_purchase_order` + `store_decision` (DB write), `calculate`
(deterministic math). Validation and invoice↔PO reconciliation are the agent's
reasoning, not hardcoded steps. PostgreSQL via SQLAlchemy 2.0; schema managed by
Alembic; connection from `DATABASE_URL`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # OPENAI_API_KEY, GEMINI_API_KEY, DATABASE_URL (+ optional model ids)

docker run -d --name aip-pg -e POSTGRES_USER=invoice -e POSTGRES_PASSWORD=invoice \
  -e POSTGRES_DB=invoices -p 5434:5432 postgres:16
alembic upgrade head        # create the 4 tables

uvicorn app.main:app --port 8010   # seeds PO reference data on startup
pytest                             # unit + integration (providers stubbed, in-memory SQLite)
```

Needs **poppler** (`brew install poppler` / `apt-get install poppler-utils`).

## Endpoints

- `POST /chat` — multipart `message`, optional `conversation_id`, `invoice`, `po` →
  natural-language reply + structured `decision` (verdict, reasons, per-check trace,
  matched PO). `NEEDS_REVIEW` is a 200 outcome; `503` = transient provider/DB error.
- `POST /chat/stream` — same inputs, SSE stream (`meta`/`tool`/`tool_result`/`token`/`decision`/`done`).
- `GET /health` · read APIs: `GET /invoices`, `/invoices/{id}`, `/summary`,
  `/purchase-orders`, `/purchase-orders/{no}`, `/vendors` (read-only).

```bash
curl -s -X POST localhost:8010/chat -F "message=process this" \
  -F 'invoice=@sample.pdf;type=application/pdf' | jq
```

## Layout

```
app/
  api/        chat.py (/chat, /chat/stream), health.py, reports.py (read APIs)
  agent/      orchestrator.py, conversation.py, prompts.py, tools/
  services/   pdf_service, extraction_service (Gemini), decision_service, reporting_service
  db/         database, models, repository, read_repository, seed
  schemas/    Pydantic models
alembic/      migrations   ·   data/  seed CSVs   ·   tests/  unit + integration
```

CORS is open for the local frontend. Config (keys, model ids, `DATABASE_URL`,
tolerances, `HIGH_VALUE_THRESHOLD`) comes from env — see `app/config.py`.
