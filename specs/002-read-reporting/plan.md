# Implementation Plan: Read & Reporting Surface

**Branch**: `002-read-reporting` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-read-reporting/spec.md`

## Summary

Add a read-only reporting surface over feature 001's data: six `GET` endpoints
(`/invoices`, `/invoices/{id}`, `/summary`, `/purchase-orders`,
`/purchase-orders/{no}`, `/vendors`) plus React screens (history list, invoice
detail, dashboard with aging/priority, PO browser, vendor list) behind a nav shell.
No new tables, no migration, no change to 001's write path — key filters run in SQL
on existing columns and vendor/amount/aging/priority are derived in Python from the
`extracted_invoice` JSON at per-run grain. See [research.md](./research.md) (R1
query strategy is the crux).

## Technical Context

**Language/Version**: Python 3.11+ (backend), React 18 + Vite (frontend, JS)
**Primary Dependencies**: Backend — FastAPI, SQLAlchemy 2.0, Pydantic (all existing; **no new backend deps**). Frontend — React, Vite + **`react-router-dom`** (one new dep, MIT)
**Storage**: Reads existing PostgreSQL tables from feature 001 (`processed_invoices` + PO/vendor reference); **no schema change, no migration, no writes**
**Testing**: `pytest` + FastAPI `TestClient` over in-memory SQLite (portable ORM types, seeded fixtures); frontend `npm run build` + lint + screenshots
**Target Platform**: Local single-user service; same monorepo (`backend/` + `frontend/`)
**Project Type**: Full-stack read layer (backend read API + React screens)
**Performance Goals**: A page of history results within ~2 s at hundreds–thousands of records (SC-002)
**Constraints**: Strictly read-only (SEC-002, no mutation endpoints); no raw-file storage/viewer (SEC-003); no auth (single user); dialect-portable queries (Postgres runtime, SQLite tests)
**Scale/Scope**: Alpha/local; 6 endpoints + ~5 React screens; ~10–14 new modules; est. < 1500 added lines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

> Same standalone monorepo as 001. Humain-constitution *principles* apply as good
> practice; platform specifics (React-in-`src/`, `develop` PRs, platform secrets
> service) are mapped to this repo's equivalents.

- **Persona-Scoped Product Value**: PASS. Single persona (finance operator). P1
  (US1 history + detail) is independently demonstrable. Out-of-scope is explicit
  (no mutations, no doc viewer, no email, no auth).
- **Branch/PR Discipline**: PASS (adapted). One logical change on a `feat/…` branch,
  Conventional Commits, est. < 1500 lines (well under 5000; `specs/` excluded).
- **Security, Secrets, Tenant Isolation**: PASS. No auth/tenants by design (SEC-001).
  **No writes** (SEC-002) — enforced by a read-only invariant test (SC-008). No raw
  files stored/served (SEC-003). No new secrets; reuses `DATABASE_URL` from env.
- **Testable Increment Quality**: PASS. `tasks.md` orders tests before implementation
  for the reporting service (pure list/filter/paginate, aging/priority, summary) and
  the read repository; every endpoint gets an integration test over a seeded store.
  Coverage ≥ 80% on new backend read logic. Frontend: lint + build + screenshots.
- **Minimal Maintainable Change**: PASS. Functional-first — reporting logic is pure
  functions in a service; repository is thin data-access; handlers are thin. Only new
  dep is `react-router-dom` (justified: multi-screen routing; MIT). No backend deps,
  no migration.
- **Reusable-Core-First**: PASS. Read logic in `app/services/reporting_service.py`
  (pure, testable without HTTP) + `app/db/read_repository.py`; `app/api/reports.py`
  handlers delegate. Frontend logic in `src/api.js` + small page components.
- **HTTP API Schema Contracts**: PASS. All six response schemas are defined in
  [data-model.md](./data-model.md) / [contracts/](./contracts/) before implementation.
  Additive (new `GET` routes); no breaking changes to 001's `/chat`.

**Result**: All gates PASS. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/002-read-reporting/
├── plan.md              # This file
├── research.md          # R1 query strategy (crux) … R7 read-only guarantee
├── data-model.md        # Projection schemas over 001's tables (no new persistence)
├── quickstart.md        # Endpoint smoke + screen walkthrough
├── contracts/           # read-endpoints.md (6 GET endpoints)
└── tasks.md             # /speckit.tasks output (NOT created here)
```

### Source Code (monorepo)

```text
backend/app/
├── schemas/
│   └── reports.py              # InvoiceListRow/Response, InvoiceDetailResponse, SummaryResponse,
│                               # AgingBucket, PriorityItem, PurchaseOrder*List/Detail, Vendor* (new)
├── db/
│   └── read_repository.py      # list_processed_invoices(filters), get_by_record_id,
│                               # list_purchase_orders/get_po, list_vendors (read-only)
├── services/
│   └── reporting_service.py    # pure: build rows, search, paginate, aging/priority, summary
└── api/
    └── reports.py              # 6 GET routes; thin; delegate to service+repo; register in main.py

frontend/src/
├── main.jsx                    # add <BrowserRouter>
├── App.jsx                     # -> nav shell (sidebar) + <Routes>
├── api.js                      # + getInvoices/getInvoice/getSummary/getPurchaseOrders/getPurchaseOrder/getVendors
├── pages/
│   ├── ChatPage.jsx            # existing chat UI moved here (unchanged behaviour)
│   ├── HistoryPage.jsx         # list + filters + search + pagination
│   ├── InvoiceDetailPage.jsx   # /invoices/:recordId — reuses DecisionCard + line-items table
│   ├── DashboardPage.jsx       # summary cards + aging + priority
│   ├── PurchaseOrdersPage.jsx  # list + detail
│   └── VendorsPage.jsx         # list
└── components/
    ├── Sidebar.jsx             # nav: Chat, History, Dashboard, Purchase Orders, Vendors
    ├── DecisionCard.jsx        # (existing, reused on the detail page)
    └── LineItemsTable.jsx      # extracted line items with qty×price mismatch flag

backend/tests/
├── unit/test_reporting_service.py   # search/filter/paginate, aging/priority, summary (pure)
└── integration/test_reports_api.py  # all 6 endpoints over seeded SQLite + read-only invariant
```

**Structure Decision**: Purely additive to the existing monorepo. Backend gains a
`reports` router + reporting service + read repository (mirrors 001's
service/repository/handler layering); the frontend gains routing, a sidebar shell, and
per-screen pages, reusing the existing `DecisionCard`. No files from 001 are modified
except registering the new router in `app/main.py` and refactoring `App.jsx` into a
shell + `ChatPage` (behaviour unchanged).

## Local Validation Commands

- **Backend**: `python -c "import app.main"`; `uvicorn app.main:app --port 8010` then the
  `curl` smokes in [quickstart.md](./quickstart.md); `pytest --cov=app` (≥ 80% on new read logic).
- **Read-only invariant (SC-008)**: a test captures row counts, exercises every read
  endpoint, and asserts counts are unchanged.
- **Frontend**: `npm run build`; screenshots of History, an Invoice detail, and the Dashboard (VAL-002).

## Complexity Tracking

No constitution gate failed; no entries required.
