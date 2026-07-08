# Quickstart: Read & Reporting Surface

**Feature**: `002-read-reporting` | Local run + smoke test

Builds on the running feature-001 stack (backend on :8010, Postgres `aip-pg` :5434,
frontend on :5173). Process a few invoices via the chat first so there's data to report on.

## Backend

```bash
cd backend
# (venv + Postgres already set up from feature 001; schema via alembic upgrade head)
uvicorn app.main:app --port 8010
```

Smoke the read endpoints:
```bash
curl -s 'localhost:8010/invoices?page=1&page_size=10' | jq '.total, .items[0]'
curl -s 'localhost:8010/invoices?verdict=NEEDS_REVIEW&window=7d&q=synacktek' | jq '.total'
curl -s localhost:8010/invoices/<record_id> | jq '.verdict, .checks | length'
curl -s localhost:8010/summary | jq '{total_processed, approved_count, total_approved_amount, aging, priority}'
curl -s 'localhost:8010/purchase-orders?q=PO-54872' | jq '.items[0]'
curl -s localhost:8010/purchase-orders/PO-54872 | jq '.line_items | length'
curl -s localhost:8010/vendors | jq '.items'
```

## Frontend

```bash
cd frontend
npm install                 # picks up react-router-dom
npm run dev                 # http://localhost:5173
```

Navigate the sidebar:
- **Chat** — the existing processing UI (unchanged).
- **History** — table of processed invoices; filter by verdict/timeframe, search, paginate; click a row → **Invoice detail** (checks, reasons, extracted line items, matched PO).
- **Dashboard** — summary cards, aging breakdown, priority list.
- **Purchase Orders** — list + detail (line items).
- **Vendors** — list.

## Validate

```bash
# backend read tests (seeded store, no live providers needed)
cd backend && pytest -q -k "reports or reporting or read"
# read-only invariant: row counts unchanged after hitting every read view (SC-008)

# frontend
cd frontend && npm run build
```

Integration tests seed `processed_invoices` with labelled records and assert list
filtering/search/pagination, detail lookup + 404, summary counts, aging/priority
bucketing, and PO/vendor reads — all against an in-memory SQLite store.
