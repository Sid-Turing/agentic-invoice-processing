# Feature Specification: Read & Reporting Surface

**Feature Branch**: `002-read-reporting`
**Created**: 2026-07-08
**Status**: Draft
**Input**: User description: "Create the spec for the whole read/reporting side — the browse/history/detail/dashboard surface that sits on top of the invoices the agent has already processed (feature 001). Skip email-fetch. Read-only, full analytics (counts + totals + aging + priority), no original-document viewer."

## Context & Motivation

Feature 001 delivers the *processing* experience: a chat surface where the agent
extracts an invoice, validates/reconciles it, and persists a decision to a results
store. But there is currently **no way to look back**: every processed invoice is
written to storage, yet nothing lists, searches, or reports on them, and the chat
UI only shows the current session's turns. Purchase-order and vendor reference data
is likewise never surfaced.

This feature adds the **read/reporting side**: a browsable history of processed
invoices, a detail view for any one of them, a dashboard with summary metrics and
aging/priority analytics, and reference browsers for purchase orders and vendors.
It is strictly **read-only** — it reports on data produced by feature 001 and the
seeded reference data; it never mutates anything. It reuses the same monorepo
(backend API + React frontend).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse processed-invoice history and open a decision (Priority: P1)

An accounts-payable user opens a history view listing every invoice the agent has
processed, most recent first, with the key facts per row (invoice number, vendor,
amount, verdict, when). They filter and search to find one, click it, and see the
full decision: the extracted invoice, the per-check trace, the blocking reasons,
and (when reconciliation ran) the matched purchase order.

**Why this priority**: This is the single biggest gap today — decisions are stored
but invisible. A reviewer cannot act on `NEEDS_REVIEW`, audit an approval, or find a
past invoice at all. History + detail is the core of the reporting surface;
everything else is analytics or reference on top of it.

**Independent Test**: With several invoices already processed, open the history
list and confirm each appears with its verdict and can be opened to a detail view
showing its checks, reasons, extracted fields, and matched PO (or a clear
"no PO — reconciliation skipped"). Filtering to `NEEDS_REVIEW` shows only those.

**Acceptance Scenarios**:

1. **Given** N processed invoices exist, **When** the user opens the history view, **Then** all N are listed newest-first with invoice number, vendor, amount, currency, verdict, and processed time, paginated.
2. **Given** the history view, **When** the user filters by verdict `NEEDS_REVIEW` (or `APPROVED`), **Then** only matching records are shown and the count reflects the filter.
3. **Given** the history view, **When** the user searches by invoice number, vendor name, or PO number, **Then** only matching records are shown.
4. **Given** a record in the list, **When** the user opens it, **Then** the detail view shows the verdict, blocking reason codes, the full check-by-check trace (each pass/fail/skipped with its detail), the extracted invoice (header, amounts, tax, line items, vendor, customer), and the matched PO with its source when one was used.
5. **Given** a record id that does not exist, **When** its detail is requested, **Then** the system responds with a clear "not found" rather than an error page.

---

### User Story 2 - Dashboard with summary metrics and aging/priority analytics (Priority: P2)

A finance operator opens a dashboard that summarizes processing at a glance: how
many invoices have been processed, how many approved vs. needing review, the total
approved amount, and recent activity. It also shows an **aging** breakdown of
invoices by due date and a **priority** list highlighting high-value and overdue
invoices that warrant attention.

**Why this priority**: Once history exists, the dashboard turns it into insight —
the "what needs my attention and how are we doing" view. Valuable, but it depends on
the underlying records being browsable (US1) and is a layer on top rather than the
core need.

**Independent Test**: With a mix of processed invoices (some approved, some
needing review, varying due dates and amounts), open the dashboard and confirm the
summary counts and total approved amount match the stored data, the aging buckets
tally correctly from due dates, and the priority list surfaces the high-value /
overdue invoices.

**Acceptance Scenarios**:

1. **Given** processed invoices exist, **When** the dashboard loads, **Then** it shows total processed, approved count, needs-review count, total approved amount, and a count processed today — each consistent with the stored records.
2. **Given** invoices with due dates, **When** the dashboard loads, **Then** an aging breakdown groups them into overdue / due today / due in 1–7 / 8–14 / 15+ days (invoices lacking a due date are grouped as "undated").
3. **Given** invoices, **When** the dashboard loads, **Then** a priority list shows invoices that are high value (above a configurable threshold, default 3000) AND overdue or due within 7 days, labeled with the reason (high value, overdue, due soon).
4. **Given** an empty system (nothing processed yet), **When** the dashboard loads, **Then** it shows zeroed metrics and empty states rather than errors.

---

### User Story 3 - Browse purchase orders and vendors (Priority: P3)

A user browses the purchase orders and vendors held in the reference data — a list
of POs (number, vendor, totals, dates) with a detail view (header + line items),
and a list of vendors (name, address, tax id). This is the reference context the
agent reconciles against.

**Why this priority**: Useful context and closes the parity gap with the original
app, but it is reference lookup rather than the core invoice-reporting need, so it
comes last.

**Independent Test**: With the reference data seeded, open the PO list and confirm
each PO shows its number, vendor, and total; open one to see its line items; open
the vendor list and confirm vendors show name, address, and tax id.

**Acceptance Scenarios**:

1. **Given** seeded purchase orders, **When** the user opens the PO list, **Then** each PO is listed with number, vendor name, total amount, currency, and dates, searchable by PO number and paginated.
2. **Given** a PO, **When** the user opens it, **Then** the detail shows its header (dates, totals, currency, status), vendor, and line items (description, quantity, unit price, total).
3. **Given** seeded vendors, **When** the user opens the vendor list, **Then** each vendor shows name, address, and tax id, searchable by name.

---

### Edge Cases

- **Empty system**: history, dashboard, PO, and vendor views all render clean empty states (no records) rather than spinners or errors.
- **Large history**: listing remains responsive with many records via pagination; the UI never loads the entire table at once.
- **Missing/partial extracted fields**: a record whose extracted invoice lacks amount, vendor, or due date still lists and opens; missing values render as "—" (and, for due date, land in the "undated" aging bucket).
- **Record not found**: requesting a detail for an unknown id returns a clear not-found result.
- **Filter/search with no matches**: shows an explicit "no results" state and a zero count.
- **Currency**: amounts display with the currency stored on the record; mixed currencies across records are shown per-record (no forced conversion).
- **Backend/database unavailable**: read views surface a retryable error state, distinct from an empty result.

### Scope and Persona Impact *(mandatory)*

- **Affected Persona(s)**: Accounts-payable / finance operator (browses history, reads decisions, views the dashboard and reference data).
- **In Scope**: A read-only history list of processed invoices (filter by verdict and timeframe, search, pagination, newest-first); an invoice detail view (extracted invoice, check trace, reasons, matched PO); a dashboard (summary counts, total approved amount, processed-today, an aging breakdown, and a high-value/overdue priority list); a purchase-order list + detail; a vendor list; the navigation shell tying these screens together alongside the existing chat screen.
- **Out of Scope**: Any mutation of data (no delete, edit, re-run, or approve actions — strictly read-only); an original-document / PDF viewer (raw uploaded files are intentionally not stored — see 001); email-fetch/ingestion screens; user accounts / auth / multi-tenancy; exporting/downloading reports; currency conversion; real-time push updates (views refresh on load / manual refresh, not via a live socket); editing reference data (POs/vendors remain managed by 001's processing path only).
- **Tenant/Role Impact**: None — single-user local tool, consistent with feature 001. No authorization boundaries introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST list processed invoices, newest-first, each row showing at least: invoice number, vendor name, total amount, currency, verdict (`APPROVED` / `NEEDS_REVIEW`), matched-PO source (or none), and processed timestamp.
- **FR-002**: The history list MUST support pagination so the full set is never loaded at once, and MUST report the total count for the current filter.
- **FR-003**: The history list MUST support filtering by verdict and by processed-time window (e.g. today, last 7/30 days, all time).
- **FR-004**: The history list MUST support text search matching invoice number, vendor name, or PO number.
- **FR-005**: The system MUST provide a detail view for a single processed-invoice record, showing the verdict, blocking reason codes, the full check-by-check trace (each check's id, status pass/fail/skipped, and detail), the extracted invoice (header fields, amounts, tax, line items, vendor, customer), and the matched purchase order with its source when reconciliation ran.
- **FR-006**: Requesting the detail of a non-existent record MUST return a clear not-found result, not a server error.
- **FR-007**: The system MUST provide summary metrics over all processed invoices: total processed, approved count, needs-review count, total approved amount, and count processed today.
- **FR-008**: The system MUST provide an aging breakdown of processed invoices by due date into buckets: overdue, due today, due in 1–7 days, 8–14 days, 15+ days, and undated (missing due date).
- **FR-009**: The system MUST provide a priority list of processed invoices that are high value (above a configurable amount threshold, default 3000) AND overdue or due within 7 days, each labeled with the reason(s): high value, overdue, due soon.
- **FR-010**: The system MUST provide a purchase-order list (PO number, vendor, total, currency, dates), searchable by PO number and paginated, and a PO detail view including its line items.
- **FR-011**: The system MUST provide a vendor list (name, address, tax id), searchable by name.
- **FR-012**: All reporting surfaces MUST be read-only; the feature MUST NOT expose any create, update, or delete operation.
- **FR-013**: All list, detail, dashboard, PO, and vendor views MUST render clean empty states when there is no data, and an explicit no-results state when a filter/search matches nothing.
- **FR-014**: Records or fields with missing values (e.g. no amount, vendor, or due date) MUST still list and open, rendering absent values as a neutral placeholder.
- **FR-015**: The reporting surface MUST be reachable via navigation alongside the existing chat screen, so a user can move between processing and reviewing.
- **FR-016**: Read requests MUST reflect the current stored state at load time; a manual refresh MUST re-fetch the latest (no stale cache that hides newly processed invoices).
- **FR-017**: When the underlying data store is unreachable, read views MUST show a retryable error state distinct from an empty result.

### API Schema Requirements *(mandatory when HTTP endpoints are added or changed)*

- **SCH-001**: `GET /invoices` (processed-invoice list) MUST accept query params for pagination, verdict filter, time window, and search text, and return a list response schema (`InvoiceListResponse`) of summary rows plus a total count and paging info.
- **SCH-002**: `GET /invoices/{record_id}` MUST return an invoice detail schema (`InvoiceDetailResponse`) with the decision, check trace, extracted invoice, and matched PO; unknown id → 404.
- **SCH-003**: `GET /summary` MUST return a dashboard schema (`SummaryResponse`) with the counts, total approved amount, processed-today count, the aging buckets, and the priority list.
- **SCH-004**: `GET /purchase-orders` MUST return a PO list schema (`PurchaseOrderListResponse`) (paginated, searchable), and `GET /purchase-orders/{po_number}` MUST return a PO detail schema (`PurchaseOrderDetailResponse`) including line items; unknown number → 404.
- **SCH-005**: `GET /vendors` MUST return a vendor list schema (`VendorListResponse`) (searchable). Exact model names are finalized in the plan.

### Security and Data Requirements *(mandatory when auth, tenants, secrets, or state are touched)*

- **SEC-001**: No authentication or tenant model is introduced; consistent with feature 001's single-user posture. Read endpoints expose the same local data set.
- **SEC-002**: The feature performs **no writes** of any kind — no mutation endpoints, no deletes. It reads the processed-invoice results and the reference tables only.
- **SEC-003**: No raw uploaded documents are stored or served (unchanged from 001); detail views present extracted data and decisions only, never the source file.

### Key Entities *(include if feature involves data)*

- **Processed Invoice (record)**: A previously produced decision — record id, processed timestamp, verdict, reason codes, check trace, the extracted invoice, and matched-PO reference (number + source). The primary entity of the reporting surface (produced by feature 001).
- **Invoice Summary (list row)**: The compact projection shown in the history list — invoice number, vendor, amount, currency, verdict, matched-PO source, processed time — derived from a Processed Invoice.
- **Summary Metrics**: Aggregate counts and totals over all Processed Invoices — totals, approved/needs-review counts, total approved amount, processed-today.
- **Aging Bucket**: A due-date grouping (overdue / due today / 1–7 / 8–14 / 15+ / undated) with its invoice count and amount.
- **Priority Item**: A processed invoice flagged as high-value-and-overdue/due-soon, with its reason label(s).
- **Purchase Order** / **PO Line Item** / **Vendor**: Reference records (from 001's seeded data) surfaced for browsing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can find any previously processed invoice by scrolling, filtering, or searching the history and open it to its full decision — a task that is impossible today.
- **SC-002**: The history list returns and paginates results quickly at expected local scale (hundreds–thousands of records) without loading the entire set at once; a page of results appears within about 2 seconds.
- **SC-003**: Dashboard summary counts and total approved amount exactly match the stored records for a labelled data set (verified by cross-checking against the underlying rows).
- **SC-004**: Aging buckets and the priority list correctly classify a labelled set of invoices with known due dates and amounts (100% correct bucketing for the test set).
- **SC-005**: Verdict filter, time-window filter, and text search each return exactly the expected subset for a labelled data set, and combine correctly.
- **SC-006**: Every invoice detail view shows the verdict, all reason codes, every check in the trace, the extracted line items, and the matched PO (or an explicit "no PO") — with no missing sections.
- **SC-007**: Empty, no-match, missing-field, not-found, and store-unavailable conditions each render a clear, non-broken state (no blank screens or unhandled errors).
- **SC-008**: The reporting surface performs zero writes — verified by confirming stored data (record counts, PO/vendor rows) is unchanged after exercising every read view.

### Validation Expectations

- **VAL-001**: Backend — the read endpoints start and return valid responses against a seeded data set (startup/import check plus endpoint smoke; exact commands in the plan).
- **VAL-002**: Frontend — the project's lint and build pass; screenshots or a short recording of the history list, an invoice detail, and the dashboard accompany the change.
- **VAL-003**: New backend read logic (list/filter/search/paginate, detail lookup, summary aggregation, aging/priority derivation) meets the project coverage gate, or documents why a surface is excluded.
- **VAL-004**: Every new read endpoint (`GET /invoices`, `GET /invoices/{id}`, `GET /summary`, `GET /purchase-orders`, `GET /purchase-orders/{po_number}`, `GET /vendors`) has an integration test against a seeded store.

## Assumptions

- **Builds on feature 001**: This reports over the `processed_invoices` results and the seeded PO/vendor reference tables produced/loaded by feature 001. No new domain is introduced; it is a read layer plus UI.
- **Same monorepo, two folders**: read endpoints are added to the existing backend API; the screens are added to the existing React frontend, both under the current `backend/` and `frontend/` layout. A navigation shell hosts the existing chat screen plus the new reporting screens.
- **Read-only**: per clarification, no delete or other mutations — the surface only reads.
- **No original-document viewer**: per clarification, raw uploaded files remain unstored (001's SEC-003), so detail views never show the source PDF — extracted data + decision only.
- **Full analytics**: per clarification, the dashboard includes both basic counts/totals AND the aging breakdown and high-value/overdue priority list.
- **Aging & priority are derived** from each record's extracted invoice due date and total amount; records without a due date fall into an "undated" bucket and are excluded from overdue/due-soon priority. The high-value threshold defaults to 3000 and is configurable (matching 001's tolerances-as-config style).
- **Pagination** uses a simple page/limit model at the expected local scale; the exact scheme is a plan-level detail.
- **No auth / single user / no real-time push**: consistent with 001; views refresh on load or manual refresh rather than via a live socket.
- **Currency** is displayed as stored on each record; no conversion or normalization beyond what 001 already applied.
