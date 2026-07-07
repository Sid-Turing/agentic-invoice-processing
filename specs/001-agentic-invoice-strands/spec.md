# Feature Specification: Agentic Invoice Processing (Strands)

**Feature Branch**: `001-agentic-invoice-strands`
**Created**: 2026-07-07
**Status**: Draft
**Input**: User description: "Rework the existing multi-service Invoice Processing application into a single, truly *agentic* flow. Drop the email-fetch service and the frontend. A user uploads an invoice and, optionally, a purchase order in the same request. Purchase orders also live in a database. If a PO is uploaded, the agent extracts it and writes it to the database using its tools; if not, and the invoice carries a PO number, the agent looks that PO up in the database. Either way it reconciles the invoice against the PO — otherwise it skips reconciliation. Built on Amazon's Strands Agents framework, as a new standalone repository in the root. Keep the flow strong but not unnecessarily complex."

## Context & Motivation

The current application (separate `Email_fetch`, `extraction`, `processor`, `frontend`, and mock-database services) is a conventional pipeline that happens to call an LLM at a couple of fixed steps: extraction reads documents with a vision model, and the processor uses an LLM only for semantic vendor/line-item matching. The orchestration itself is a hardcoded chain of status transitions (`extracted → Validated1 → … → Approved`), with no reasoning about *what to check next* or *why a decision was made*.

This feature reimagines that same business outcome — turning an invoice into an approve / needs-review decision — as a **model-driven agent** that decides which checks to run, calls purpose-built tools, recovers from ambiguity, and returns a decision **with a human-readable explanation of its reasoning**. Email ingestion and the web UI are removed. A **purchase-order database is retained**, and the agent resolves the PO one of two ways:

- **Uploaded PO**: the user submits a PO document alongside the invoice. The agent extracts it (vision tool) and writes it into the PO store (write tool), then reconciles against it.
- **PO on file**: no PO is uploaded, but the invoice carries a PO number. The agent looks that PO up in the database (read tool) and reconciles against it.

If neither path yields a PO, reconciliation is skipped and the decision rests on invoice-internal validation alone.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconcile an invoice against its purchase order (Priority: P1)

An accounts-payable user uploads an invoice, and optionally its purchase order, in a single request. The agent extracts the invoice; resolves the PO — extracting and storing an uploaded PO, or else looking one up by the invoice's PO number; validates the invoice internally; reconciles it against the resolved PO (vendor and line items); and returns a decision of **APPROVED** or **NEEDS_REVIEW** with the specific reasons and a short natural-language explanation.

**Why this priority**: This is the core value of the whole system and the reason the original processor exists — deciding whether an invoice is safe to pay by matching it to what was actually ordered. It is the full end-to-end agentic flow; everything else is a subset or an enhancement.

**Independent Test**: (Upload path) Submit an invoice + a matching PO document and confirm the PO is extracted, persisted to the store, reconciled, and the verdict is `APPROVED`. (Lookup path) Seed the database with a PO, submit an invoice carrying that PO number and no PO file, and confirm the PO is fetched and reconciled. In both, introduce a divergence beyond tolerance and confirm `NEEDS_REVIEW` with the correct reason code.

**Acceptance Scenarios**:

1. **Given** an invoice and a matching PO document uploaded together, **When** the request is processed, **Then** the agent extracts the PO, writes it to the PO store, reconciles the invoice against it, and returns `APPROVED` with no blocking reasons and an explanation citing the successful checks.
2. **Given** an invoice carrying a PO number and no uploaded PO, with that PO present in the database, **When** it is processed, **Then** the agent looks the PO up, reconciles, and decides accordingly.
3. **Given** an invoice whose line-item quantities differ from the resolved PO by more than the allowed tolerance, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `line_items_match` reason identifying the divergent item(s).
4. **Given** an invoice whose vendor cannot be matched to the resolved PO's vendor, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `po_vendor_match` reason and its confidence in the (non-)match.
5. **Given** both an uploaded PO and a PO already on file for the same PO number, **When** the request is processed, **Then** the uploaded PO takes precedence: it is extracted and upserted to the store, and reconciliation uses it.

---

### User Story 2 - Validate an invoice with no resolvable purchase order (Priority: P2)

A user uploads an invoice with no PO document, and either the invoice carries no PO number or its PO number is not present in the database. The agent extracts the invoice, runs all invoice-internal validations (mandatory fields, currency, line-item arithmetic, sales tax, financial totals), skips reconciliation (recording why), and returns a decision based on those checks alone.

**Why this priority**: Not every invoice arrives with a PO — uploaded or on file — and the original app explicitly allowed PO-less invoices to be approved on internal validation alone. Supporting this makes the tool usable for the common case without failing the invoice merely for lacking a PO.

**Independent Test**: Submit an invoice with no PO file whose PO number is absent (or missing entirely) and confirm reconciliation is skipped with the right reason and the verdict rests only on invoice-internal checks; confirm a missing mandatory field or mismatched totals still yields `NEEDS_REVIEW` with the correct reason.

**Acceptance Scenarios**:

1. **Given** a well-formed invoice with no PO document and no PO number, **When** it is uploaded, **Then** the agent runs only invoice-internal checks, records reconciliation as `skipped` (reason: no PO number on invoice), and returns `APPROVED`.
2. **Given** a well-formed invoice with no PO document whose PO number is not found in the database, **When** it is uploaded, **Then** the agent records reconciliation as `skipped` (reason: PO not found in database) and decides on invoice-internal checks alone.
3. **Given** an invoice missing a required field (e.g. invoice number or total), **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `mandatory_fields` reason listing the missing field(s).
4. **Given** an invoice priced in an unsupported currency, **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `currency` reason.

---

### User Story 3 - Understand and trust the decision (Priority: P3)

A reviewer receives the decision and needs to understand *why* the agent decided as it did: which checks ran, which passed / failed / were skipped, the values that drove each outcome (including which PO was used and whether it came from the upload or the database), and the confidence of any semantic (LLM) judgments. The response includes a structured, check-by-check trace alongside the plain-language explanation.

**Why this priority**: The whole point of making this "truly agentic" rather than a black-box pipeline is explainability — a human must be able to act on `NEEDS_REVIEW`. This is an enhancement layered on top of the decision, valuable but not required for the system to produce a correct verdict.

**Independent Test**: For any processed invoice, confirm the response contains an ordered list of the checks the agent performed, each with a pass/fail/skipped status and the key figures it compared (including the PO number, the PO source, and the persisted record id), plus a natural-language summary consistent with the final decision.

**Acceptance Scenarios**:

1. **Given** any processed submission, **When** the decision is returned, **Then** it includes a trace listing each check performed with its outcome and the concrete values compared (e.g. expected vs. actual totals, and the resolved PO identifier and source).
2. **Given** a decision that relied on a semantic vendor or line-item match, **When** the trace is inspected, **Then** it records the match confidence and a short rationale for that judgment.
3. **Given** a check that was intentionally not run (e.g. reconciliation because no PO was uploaded or found, or tax validation when tax inputs are unavailable), **When** the trace is inspected, **Then** that check appears as `skipped` with the reason it was skipped.

---

### Edge Cases

- **Unreadable / corrupt file** (invoice or uploaded PO): the file cannot be opened or converted to an image. The agent returns a clear input error or `NEEDS_REVIEW` with a reason rather than crashing; a bad PO file specifically is reported distinctly from a bad invoice.
- **Unsupported file format**: a file that is neither a supported image type nor a PDF is rejected with an explanatory reason.
- **Multi-page document**: a multi-page PDF (invoice or PO) is fully considered (all pages contribute to extraction), not just the first page.
- **Extraction returns implausible or empty data**: the vision step yields no parseable structured data or obviously garbage values; the agent flags this as an extraction-quality issue rather than silently proceeding.
- **Uploaded PO whose number already exists on file**: the uploaded PO is upserted (created or updated by PO number); the uploaded version is used for reconciliation (US1 scenario 5).
- **PO number extracted but not uploaded and not in database**: reconciliation is skipped with the reason "PO not found"; the decision rests on invoice-internal checks (US2).
- **No PO number on the invoice and none uploaded**: reconciliation is skipped with the reason "no PO number"; the decision rests on invoice-internal checks (US2).
- **Database unreachable / lookup or write times out**: treated as a transient failure (retryable), distinct from a "PO not found" business skip and distinct from a `NEEDS_REVIEW` verdict.
- **Line items reordered, grouped, or split** between invoice and PO: reconciliation tolerates ordering/grouping differences and still matches on content within tolerance.
- **LLM/vision provider error, timeout, or rate limit**: surfaced as a transient-failure outcome distinct from a business `NEEDS_REVIEW`, so callers can retry.
- **Zero-quantity or zero-priced line items**: handled without divide-by-zero or false tax mismatches.
- **Missing tax inputs** (no customer/vendor address, or no per-line tax basis): sales-tax validation is marked `skipped` with a reason, not failed.

### Scope and Persona Impact *(mandatory)*

- **Affected Persona(s)**: Accounts-payable / finance operator (uploads an invoice and optionally a PO, reads decisions) and the developer/operator running the service and seeding the PO database.
- **In Scope**: A single upload endpoint accepting one invoice document (required) and one optional PO document; agent-driven extraction of the invoice and, when supplied, the PO; a database-backed write tool the agent uses both to persist an extracted uploaded PO (vendor + line items, upserted by PO number) and to persist the processed invoice with its final decision; a database-backed read tool that looks up a PO (with vendor and line items) by the invoice's PO number; invoice-internal validation (mandatory fields, currency, line-item arithmetic, sales tax, financial totals); invoice-to-PO reconciliation (vendor + line items) when a PO is resolved; a structured decision (`APPROVED` / `NEEDS_REVIEW`) with reason codes, a per-check trace, and a natural-language explanation; the agent orchestration itself, built on the Strands Agents framework as a model-driven loop over purpose-built tools.
- **Out of Scope**: Email ingestion; the web frontend; user accounts / multi-tenancy / auth; a dedicated PO-management API or UI, PO deletion, or bulk PO import beyond the single uploaded PO per request; a read API or UI to browse persisted decisions (write-only persistence in v1); TaxCloud (or any external tax authority) integration; address standardization via external services; payment execution; batch/bulk processing beyond a single invoice per request.
- **Tenant/Role Impact**: None — this is a standalone, single-user local service with no tenant or role model. No authorization boundaries are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a single submission consisting of one invoice document (required) and one optional purchase-order document, provided directly by the user in the same request (no email ingestion).
- **FR-002**: The system MUST accept invoices and POs as PDF or common image formats (at minimum PDF, PNG, JPEG) and MUST convert PDFs (including multi-page PDFs) into images the vision model can read.
- **FR-003**: The system MUST extract structured data from the invoice, including at minimum: invoice number, PO number (if present), invoice date, due date, vendor identity and address, customer identity and address, currency, subtotal, tax amount, discount, shipping, total amount, and line items (description, quantity, unit price, tax rate, total price, category).
- **FR-004**: When a PO document is uploaded, the system MUST extract comparable structured data from it (PO number, vendor, dates, totals, and line items) via the extraction tool, and MUST persist it to the PO store via the write tool — creating or updating (upserting by PO number) the purchase order, its vendor, and its line items — then use it for reconciliation.
- **FR-005**: When no PO document is uploaded, the system MUST provide a read tool that, given the PO number extracted from the invoice, retrieves the matching purchase order (with its vendor and line items) from the PO store and reports whether a match was found.
- **FR-006**: The system MUST resolve at most one PO per submission, preferring an uploaded PO over one on file; the resolved PO's source (uploaded vs. database) MUST be recorded and surfaced in the decision.
- **FR-007**: The system MUST validate the invoice's mandatory fields and flag the decision when required fields are missing, naming the missing field(s).
- **FR-008**: The system MUST validate that the invoice currency is supported and flag unsupported currencies. (Default supported set: USD; configurable.)
- **FR-009**: The system MUST verify per-line-item arithmetic (quantity × unit price ≈ total price) within a configurable tolerance and flag divergent line items.
- **FR-010**: The system MUST validate sales tax against an expected basis using a configurable flat tax rate; when the inputs required for tax validation are unavailable, it MUST mark the tax check as `skipped` rather than failed.
- **FR-011**: The system MUST verify invoice financial totals — that line-item totals sum to the subtotal, that computed tax matches the stated tax, and that subtotal + tax + shipping − discount equals the stated total — each within a configurable tolerance, and flag any mismatch.
- **FR-012**: When a PO is resolved (uploaded or on file), the system MUST reconcile the invoice vendor against the PO vendor, tolerating superficial formatting differences, and MUST record a match confidence; a match below the confidence threshold is a blocking reason.
- **FR-013**: When a PO is resolved, the system MUST reconcile invoice line items against the PO line items — tolerant of reordering, grouping, and description wording — comparing quantity, unit price, and total price within configurable per-dimension tolerances, and flag items that do not match.
- **FR-014**: When no PO is uploaded and none is found on file, the system MUST run invoice-internal validation only, MUST NOT attempt reconciliation, and MUST record reconciliation as `skipped` with the distinguishing reason (no PO number vs. PO not found).
- **FR-015**: The system MUST return a single terminal decision of `APPROVED` or `NEEDS_REVIEW`. `APPROVED` requires every applicable check to pass; any failing check yields `NEEDS_REVIEW` with one or more reason codes.
- **FR-016**: The decision MUST include machine-readable reason codes drawn from a fixed taxonomy covering at least: mandatory fields, currency, line-item arithmetic, sales tax, financial totals, PO vendor match, and PO line-item match.
- **FR-017**: The decision MUST include a check-by-check trace, where each check reports `pass` / `fail` / `skipped`, the key values compared (including the resolved PO identifier and source when reconciliation ran), and (for semantic judgments) a confidence and short rationale.
- **FR-018**: The decision MUST include a concise natural-language explanation of the outcome, consistent with the structured trace.
- **FR-019**: The orchestration MUST be agent-driven: a model reasons over the submission and invokes purpose-built tools (extraction, PO write, PO read, and a deterministic math helper) rather than executing a fixed hardcoded sequence, and the flow MUST be resilient to an individual tool returning ambiguous or partial results.
- **FR-020**: The system MUST persist each processed invoice together with its final decision — verdict, reason codes, and the per-check trace — to a results store via the write tool, addressable by a `record_id`.
- **FR-021**: The system MUST confine database writes to two controlled operations — (a) upserting an uploaded PO (with vendor and line items) into the PO store, and (b) persisting a processed-invoice result — and MUST perform no other mutations and no deletes. The raw uploaded files MUST NOT be persisted beyond the lifetime of the request; only extracted structured data and the decision are stored.
- **FR-022**: The system MUST distinguish transient failures (model/provider errors, timeouts, database unavailability on read or write) from business `NEEDS_REVIEW` outcomes and from a benign "PO not found" skip, so a caller can tell "retry me" apart from "a human must review this" apart from "no PO available". A failure to persist the uploaded PO or the result is a transient/operational failure, not a `NEEDS_REVIEW`.
- **FR-023**: The system MUST operate as a standalone service requiring only the uploaded invoice (and optional PO), a reachable database, and configured model credentials — no email service and no frontend are required to run it.

### API Schema Requirements *(mandatory when HTTP endpoints are added or changed)*

- **SCH-001**: `POST /process` MUST accept a multipart request with an `invoice` file part (required) and an optional `po` file part, and MUST return a decision response schema (`InvoiceDecisionResponse`) containing: a `record_id` identifying the persisted result, overall `decision` (`APPROVED` | `NEEDS_REVIEW`), `reasons[]` (reason codes with detail), `checks[]` (the per-check trace), `explanation` (text), the `extracted_invoice` structured data, and, when a PO was resolved, the `matched_po` data (with its `source`: `uploaded` | `database`) and reconciliation results. The exact request/response model names are finalized in the plan.
- **SCH-002**: `GET /health` MUST return a lightweight liveness/readiness response (`HealthResponse`) indicating the service, its configured model provider(s), and the database are reachable.

### Security and Data Requirements *(mandatory when auth, tenants, secrets, or state are touched)*

- **SEC-001**: No authentication or tenant model is introduced; the service is a single-user local tool. This is an explicit scope decision, not an omission — any future multi-user exposure is out of scope here.
- **SEC-002**: All model-provider credentials (Gemini and OpenAI API keys) and database connection credentials MUST be sourced from the runtime environment / a secrets mechanism at startup; they MUST NOT be committed to the repository or baked into images or manifests.
- **SEC-003**: Uploaded invoices and POs MUST be treated as untrusted input: size and type MUST be validated before processing, and files MUST NOT be persisted beyond the lifetime of the request (see FR-021).
- **SEC-004**: The service MUST write to the database only via the two controlled operations in FR-021 (upsert uploaded PO; persist result). It MUST NOT delete PO or vendor data and MUST NOT mutate a stored PO except by upsert from a freshly uploaded PO of the same number.

### Key Entities *(include if feature involves data)*

- **Submission**: One processing request — a required invoice document plus an optional PO document. The raw files are transient (not stored); extracted data and the decision are persisted separately.
- **Extracted Invoice**: Structured representation of the invoice — header fields (numbers, dates, currency, totals, tax, discount, shipping), vendor block, customer block, and a list of line items — including the PO number when present.
- **Purchase Order**: A record in the PO store — PO number, associated vendor, dates, subtotal, tax, total, currency, payment terms, status — either seeded, previously stored, or freshly upserted from an uploaded PO document. Carries a `source` when used in a decision (`uploaded` | `database`).
- **Vendor**: The vendor record associated with a purchase order — name, tax ID, address, banking and tax-classification details.
- **PO Line Item**: A stored line on a purchase order — description, quantity, unit price, tax rate, total price, category.
- **Line Item (invoice)**: A single billed entry on the invoice — description, quantity, unit price, tax rate, total price, category.
- **Check**: One validation or reconciliation step the agent performed — its identifier, outcome (`pass`/`fail`/`skipped`), the values it compared, and any confidence/rationale.
- **Decision**: The terminal verdict — `APPROVED` or `NEEDS_REVIEW` — with its blocking reason codes, the ordered list of Checks, and the natural-language explanation.
- **Processed Invoice Record (persisted)**: The durable record written once per submission via the write tool — the extracted invoice data, the final decision (verdict + reason codes), and the check trace, addressable by a `record_id`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can obtain a decision for an uploaded invoice (with or without an accompanying PO) through a single request, with no email service and no frontend involved.
- **SC-002**: When a PO is uploaded with the invoice, the PO is extracted and persisted to the store (retrievable afterward by its PO number) and used for reconciliation; when no PO is uploaded, a matching PO on file is fetched and used — verified across a labelled test set covering both paths.
- **SC-003**: A well-formed invoice that matches its resolved PO returns `APPROVED`; an invoice with a deliberately introduced discrepancy (missing field, total mismatch, or line-item/vendor divergence) returns `NEEDS_REVIEW` with a reason code that correctly identifies the discrepancy — verified across a labelled test set of at least 10 invoices.
- **SC-004**: On a labelled test set, the decision (`APPROVED` vs `NEEDS_REVIEW`) matches the expected verdict for at least 90% of cases, with no well-formed matching invoice incorrectly flagged for a reason unrelated to any real discrepancy.
- **SC-005**: Every `NEEDS_REVIEW` decision includes at least one reason code and a trace entry that a reviewer can act on without inspecting logs or source.
- **SC-006**: A single invoice submission with no resolvable PO completes and returns a decision within a typical interactive wait (target: under 60 seconds for a single-page document), with reconciliation recorded as skipped.
- **SC-007**: Corrupt, unsupported, or missing-input submissions never crash the service; each returns a clear, categorized error or `NEEDS_REVIEW` reason.
- **SC-008**: Transient failures — provider errors and database unavailability (read or write) — are reported as retryable and are never reported as a business `NEEDS_REVIEW` or as "PO not found".
- **SC-009**: Each successfully processed invoice produces exactly one persisted result record (extracted invoice + verdict + reason codes + check trace), retrievable by its `record_id`; database writes are limited to result records and PO upserts, with no deletions (verified by inspecting write operations over a run).

### Validation Expectations

- **VAL-001**: Backend startup / import-level check — the service starts and `GET /health` returns healthy with valid credentials and a reachable, seeded database (see plan/README for the exact command).
- **VAL-002**: No UI in scope; instead, sample request/response captures for both paths (a `POST /process` call with an uploaded PO, and one relying on a PO on file) document the observable behavior. No visual artifact is required.
- **VAL-003**: New core logic (invoice + PO extraction mapping, PO upsert, PO lookup, validation checks, reconciliation, decision assembly) meets the project's line-coverage gate, or documents why a given surface (e.g. live model calls) is excluded and how it is covered instead.
- **VAL-004**: Both public HTTP endpoints (`POST /process`, `GET /health`) have integration tests, exercising both the uploaded-PO and PO-on-file paths, using fixture documents, a seeded (or stubbed) database, and stubbed/recorded model responses where live calls are impractical.

## Assumptions

- **Framework**: The agent is built on the **Strands Agents** SDK (Amazon's open-source agent framework), using its model-driven agent loop and tool (`@tool`) abstraction. This is a fixed constraint from the request, recorded here because it is otherwise an implementation choice.
- **Model providers**: Per an earlier clarification, the original providers are retained but driven through Strands — **Gemini** for document/vision extraction and **OpenAI** for semantic reconciliation reasoning. The specific model IDs and the single-agent-with-tools vs. multi-agent topology are plan-level decisions; the requirements above are agnostic to that choice.
- **Entry point**: The surface is a **thin local HTTP API** (a single `POST /process` upload endpoint plus `GET /health`), not a CLI or a library — chosen for parity with the original service shape and ease of scripting.
- **Agreed agent architecture**: A single **Orchestrator/Invoice agent** drives the flow with four tools — (1) a **VLM-backed extraction tool** (document → structured data, used for both invoice and any uploaded PO), (2) a **database write tool** (upsert an uploaded PO; persist the processed invoice + decision), (3) a **read-only PO lookup/search tool** (fetch PO + vendor + line items by PO number), and (4) a deterministic **math tool** (summations and total/tax checks). Validation and reconciliation (mandatory fields, currency, vendor and line-item matching) are performed by the orchestrator's own reasoning, using the math tool for arithmetic, rather than as separate tools. This mirrors the original app, where the LLM did the semantic matching and only extraction/lookup/persistence were mechanical. The exact tool signatures and whether any are split further are plan-level details.
- **Purchase orders live in a database**: A PO store holds purchase orders with their vendors and line items. It is seeded from the existing project data — `purchase_orders_data.csv`, `po_vendors_data.csv`, and `purchase_order_line_items_data.csv` — and is additionally populated at runtime whenever a PO is uploaded (upsert by PO number). It is read for lookup when no PO is uploaded. The original app never mutated PO tables at runtime; uploading a PO is the one deliberate exception this feature introduces.
- **Persistence**: The processed invoice and its decision are written to a **results store** (the modern analog of the original `extracted_invoices` record), addressable by `record_id`. The original app's intermediate status-machine writes (`extraction_status` transitions, claim handoffs, the raw-email queue) do NOT carry over — they existed only to coordinate the async multi-service pipeline and dashboard, both removed here.
- **PO precedence**: If both an uploaded PO and a stored PO of the same number exist, the uploaded PO wins (and upserts the stored copy). At most one PO is reconciled per submission.
- **Tax validation is self-contained**: Sales-tax validation uses a configurable flat rate (default 9.125%, matching the original app's fallback). TaxCloud and external address verification are out of scope.
- **Tolerances carry over from the original app** as configurable defaults: line-item/total arithmetic within 0.02; PO line-item matching within quantity 10%, unit price 5%, total price 5%; vendor semantic match at ≥70% confidence; tax discrepancy threshold 0.25. The plan may tune these.
- **Database engine & access layer** are plan-level decisions (the original used PostgreSQL + SQLAlchemy; a lighter self-contained engine is an option for a single-user local service).
- **Single submission per request**: One invoice and at most one PO per call; batch processing is out of scope for v1.
- **New standalone repository**: The work lives in a new git repo at the workspace root (`agentic-invoice-processing/`), independent of both `invoice-processing` and `humain-marketplace`.
- **Runtime**: Python 3.11+ (Strands' supported runtime), consistent with the original backend's toolchain.
