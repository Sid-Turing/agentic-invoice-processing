# Tasks: Read & Reporting Surface

**Input**: Design documents from `specs/002-read-reporting/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: REQUIRED (TDD). Backend read logic (reporting service, read repository)
and every read endpoint get tests before implementation, over an in-memory SQLite
store seeded with labelled `processed_invoices` + reference rows. Frontend: lint +
build + screenshots (no FE unit harness).

**Organization**: By user story. US1 (P1) is a complete, independently testable MVP
(history list + invoice detail). US2 (dashboard) and US3 (PO/vendor browsers) layer on.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- Paths are under the monorepo: `backend/…`, `frontend/…`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies + shared test fixtures for reporting.

- [ ] T001 Add `react-router-dom` to `frontend/package.json` dependencies (and `npm install`)
- [ ] T002 [P] Add a seeded-reporting fixture to `backend/tests/conftest.py`: a helper that inserts a labelled set of `processed_invoices` rows (mixed verdicts, varied `extracted_invoice` due dates/amounts/vendors, some undated) plus the CSV-seeded PO/vendor reference data, for reuse across reporting tests

**Checkpoint**: `npm install` succeeds; the seeded-reporting fixture imports and populates an in-memory DB.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schemas, read repository, and the pure reporting service that every
story depends on. **No user-story phase can begin until this is complete.**

### Schemas (contracts-first)

- [ ] T003 [P] Write schema tests in `backend/tests/unit/test_reports_schemas.py` (list/detail/summary/aging/priority/PO/vendor response shapes; per-run grain; enum buckets)
- [ ] T004 Implement `backend/app/schemas/reports.py` (`InvoiceListRow`, `InvoiceListResponse`, `InvoiceDetailResponse`, `AgingBucket`, `PriorityItem`, `SummaryResponse`, `PurchaseOrderListRow`, `PurchaseOrderListResponse`, `PurchaseOrderDetailResponse`, `VendorRow`, `VendorListResponse`) per data-model.md, reusing 001's `Decision`/`ExtractedInvoice`/`PurchaseOrder`

### Config

- [ ] T005 [P] Add `HIGH_VALUE_THRESHOLD` (default 3000) and reporting page-size defaults to `backend/app/config.py`

### Read repository (data-access, read-only)

- [ ] T006 Write repository tests in `backend/tests/unit/test_read_repository.py` against seeded in-memory SQLite: `list_processed_invoices` (verdict filter + `created_at` window + order desc), `get_processed_invoice(record_id)` (found/None), `list_purchase_orders`/`get_purchase_order_by_number`, `list_vendors`
- [ ] T007 Implement `backend/app/db/read_repository.py` (SQL reads only — verdict/`created_at` filters + `ORDER BY created_at DESC`; record-by-id; PO list/by-number reusing 001's mapping; vendor list). No writes.

### Reporting service (pure logic, the crux)

- [ ] T008 Write reporting-service tests in `backend/tests/unit/test_reporting_service.py`: build list rows from records; case-insensitive search over invoice#/vendor/PO; pagination (page/page_size/total); date parsing → aging buckets (incl. `undated`); priority (high-value AND overdue/due-soon, with reason labels); summary counts + total-approved (per-run, no dedup)
- [ ] T009 [P] Implement `backend/app/services/reporting_service.py` (pure functions: `to_list_row`, `apply_search`, `paginate`, `bucket_aging`, `derive_priority`, `build_summary`) parsing `extracted_invoice` JSON; "today" from server local date; make T008 pass

**Checkpoint**: T003/T006/T008 pass; schemas, repo, and service are ready.

---

## Phase 3: User Story 1 — History list + invoice detail (Priority: P1) 🎯 MVP

**Goal**: Browse all processed invoices (filter/search/paginate) and open any one to its full decision.

**Independent test**: With the seeded set, `GET /invoices` returns paginated rows newest-first; `verdict`/`window`/`q` filters return the right subset; `GET /invoices/{id}` returns the full decision; unknown id → 404. In the UI, the History page lists records and a row opens the detail page.

- [ ] T010 [P] [US1] Write `backend/tests/integration/test_reports_api.py::invoices_list` (pagination, verdict filter, window filter, `q` search, empty/no-match, 422 on bad page_size)
- [ ] T011 [P] [US1] Write `backend/tests/integration/test_reports_api.py::invoice_detail` (found → full decision; unknown id → 404)
- [ ] T012 [US1] Implement `GET /invoices` and `GET /invoices/{record_id}` in `backend/app/api/reports.py` (thin; delegate to read_repository + reporting_service); register the router in `backend/app/main.py`
- [ ] T013 [P] [US1] Add read helpers `getInvoices(params)` and `getInvoice(recordId)` to `frontend/src/api.js`
- [ ] T014 [US1] Refactor `frontend/src/App.jsx` into a nav shell (`Sidebar` + `<Routes>`); move the existing chat UI into `frontend/src/pages/ChatPage.jsx` unchanged; add `frontend/src/components/Sidebar.jsx`; wrap app in `<BrowserRouter>` in `frontend/src/main.jsx`
- [ ] T015 [US1] Implement `frontend/src/pages/HistoryPage.jsx` (table: invoice#, vendor, amount, verdict, PO source, processed time; verdict + timeframe filters; search box; pagination; row → `/invoices/:recordId`; empty/no-result/error states)
- [ ] T016 [US1] Implement `frontend/src/pages/InvoiceDetailPage.jsx` + `frontend/src/components/LineItemsTable.jsx` (fetch detail; render verdict via existing `DecisionCard`, reasons, check trace, extracted header/vendor/customer, line-items table with qty×price mismatch flag; not-found state)

**Checkpoint**: US1 backend tests pass; History → detail navigation works end-to-end (MVP demoable).

---

## Phase 4: User Story 2 — Dashboard (Priority: P2)

**Goal**: Summary metrics + aging breakdown + high-value/overdue priority list.

**Independent test**: `GET /summary` returns counts, total-approved, processed-today, six aging buckets, and the priority list — matching the seeded data; the Dashboard page renders cards, aging, and priority, with an empty-state at zero data.

- [ ] T017 [P] [US2] Write `backend/tests/integration/test_reports_api.py::summary` (counts + total-approved match seeded rows; aging bucket tallies; priority membership + reason labels; empty system → zeros)
- [ ] T018 [US2] Implement `GET /summary` in `backend/app/api/reports.py` (delegate to `reporting_service.build_summary`)
- [ ] T019 [P] [US2] Add `getSummary()` to `frontend/src/api.js`
- [ ] T020 [US2] Implement `frontend/src/pages/DashboardPage.jsx` (summary stat cards, aging breakdown bars, priority list with reason tags; empty/error states)

**Checkpoint**: US1 + US2 pass; dashboard reflects the store.

---

## Phase 5: User Story 3 — Purchase orders & vendors browsers (Priority: P3)

**Goal**: Browse the PO reference data (list + detail) and vendors (list).

**Independent test**: `GET /purchase-orders` lists seeded POs (searchable/paginated); `GET /purchase-orders/{no}` returns line items (unknown → 404); `GET /vendors` lists vendors; the PO and Vendor pages render these.

- [ ] T021 [P] [US3] Write `backend/tests/integration/test_reports_api.py::po_and_vendors` (PO list + search; PO detail incl. line items; unknown PO → 404; vendor list + name search)
- [ ] T022 [US3] Implement `GET /purchase-orders`, `GET /purchase-orders/{po_number}`, `GET /vendors` in `backend/app/api/reports.py`
- [ ] T023 [P] [US3] Add `getPurchaseOrders(params)`, `getPurchaseOrder(poNumber)`, `getVendors(params)` to `frontend/src/api.js`
- [ ] T024 [P] [US3] Implement `frontend/src/pages/PurchaseOrdersPage.jsx` (list + search + pagination + detail with line items)
- [ ] T025 [P] [US3] Implement `frontend/src/pages/VendorsPage.jsx` (list + name search)

**Checkpoint**: all three stories pass independently and together.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Write the read-only invariant test in `backend/tests/integration/test_reports_api.py::read_only` (capture row counts, exercise all six endpoints, assert `processed_invoices`/PO/vendor counts unchanged — SC-008)
- [ ] T027 [P] Map DB-unavailable to `503` and add consistent empty/no-result handling across `backend/app/api/reports.py` (FR-017)
- [ ] T028 [P] Add nav styling for the sidebar/shell in `frontend/src/styles.css` (active-route highlight; list/table/dashboard styles)
- [ ] T029 Coverage validation: `cd backend && pytest --cov=app` ≥ 80% on new read logic (`services/reporting_service.py`, `db/read_repository.py`, `api/reports.py`); document any exclusions
- [ ] T030 Final validation: backend `curl` smokes from quickstart.md against the running server; `cd frontend && npm run build`; capture screenshots of History, an Invoice detail, and the Dashboard (VAL-002)

---

## Dependencies & Execution Order

- **Setup (P1)** → **Foundational (P2)** → **US1 (P3)** → **US2 (P4)** → **US3 (P5)** → **Polish (P6)**.
- Foundational blocks all stories. Within it: schemas (T003/T004) and config (T005) are independent; the read repository (T006/T007) precedes the endpoints; the reporting service (T008/T009) precedes any endpoint that aggregates.
- **US1** depends only on Foundational and is the MVP. **US2** and **US3** depend on US1's router + `api.js`/shell being in place (T012/T014) but are independent of each other. The backend endpoints across US1–US3 all live in `backend/app/api/reports.py`, so those specific implementation tasks (T012, T018, T022) touch the same file and run sequentially; their tests and the frontend tasks are `[P]`.
- TDD: each test task precedes its implementation and must fail first.

## Parallel Execution Examples

- **Foundational**: T003 (schema tests) ∥ T005 (config) ∥ T006 (repo tests) ∥ T008 (service tests) can be written together; then T004, T007, T009.
- **US1**: T010 ∥ T011 (backend tests) and T013 (api.js) in parallel before T012/T014–T016.
- **US2/US3 frontend**: T019/T020 and T023/T024/T025 are `[P]` across different page files.
- **Polish**: T026, T027, T028 in parallel.

## Implementation Strategy

- **MVP = Phase 1 + 2 + 3 (US1)** — the history list + invoice detail, the biggest gap; ship/demo here.
- Add **US2** (dashboard) and **US3** (PO/vendor browsers) as independent increments.
- **Polish** (read-only invariant, 503 handling, nav styling, coverage, screenshots) last.
- Total: **30 tasks** — Setup 2, Foundational 7, US1 7, US2 4, US3 5, Polish 5.
