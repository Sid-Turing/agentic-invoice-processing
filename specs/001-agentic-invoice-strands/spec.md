# Feature Specification: Agentic Invoice Processing (Strands)

**Feature Branch**: `001-agentic-invoice-strands`
**Created**: 2026-07-07
**Status**: Draft
**Input**: User description: "Rework the existing multi-service Invoice Processing application into a single, truly *agentic* flow. Drop the email-fetch service and the frontend. A user uploads only the invoice; purchase orders already live in a database. The agent extracts the invoice, and if a PO number is found it looks that PO up in the database (via a DB-backed tool) and reconciles against it — otherwise it skips reconciliation. Built on Amazon's Strands Agents framework, as a new standalone repository in the root. Keep the flow strong but not unnecessarily complex."

## Context & Motivation

The current application (separate `Email_fetch`, `extraction`, `processor`, `frontend`, and mock-database services) is a conventional pipeline that happens to call an LLM at a couple of fixed steps: extraction reads documents with a vision model, and the processor uses an LLM only for semantic vendor/line-item matching. The orchestration itself is a hardcoded chain of status transitions (`extracted → Validated1 → … → Approved`), with no reasoning about *what to check next* or *why a decision was made*.

This feature reimagines that same business outcome — turning an invoice into an approve / needs-review decision — as a **model-driven agent** that is handed a single invoice, decides which checks to run, calls purpose-built tools (including a database-backed purchase-order lookup), recovers from ambiguity, and returns a decision **with a human-readable explanation of its reasoning**. Email ingestion and the web UI are removed. A **purchase-order reference database is retained**: the agent no longer receives a PO document from the user — instead it extracts the PO number from the invoice and looks the corresponding PO up in the database.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconcile an invoice against its purchase order from the database (Priority: P1)

An accounts-payable user uploads a single invoice document. The agent extracts structured data from it, validates it internally, and — because the invoice carries a PO number — uses a database-backed tool to fetch the matching purchase order (and its vendor and line items) from the PO reference database. It reconciles the invoice against that PO (vendor and line items) and returns a decision of **APPROVED** or **NEEDS_REVIEW** with the specific reasons and a short natural-language explanation.

**Why this priority**: This is the core value of the whole system and the reason the original processor exists — deciding whether an invoice is safe to pay by matching it to what was actually ordered. It is the full end-to-end agentic flow; everything else is a subset or an enhancement.

**Independent Test**: Seed the PO reference database with a known PO, submit an invoice carrying that PO number that agrees with it, and confirm the response is `APPROVED` with no blocking reasons; submit an invoice whose totals or line items diverge from the stored PO beyond tolerance and confirm `NEEDS_REVIEW` with the correct reason code(s). No other story needs to be implemented for this to deliver value.

**Acceptance Scenarios**:

1. **Given** a PO in the database and an uploaded invoice carrying that PO number that agrees on vendor, line items, and totals within tolerance, **When** the invoice is processed, **Then** the agent looks up the PO, returns `APPROVED` with no blocking reasons, and explains which checks succeeded.
2. **Given** an invoice whose line-item quantities differ from the stored PO by more than the allowed tolerance, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `line_items_match` reason identifying the divergent item(s).
3. **Given** an invoice whose vendor cannot be matched to the stored PO's vendor, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `po_vendor_match` reason and its confidence in the (non-)match.
4. **Given** an invoice whose stated total does not equal subtotal + tax + shipping − discount within tolerance, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `financial_totals` reason regardless of PO agreement.

---

### User Story 2 - Validate an invoice with no resolvable purchase order (Priority: P2)

A user uploads an invoice that either carries no PO number, or carries a PO number that is not present in the reference database. The agent extracts the invoice, runs all invoice-internal validations (mandatory fields, currency, line-item arithmetic, sales tax, financial totals), skips reconciliation (recording why), and returns a decision based on those checks alone.

**Why this priority**: Not every invoice references a PO that exists in the system, and the original app explicitly allowed PO-less invoices to be approved on internal validation alone. Supporting this makes the tool usable for the common case where no matching PO is on file, without failing the invoice for that reason alone.

**Independent Test**: Submit a well-formed invoice with no PO number (and separately, one whose PO number is absent from the seeded database) and confirm reconciliation is skipped and the verdict rests only on invoice-internal checks; confirm a missing mandatory field or mismatched totals still yields `NEEDS_REVIEW` with the correct reason.

**Acceptance Scenarios**:

1. **Given** a well-formed invoice with no PO number, **When** it is uploaded, **Then** the agent runs only invoice-internal checks, records reconciliation as `skipped` (reason: no PO number on invoice), and returns `APPROVED`.
2. **Given** a well-formed invoice whose PO number is not found in the database, **When** it is uploaded, **Then** the agent records reconciliation as `skipped` (reason: PO not found in database) and decides on invoice-internal checks alone.
3. **Given** an invoice missing a required field (e.g. invoice number or total), **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `mandatory_fields` reason listing the missing field(s).
4. **Given** an invoice priced in an unsupported currency, **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `currency` reason.

---

### User Story 3 - Understand and trust the decision (Priority: P3)

A reviewer receives the decision and needs to understand *why* the agent decided as it did: which checks ran, which passed / failed / were skipped, the values that drove each outcome (including which PO was retrieved from the database), and the confidence of any semantic (LLM) judgments. The response includes a structured, check-by-check trace alongside the plain-language explanation.

**Why this priority**: The whole point of making this "truly agentic" rather than a black-box pipeline is explainability — a human must be able to act on `NEEDS_REVIEW`. This is an enhancement layered on top of the decision, valuable but not required for the system to produce a correct verdict.

**Independent Test**: For any processed invoice, confirm the response contains an ordered list of the checks the agent performed, each with a pass/fail/skipped status and the key figures it compared (including the PO number and identity of any PO fetched), plus a natural-language summary — and that this trace is consistent with the final decision.

**Acceptance Scenarios**:

1. **Given** any processed submission, **When** the decision is returned, **Then** it includes a trace listing each check performed with its outcome and the concrete values compared (e.g. expected vs. actual totals, and the retrieved PO identifier).
2. **Given** a decision that relied on a semantic vendor or line-item match, **When** the trace is inspected, **Then** it records the match confidence and a short rationale for that judgment.
3. **Given** a check that was intentionally not run (e.g. reconciliation because no PO number was found or the PO was not in the database, or tax validation when tax inputs are unavailable), **When** the trace is inspected, **Then** that check appears as `skipped` with the reason it was skipped.

---

### Edge Cases

- **Unreadable / corrupt invoice file**: The uploaded invoice cannot be opened or converted to an image. The agent returns a clear input error or `NEEDS_REVIEW` with a reason rather than crashing.
- **Unsupported file format**: A file that is neither a supported image type nor a PDF is rejected with an explanatory reason.
- **Multi-page document**: A multi-page PDF is fully considered (all pages contribute to extraction), not just the first page.
- **Extraction returns implausible or empty data**: The vision step yields no parseable structured data or obviously garbage values; the agent flags this as an extraction-quality issue rather than silently proceeding.
- **PO number extracted but not in database**: Reconciliation is skipped with the reason "PO not found"; the decision rests on invoice-internal checks (US2).
- **No PO number on the invoice**: Reconciliation is skipped with the reason "no PO number"; the decision rests on invoice-internal checks (US2).
- **Database unreachable / lookup times out**: Treated as a transient failure (retryable), distinct from a "PO not found" business skip and distinct from a `NEEDS_REVIEW` verdict.
- **Line items reordered, grouped, or split** between invoice and the stored PO: Reconciliation tolerates ordering/grouping differences and still matches on content within tolerance.
- **LLM/vision provider error, timeout, or rate limit**: The agent surfaces a transient-failure outcome distinct from a business `NEEDS_REVIEW`, so callers can retry.
- **Zero-quantity or zero-priced line items**: Handled without divide-by-zero or false tax mismatches.
- **Missing tax inputs** (no customer/vendor address, or no per-line tax basis): Sales-tax validation is marked `skipped` with a reason, not failed.

### Scope and Persona Impact *(mandatory)*

- **Affected Persona(s)**: Accounts-payable / finance operator (uploads an invoice, reads decisions) and the developer/operator running the service and seeding the PO reference database.
- **In Scope**: A single upload endpoint accepting one invoice document (required, no PO upload); agent-driven extraction of the invoice; invoice-internal validation (mandatory fields, currency, line-item arithmetic, sales tax, financial totals); a database-backed tool that looks up a purchase order (with its vendor and line items) by the PO number extracted from the invoice; invoice-to-PO reconciliation (vendor + line items) when a PO is found; a database-backed tool that persists the processed invoice together with its final decision (verdict, reason codes, and check trace) to a results store; a structured decision (`APPROVED` / `NEEDS_REVIEW`) with reason codes, a per-check trace, and a natural-language explanation; the agent orchestration itself, built on the Strands Agents framework as a model-driven loop over purpose-built tools.
- **Out of Scope**: Email ingestion; the web frontend; user accounts / multi-tenancy / auth; creating, editing, or managing purchase orders (the PO reference data is read-only, seeded outside this feature); a read API or UI to browse persisted decisions (write-only persistence in v1); TaxCloud (or any external tax authority) integration; address standardization via external services; payment execution; batch/bulk processing beyond a single invoice per request.
- **Tenant/Role Impact**: None — this is a standalone, single-user local service with no tenant or role model. No authorization boundaries are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a single submission consisting of exactly one invoice document, provided directly by the user (no email ingestion, no PO upload).
- **FR-002**: The system MUST accept invoices as PDF or common image formats (at minimum PDF, PNG, JPEG) and MUST convert PDFs (including multi-page PDFs) into images the vision model can read.
- **FR-003**: The system MUST extract structured data from the invoice, including at minimum: invoice number, PO number (if present), invoice date, due date, vendor identity and address, customer identity and address, currency, subtotal, tax amount, discount, shipping, total amount, and line items (description, quantity, unit price, tax rate, total price, category).
- **FR-004**: The system MUST provide a database-backed lookup tool that, given a PO number, retrieves the matching purchase order from the PO reference database together with its vendor record and its line items, and reports whether a match was found.
- **FR-005**: The system MUST validate the invoice's mandatory fields and flag the decision when required fields are missing, naming the missing field(s).
- **FR-006**: The system MUST validate that the invoice currency is supported and flag unsupported currencies. (Default supported set: USD; configurable.)
- **FR-007**: The system MUST verify per-line-item arithmetic (quantity × unit price ≈ total price) within a configurable tolerance and flag divergent line items.
- **FR-008**: The system MUST validate sales tax against an expected basis using a configurable flat tax rate; when the inputs required for tax validation are unavailable, it MUST mark the tax check as `skipped` rather than failed.
- **FR-009**: The system MUST verify invoice financial totals — that line-item totals sum to the subtotal, that computed tax matches the stated tax, and that subtotal + tax + shipping − discount equals the stated total — each within a configurable tolerance, and flag any mismatch.
- **FR-010**: When a PO is retrieved from the database, the system MUST reconcile the invoice vendor against the stored PO vendor, tolerating superficial formatting differences, and MUST record a match confidence; a match below the confidence threshold is a blocking reason.
- **FR-011**: When a PO is retrieved from the database, the system MUST reconcile invoice line items against the stored PO line items — tolerant of reordering, grouping, and description wording — comparing quantity, unit price, and total price within configurable per-dimension tolerances, and flag items that do not match.
- **FR-012**: When the invoice carries no PO number, or the PO number is not found in the database, the system MUST run invoice-internal validation only, MUST NOT attempt reconciliation, and MUST record reconciliation as `skipped` with the distinguishing reason (no PO number vs. PO not found).
- **FR-013**: The system MUST return a single terminal decision of `APPROVED` or `NEEDS_REVIEW`. `APPROVED` requires every applicable check to pass; any failing check yields `NEEDS_REVIEW` with one or more reason codes.
- **FR-014**: The decision MUST include machine-readable reason codes drawn from a fixed taxonomy covering at least: mandatory fields, currency, line-item arithmetic, sales tax, financial totals, PO vendor match, and PO line-item match.
- **FR-015**: The decision MUST include a check-by-check trace, where each check reports `pass` / `fail` / `skipped`, the key values compared (including the retrieved PO identifier when reconciliation ran), and (for semantic judgments) a confidence and short rationale.
- **FR-016**: The decision MUST include a concise natural-language explanation of the outcome, consistent with the structured trace.
- **FR-017**: The orchestration MUST be agent-driven: a model reasons over the invoice and invokes purpose-built tools (extraction, the PO database lookup, each validation, reconciliation) rather than executing a fixed hardcoded sequence, and the flow MUST be resilient to an individual tool returning ambiguous or partial results.
- **FR-018**: The system MUST distinguish transient failures (model/provider errors, timeouts, database unavailability) from business `NEEDS_REVIEW` outcomes and from a benign "PO not found" skip, so a caller can tell "retry me" apart from "a human must review this" apart from "no PO on file".
- **FR-019**: The system MUST persist each processed invoice together with its final decision — verdict, reason codes, and the per-check trace — to a results store via a database-backed write tool. Persistence writes MUST go only to the results / processed-invoice records; the purchase-order reference data (POs, PO vendors, PO line items) MUST remain read-only and MUST NOT be mutated by processing.
- **FR-020**: The system MUST operate as a standalone service requiring only the uploaded invoice, a reachable database (read-only PO reference data plus the writable results store), and configured model credentials — no email service and no frontend are required to run it.
- **FR-021**: The raw uploaded invoice file MUST NOT be persisted beyond the lifetime of the request; only the extracted structured data and decision are stored (see FR-019). A failure to persist the result MUST be treated as a transient/operational failure (retryable), not as a business `NEEDS_REVIEW`.

### API Schema Requirements *(mandatory when HTTP endpoints are added or changed)*

- **SCH-001**: `POST /process` MUST accept a multipart request with a single `invoice` file part (required; no PO part) and MUST return a decision response schema (`InvoiceDecisionResponse`) containing: a `record_id` identifying the persisted result, overall `decision` (`APPROVED` | `NEEDS_REVIEW`), `reasons[]` (reason codes with detail), `checks[]` (the per-check trace), `explanation` (text), the `extracted_invoice` structured data, and, when a PO was retrieved from the database, the `matched_po` data and reconciliation results. The exact request/response model names are finalized in the plan.
- **SCH-002**: `GET /health` MUST return a lightweight liveness/readiness response (`HealthResponse`) indicating the service, its configured model provider(s), and the PO reference database are reachable.

### Security and Data Requirements *(mandatory when auth, tenants, secrets, or state are touched)*

- **SEC-001**: No authentication or tenant model is introduced; the service is a single-user local tool. This is an explicit scope decision, not an omission — any future multi-user exposure is out of scope here.
- **SEC-002**: All model-provider credentials (Gemini and OpenAI API keys) and database connection credentials MUST be sourced from the runtime environment / a secrets mechanism at startup; they MUST NOT be committed to the repository or baked into images or manifests.
- **SEC-003**: Uploaded invoices MUST be treated as untrusted input: size and type MUST be validated before processing, and files MUST NOT be persisted beyond the lifetime of the request (see FR-019).
- **SEC-004**: The service MUST NOT write to the purchase-order reference tables (purchase orders, PO vendors, PO line items) — those are read-only. All persistence writes are confined to the results / processed-invoice records (FR-019).

### Key Entities *(include if feature involves data)*

- **Submission**: One processing request — a single invoice document. The raw file is transient (not stored); its extracted data and decision are persisted separately (see Processed Invoice Record).
- **Extracted Invoice**: Structured representation of the invoice — header fields (numbers, dates, currency, totals, tax, discount, shipping), vendor block, customer block, and a list of line items — including the PO number when present.
- **Purchase Order (reference)**: A record in the PO reference database — PO number, associated vendor, dates, subtotal, tax, total, currency, payment terms, status — retrieved by PO number for reconciliation. Read-only.
- **Vendor (reference)**: The vendor record associated with a purchase order — name, tax ID, address, banking and tax-classification details. Read-only.
- **PO Line Item (reference)**: A stored line on a purchase order — description, quantity, unit price, tax rate, total price, category. Read-only.
- **Line Item (invoice)**: A single billed entry on the invoice — description, quantity, unit price, tax rate, total price, category.
- **Check**: One validation or reconciliation step the agent performed — its identifier, outcome (`pass`/`fail`/`skipped`), the values it compared, and any confidence/rationale.
- **Decision**: The terminal verdict — `APPROVED` or `NEEDS_REVIEW` — with its blocking reason codes, the ordered list of Checks, and the natural-language explanation.
- **Processed Invoice Record (persisted)**: The durable record written once per submission via the write tool — the extracted invoice data, the final decision (verdict + reason codes), and the check trace, addressable by a `record_id`. Written to the results store only; never to PO reference tables.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can obtain a decision for an uploaded invoice through a single request, with no email service and no frontend involved, and with purchase orders sourced entirely from the reference database.
- **SC-002**: With the PO reference database seeded, a well-formed invoice whose PO number matches its stored PO returns `APPROVED`; an invoice with a deliberately introduced discrepancy (missing field, total mismatch, or line-item/vendor divergence from the stored PO) returns `NEEDS_REVIEW` with a reason code that correctly identifies the discrepancy — verified across a labelled test set of at least 10 invoices.
- **SC-003**: On a labelled test set, the decision (`APPROVED` vs `NEEDS_REVIEW`) matches the expected verdict for at least 90% of cases, with no well-formed matching invoice incorrectly flagged as `NEEDS_REVIEW` for a reason unrelated to any real discrepancy.
- **SC-004**: Every `NEEDS_REVIEW` decision includes at least one reason code and a trace entry that a reviewer can act on without inspecting logs or source.
- **SC-005**: A single invoice submission whose PO number is absent from the database completes and returns a decision within a typical interactive wait (target: under 60 seconds for a single-page document), with reconciliation recorded as skipped.
- **SC-006**: Corrupt, unsupported, or missing-input submissions never crash the service; each returns a clear, categorized error or `NEEDS_REVIEW` reason.
- **SC-007**: Transient failures — provider errors and database unavailability (read or write) — are reported as retryable and are never reported as a business `NEEDS_REVIEW` or as "PO not found".
- **SC-008**: Each successfully processed invoice produces exactly one persisted result record (extracted invoice + verdict + reason codes + check trace), retrievable by its `record_id`, and the purchase-order reference tables are unchanged by processing (verified by row counts before and after a run).

### Validation Expectations

- **VAL-001**: Backend startup / import-level check — the service starts and `GET /health` returns healthy with valid credentials and a reachable, seeded PO reference database (see plan/README for the exact command).
- **VAL-002**: No UI in scope; instead, a sample request/response (e.g. a captured `POST /process` call against a fixture invoice, with the PO reference database seeded) documents the observable behavior. No visual artifact is required.
- **VAL-003**: New core logic (extraction mapping, PO lookup, validation checks, reconciliation, decision assembly) meets the project's line-coverage gate, or documents why a given surface (e.g. live model calls) is excluded and how it is covered instead.
- **VAL-004**: Both public HTTP endpoints (`POST /process`, `GET /health`) have integration tests, using fixture invoices, a seeded (or stubbed) PO database, and stubbed/recorded model responses where live calls are impractical.

## Assumptions

- **Framework**: The agent is built on the **Strands Agents** SDK (Amazon's open-source agent framework), using its model-driven agent loop and tool (`@tool`) abstraction. This is a fixed constraint from the request, recorded here because it is otherwise an implementation choice.
- **Model providers**: Per an earlier clarification, the original providers are retained but driven through Strands — **Gemini** for document/vision extraction and **OpenAI** for semantic reconciliation reasoning. The specific model IDs and the single-agent-with-tools vs. multi-agent topology are plan-level decisions; the requirements above are agnostic to that choice.
- **Entry point**: The surface is a **thin local HTTP API** (a single `POST /process` invoice-upload endpoint plus `GET /health`), not a CLI or a library — chosen for parity with the original service shape and ease of scripting.
- **Agreed agent architecture**: A single **Orchestrator/Invoice agent** drives the flow with four tools — (1) a **VLM-backed extraction tool** (document → structured data), (2) a **read-only PO lookup/search tool** (fetch PO + vendor + line items by PO number), (3) a **database write tool** (persist the processed invoice + decision to the results store), and (4) a deterministic **math tool** (summations and total/tax checks). Validation and reconciliation (mandatory fields, currency, vendor and line-item matching) are performed by the orchestrator's own reasoning, using the math tool for arithmetic, rather than as separate tools. This mirrors the original app, where the LLM did the semantic matching and only extraction/lookup/persistence were mechanical. The exact tool signatures and whether any are split further are plan-level details.
- **Purchase orders come from a database**: The user uploads only the invoice. Purchase orders (with their vendors and line items) already exist as **read-only reference data**, queried by the PO number extracted from the invoice. This matches the original app, which never mutates PO tables at runtime — they are seeded once and only ever read.
- **Persistence**: The processed invoice and its decision are written to a **results store** (the modern analog of the original `extracted_invoices` record), addressable by `record_id`. The original app's intermediate status-machine writes (`extraction_status` transitions, claim handoffs, the raw-email queue) do NOT carry over — they existed only to coordinate the async multi-service pipeline and dashboard, both of which are removed here.
- **Database engine & seed data**: The exact database engine and access layer are plan-level decisions. The read-only reference data is expected to be seeded from the existing project data — `purchase_orders_data.csv`, `po_vendors_data.csv`, and `purchase_order_line_items_data.csv` — which define the PO, vendor, and PO-line-item shapes. Seeding/loading itself is operational setup, not part of this feature's runtime behavior.
- **Reconciliation is conditional on a resolvable PO**: When a PO number resolves in the database the agent reconciles; when it is absent (no PO number, or not on file) it validates only. This mirrors the original app's with-PO / without-PO split.
- **Tax validation is self-contained**: Sales-tax validation uses a configurable flat rate (default 9.125%, matching the original app's fallback). TaxCloud and external address verification are out of scope.
- **Tolerances carry over from the original app** as configurable defaults: line-item/total arithmetic within 0.02; PO line-item matching within quantity 10%, unit price 5%, total price 5%; vendor semantic match at ≥70% confidence; tax discrepancy threshold 0.25. The plan may tune these.
- **Single submission per request**: One invoice per call; batch processing is out of scope for v1.
- **New standalone repository**: The work lives in a new git repo at the workspace root (`agentic-invoice-processing/`), independent of both `invoice-processing` and `humain-marketplace`.
- **Runtime**: Python 3.11+ (Strands' supported runtime), consistent with the original backend's toolchain.
