# Research: Read & Reporting Surface

**Feature**: `002-read-reporting` | **Date**: 2026-07-08

Reporting is a read layer over feature 001's `processed_invoices` results and the
seeded PO/vendor reference tables. No external unknowns (no new providers/frameworks).
Decisions below resolve how to query, aggregate, and present that data.

---

## R1 — Query strategy: SQL on columns + Python derivation over JSON (the crux)

**Decision**: `processed_invoices` stores `invoice_number`, `verdict`,
`matched_po_number`, `matched_po_source`, `created_at` as **real columns**, but the
vendor name, total amount, currency, and due date live inside the **`extracted_invoice`
JSON** column. So: push the portable, indexable filters to SQL (verdict equality,
`created_at` time window, ordering by `created_at DESC`), then a pure reporting
service parses `extracted_invoice` JSON in Python to derive amount/currency/vendor/
due-date, apply text search (invoice#/vendor/PO), compute aging/priority/summary, and
paginate.

**Rationale**: Keeps the query **dialect-portable** (Postgres runtime + SQLite in
tests) — no `JSONB`-specific operators. Avoids a schema migration and avoids touching
feature 001's write path. Correct for the existing 26 rows (whose JSON is already
populated). At the spec's alpha scale (hundreds–thousands of records) parsing the
verdict/time-filtered slice in Python is well within the SC-002 2-second target.

**Alternatives rejected**: (a) **Denormalize** vendor/amount/due-date into columns via
a migration + populate them in 001's `persist_decision` — more scalable and SQL-native,
but couples 002 to 001's write path, needs a backfill for existing rows, and adds a
migration to a read-only feature. Documented as the **swap point** when volume grows.
(b) Postgres `JSONB` path queries — breaks SQLite test portability (001's testing model).

## R2 — Pagination: offset/limit with page + page_size

**Decision**: Simple `page` (1-based) + `page_size` (default 25, max 100). Responses
return `items`, `total` (count for the current filter), `page`, `page_size`.

**Rationale**: Trivial to implement and test, and adequate at alpha scale. Cursor
pagination is unnecessary complexity here.

**Alternatives rejected**: Cursor/keyset pagination — better for very large or
concurrently-mutating sets; neither applies to this local, low-write reporting surface.

## R3 — Aging, priority, and "today" semantics

**Decision**: Derive from each record's `extracted_invoice.due_date` (string, `YYYY-MM-DD`)
and `total_amount`, relative to the **server's current local date**. Buckets:
`overdue` (due < today), `due_today`, `due_1_7`, `due_8_14`, `due_15_plus`, and
`undated` (missing/unparseable due date). **Priority** = `total_amount` above a
configurable threshold (**default 3000**) AND (overdue OR due within 7 days); each
priority item is labeled with reasons (`high_value`, `overdue`, `due_soon`). Undated or
threshold-below records are excluded from priority. All computed at **per-run grain**
(clarification): each record counts once, no de-duplication.

**Rationale**: Mirrors the original app's aging/priority semantics and 001's
tolerances-as-config style. Robust date parsing (fallback to `undated`) satisfies the
missing-field edge case.

**Alternatives rejected**: Basing aging on invoice date rather than due date (less
meaningful for payables); a fixed threshold (config is cheap and matches 001).

## R4 — Search semantics

**Decision**: Case-insensitive substring match across `invoice_number`, vendor name,
and `matched_po_number`. Applied in the reporting service after the SQL filter.

**Rationale**: Matches user expectation ("type part of a number/name"); simple and
portable. Alpha scale makes in-Python matching acceptable.

## R5 — Detail response reuses the stored Decision shape

**Decision**: `GET /invoices/{record_id}` returns the persisted decision as-is —
`record_id`, `created_at`, `conversation_id`, `verdict`, `reasons`, `checks`,
`explanation`, `extracted_invoice`, `matched_po` — reusing feature 001's `Decision`
schema plus record metadata, rather than inventing a new shape.

**Rationale**: The detail view needs exactly what 001 persisted; reusing the schema
keeps one source of truth and lets the React `DecisionCard` render it unchanged.

## R6 — Frontend routing & shell

**Decision**: Introduce `react-router-dom` and a nav shell (sidebar) with routes:
**Chat** (the existing turn UI, refactored into a page), **History** (list),
**Invoice detail** (`/invoices/:recordId`), **Dashboard**, **Purchase Orders**
(+ detail), **Vendors**. A small `api.js` gains typed read helpers per endpoint.

**Rationale**: The app is currently a single page; multiple read screens need routing.
`react-router-dom` is the standard, minimal choice for a Vite React app and is the one
new frontend dependency.

**Alternatives rejected**: Hand-rolled hash/state routing (reinvents the wheel);
a heavier framework (unwarranted).

## R7 — Read-only guarantee

**Decision**: All six endpoints are `GET`; the reporting service and read repository
contain no `INSERT`/`UPDATE`/`DELETE`. A test asserts stored row counts are unchanged
after exercising every read view (SC-008).

**Rationale**: Enforces SEC-002 mechanically, not just by convention.

---

## Dependencies

- **Backend**: no new runtime dependencies (reuses FastAPI, SQLAlchemy, Pydantic).
- **Frontend**: one new dependency — `react-router-dom` (MIT).
- No new database tables, no migration, no change to feature 001's write path.
