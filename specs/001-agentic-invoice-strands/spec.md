# Feature Specification: Agentic Invoice Processing (Strands)

**Feature Branch**: `001-agentic-invoice-strands`
**Created**: 2026-07-07
**Status**: Draft
**Input**: User description: "Rework the existing multi-service Invoice Processing application into a single, truly *agentic* flow. Drop the email-fetch service, the mock database, and the frontend. Instead, let a user directly upload an invoice and (optionally) a purchase order, and let an agent — built on Amazon's Strands Agents framework — reason its way through extraction, validation, and reconciliation to a decision. Build it as a new standalone repository in the root. Keep the flow strong but not unnecessarily complex."

## Context & Motivation

The current application (separate `Email_fetch`, `extraction`, `processor`, `frontend`, and mock-database services) is a conventional pipeline that happens to call an LLM at a couple of fixed steps: extraction reads documents with a vision model, and the processor uses an LLM only for semantic vendor/line-item matching. The orchestration itself is a hardcoded chain of status transitions (`extracted → Validated1 → … → Approved`), with no reasoning about *what to check next* or *why a decision was made*.

This feature reimagines that same business outcome — turning an invoice into an approve / needs-review decision — as a **model-driven agent** that is handed the documents directly and decides which checks to run, calls purpose-built tools, recovers from ambiguity, and returns a decision **with a human-readable explanation of its reasoning**. Email ingestion, the database, and the web UI are removed; the surface is a single thin upload endpoint.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconcile an invoice against its purchase order (Priority: P1)

An accounts-payable user uploads an invoice document and its corresponding purchase order document to a single endpoint. The agent extracts structured data from both, validates the invoice internally, reconciles it against the PO (vendor and line items), and returns a decision of **APPROVED** or **NEEDS_REVIEW** together with the specific reasons and a short natural-language explanation of how it reached that decision.

**Why this priority**: This is the core value of the whole system and the reason the original processor exists — deciding whether an invoice is safe to pay by matching it to what was actually ordered. It is the full end-to-end agentic flow; everything else is a subset or an enhancement.

**Independent Test**: Submit a known-good invoice + matching PO and confirm the response is `APPROVED` with no blocking reasons; submit an invoice whose totals or line items diverge from the PO beyond tolerance and confirm `NEEDS_REVIEW` with the correct reason code(s). No other story needs to be implemented for this to deliver value.

**Acceptance Scenarios**:

1. **Given** an invoice and a PO that agree on vendor, line items, and totals within tolerance, **When** both are uploaded to the process endpoint, **Then** the agent returns `APPROVED` with an empty list of blocking reasons and an explanation citing the successful checks.
2. **Given** an invoice whose line-item quantities differ from the PO by more than the allowed tolerance, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `line_items_match` reason identifying the divergent item(s).
3. **Given** an invoice whose vendor cannot be matched to the PO vendor, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `po_vendor_match` reason and its confidence in the (non-)match.
4. **Given** an invoice whose stated total does not equal subtotal + tax + shipping − discount within tolerance, **When** it is processed, **Then** the agent returns `NEEDS_REVIEW` with a `financial_totals` reason regardless of PO agreement.

---

### User Story 2 - Validate a standalone invoice with no purchase order (Priority: P2)

A user uploads only an invoice (no PO). The agent extracts the invoice, runs all invoice-internal validations (mandatory fields, currency, line-item arithmetic, sales tax, financial totals), and returns a decision based on those checks alone — no reconciliation is attempted.

**Why this priority**: Not every invoice has a matching PO, and the original system explicitly allowed PO-less invoices to be approved on internal validation alone. Supporting this makes the tool usable on day one for the common case where a PO is unavailable, without forcing users to fabricate one.

**Independent Test**: Submit a well-formed invoice with no PO file and confirm `APPROVED`; submit an invoice missing a mandatory field or with mismatched totals and confirm `NEEDS_REVIEW` with the correct reason — all without any PO in the request.

**Acceptance Scenarios**:

1. **Given** a well-formed invoice and no PO, **When** it is uploaded, **Then** the agent runs only invoice-internal checks and returns `APPROVED` with an explanation noting that reconciliation was skipped because no PO was provided.
2. **Given** an invoice missing a required field (e.g. invoice number or total) and no PO, **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `mandatory_fields` reason listing the missing field(s).
3. **Given** an invoice priced in an unsupported currency and no PO, **When** it is uploaded, **Then** the agent returns `NEEDS_REVIEW` with a `currency` reason.

---

### User Story 3 - Understand and trust the decision (Priority: P3)

A reviewer receives the decision and needs to understand *why* the agent decided as it did: which checks ran, which passed or failed, the values that drove each outcome, and the confidence of any semantic (LLM) judgments. The response includes a structured, check-by-check trace alongside the plain-language explanation.

**Why this priority**: The whole point of making this "truly agentic" rather than a black-box pipeline is explainability — a human must be able to act on `NEEDS_REVIEW`. This is an enhancement layered on top of the decision, valuable but not required for the system to produce a correct verdict.

**Independent Test**: For any processed invoice, confirm the response contains an ordered list of the checks the agent performed, each with a pass/fail/skipped status and the key figures it compared, plus a natural-language summary — and that this trace is consistent with the final decision.

**Acceptance Scenarios**:

1. **Given** any processed submission, **When** the decision is returned, **Then** it includes a trace listing each check performed with its outcome and the concrete values compared (e.g. expected vs. actual totals).
2. **Given** a decision that relied on a semantic vendor or line-item match, **When** the trace is inspected, **Then** it records the match confidence and a short rationale for that judgment.
3. **Given** a check that was intentionally not run (e.g. reconciliation with no PO, or tax validation when tax inputs are unavailable), **When** the trace is inspected, **Then** that check appears as `skipped` with the reason it was skipped.

---

### Edge Cases

- **Unreadable / corrupt file**: The uploaded invoice or PO cannot be opened or converted to an image. The agent returns a clear input error or `NEEDS_REVIEW` with a reason rather than crashing.
- **Unsupported file format**: A file that is neither a supported image type nor a PDF is rejected with an explanatory reason.
- **Multi-page document**: A multi-page PDF is fully considered (all pages contribute to extraction), not just the first page.
- **Extraction returns implausible or empty data**: The vision step yields no parseable structured data or obviously garbage values; the agent flags this as an extraction-quality issue rather than silently proceeding.
- **PO number present on invoice but PO document not uploaded**: Treated as the no-PO path (validation-only), with the missing-PO condition noted in the explanation.
- **Line items reordered, grouped, or split** between invoice and PO: Reconciliation tolerates ordering/grouping differences and still matches on content within tolerance.
- **LLM/vision provider error, timeout, or rate limit**: The agent surfaces a transient-failure outcome distinct from a business `NEEDS_REVIEW`, so callers can retry rather than treat it as a rejection.
- **Zero-quantity or zero-priced line items**: Handled without divide-by-zero or false tax mismatches.
- **Missing tax inputs** (no customer/vendor address, or no per-line tax basis): Sales-tax validation is marked `skipped` with a reason, not failed.

### Scope and Persona Impact *(mandatory)*

- **Affected Persona(s)**: Accounts-payable / finance operator (uploads documents, reads decisions) and the developer/operator running the service.
- **In Scope**: A single upload endpoint accepting one invoice (required) and one optional PO; agent-driven extraction of both documents; invoice-internal validation (mandatory fields, currency, line-item arithmetic, sales tax, financial totals); invoice-to-PO reconciliation (vendor + line items) when a PO is present; a structured decision (`APPROVED` / `NEEDS_REVIEW`) with reason codes, per-check trace, and a natural-language explanation; the agent orchestration itself, built on the Strands Agents framework as a model-driven loop over purpose-built tools.
- **Out of Scope**: Email ingestion; any persistent database or state store; the web frontend; user accounts / multi-tenancy / auth; long-term storage or retrieval of past decisions; TaxCloud (or any external tax authority) integration; address standardization via external services; payment execution; batch/bulk processing beyond a single submission per request.
- **Tenant/Role Impact**: None — this is a standalone, single-user local service with no tenant or role model. No authorization boundaries are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a single submission consisting of one invoice document (required) and one optional purchase-order document, provided directly by the user (no email ingestion, no database lookup).
- **FR-002**: The system MUST accept invoices and POs as PDF or common image formats (at minimum PDF, PNG, JPEG) and MUST convert PDFs (including multi-page PDFs) into images the vision model can read.
- **FR-003**: The system MUST extract structured data from the invoice, including at minimum: invoice number, PO number (if present), invoice date, due date, vendor identity and address, customer identity and address, currency, subtotal, tax amount, discount, shipping, total amount, and line items (description, quantity, unit price, tax rate, total price, category).
- **FR-004**: When a PO document is provided, the system MUST extract comparable structured data from it (PO number, vendor, line items, and totals).
- **FR-005**: The system MUST validate the invoice's mandatory fields and flag the decision when required fields are missing, naming the missing field(s).
- **FR-006**: The system MUST validate that the invoice currency is supported and flag unsupported currencies. (Default supported set: USD; configurable.)
- **FR-007**: The system MUST verify per-line-item arithmetic (quantity × unit price ≈ total price) within a configurable tolerance and flag divergent line items.
- **FR-008**: The system MUST validate sales tax against an expected basis using a configurable flat tax rate; when the inputs required for tax validation are unavailable, it MUST mark the tax check as `skipped` rather than failed.
- **FR-009**: The system MUST verify invoice financial totals — that line-item totals sum to the subtotal, that computed tax matches the stated tax, and that subtotal + tax + shipping − discount equals the stated total — each within a configurable tolerance, and flag any mismatch.
- **FR-010**: When a PO is present, the system MUST reconcile the invoice vendor against the PO vendor, tolerating superficial formatting differences, and MUST record a match confidence; a match below the confidence threshold is a blocking reason.
- **FR-011**: When a PO is present, the system MUST reconcile invoice line items against PO line items — tolerant of reordering, grouping, and description wording — comparing quantity, unit price, and total price within configurable per-dimension tolerances, and flag items that do not match.
- **FR-012**: When no PO is provided, the system MUST run invoice-internal validation only, MUST NOT attempt reconciliation, and MUST record reconciliation as `skipped` with the reason.
- **FR-013**: The system MUST return a single terminal decision of `APPROVED` or `NEEDS_REVIEW`. `APPROVED` requires every applicable check to pass; any failing check yields `NEEDS_REVIEW` with one or more reason codes.
- **FR-014**: The decision MUST include machine-readable reason codes drawn from a fixed taxonomy covering at least: mandatory fields, currency, line-item arithmetic, sales tax, financial totals, PO vendor match, and PO line-item match.
- **FR-015**: The decision MUST include a check-by-check trace, where each check reports `pass` / `fail` / `skipped`, the key values compared, and (for semantic judgments) a confidence and short rationale.
- **FR-016**: The decision MUST include a concise natural-language explanation of the outcome, consistent with the structured trace.
- **FR-017**: The orchestration MUST be agent-driven: a model reasons over the submission and invokes purpose-built tools (extraction, each validation, reconciliation) rather than executing a fixed hardcoded sequence, and the flow MUST be resilient to an individual tool returning ambiguous or partial results.
- **FR-018**: The system MUST distinguish transient failures (model/provider errors, timeouts) from business `NEEDS_REVIEW` outcomes, so a caller can tell "retry me" apart from "a human must review this".
- **FR-019**: The system MUST NOT persist submitted documents or decisions beyond what is required to serve the single request; there is no database and no durable store of past submissions.
- **FR-020**: The system MUST operate as a standalone service requiring only the uploaded files and configured model credentials — no email service, no database, and no frontend are required to run it.

### API Schema Requirements *(mandatory when HTTP endpoints are added or changed)*

- **SCH-001**: `POST /process` MUST accept a multipart request with an `invoice` file part (required) and an optional `po` file part, and MUST return a decision response schema (`InvoiceDecisionResponse`) containing: overall `decision` (`APPROVED` | `NEEDS_REVIEW`), `reasons[]` (reason codes with detail), `checks[]` (the per-check trace), `explanation` (text), the `extracted_invoice` structured data, and, when a PO was provided, the `extracted_po` data and reconciliation results. The exact request/response model names are finalized in the plan.
- **SCH-002**: `GET /health` MUST return a lightweight liveness/readiness response (`HealthResponse`) indicating the service and its configured model provider(s) are reachable.

### Security and Data Requirements *(mandatory when auth, tenants, secrets, or state are touched)*

- **SEC-001**: No authentication or tenant model is introduced; the service is a single-user local tool. This is an explicit scope decision, not an omission — any future multi-user exposure is out of scope here.
- **SEC-002**: All model-provider credentials (Gemini and OpenAI API keys) MUST be sourced from the runtime environment / a secrets mechanism at startup; they MUST NOT be committed to the repository or baked into images or manifests.
- **SEC-003**: Uploaded documents MUST be treated as untrusted input: size and type MUST be validated before processing, and files MUST NOT be persisted beyond the lifetime of the request (see FR-019).

### Key Entities *(include if feature involves data)*

- **Submission**: One processing request — a required invoice document plus an optional PO document. Transient; not stored.
- **Extracted Invoice**: Structured representation of the invoice — header fields (numbers, dates, currency, totals, tax, discount, shipping), vendor block, customer block, and a list of line items.
- **Extracted Purchase Order**: Structured representation of the PO when provided — PO number, vendor, totals, and line items — shaped for comparison against the invoice.
- **Line Item**: A single billed/ordered entry — description, quantity, unit price, tax rate, total price, category.
- **Check**: One validation or reconciliation step the agent performed — its identifier, outcome (`pass`/`fail`/`skipped`), the values it compared, and any confidence/rationale.
- **Decision**: The terminal verdict — `APPROVED` or `NEEDS_REVIEW` — with its blocking reason codes, the ordered list of Checks, and the natural-language explanation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can obtain a decision for an invoice + PO submission through a single request, with no email service, database, or frontend involved.
- **SC-002**: For a well-formed invoice and matching PO, the system returns `APPROVED`; for a submission with a deliberately introduced discrepancy (missing field, total mismatch, or line-item/vendor divergence), it returns `NEEDS_REVIEW` with a reason code that correctly identifies the discrepancy — verified across a labelled test set of at least 10 invoice/PO pairs.
- **SC-003**: On a labelled test set, the decision (`APPROVED` vs `NEEDS_REVIEW`) matches the expected verdict for at least 90% of cases, with no well-formed matching pair incorrectly flagged as `NEEDS_REVIEW` for a reason unrelated to any real discrepancy.
- **SC-004**: Every `NEEDS_REVIEW` decision includes at least one reason code and a trace entry that a reviewer can act on without inspecting logs or source.
- **SC-005**: A single invoice-only submission (no PO) completes and returns a decision within a typical interactive wait (target: under 60 seconds for a single-page document), skipping reconciliation.
- **SC-006**: Corrupt, unsupported, or missing-input submissions never crash the service; each returns a clear, categorized error or `NEEDS_REVIEW` reason.
- **SC-007**: Transient provider failures are reported as retryable and are never reported as a business `NEEDS_REVIEW`.

### Validation Expectations

- **VAL-001**: Backend startup / import-level check — the service starts and `GET /health` returns healthy with valid credentials configured (see plan/README for the exact command).
- **VAL-002**: No UI in scope; instead, a sample request/response (e.g. a captured `POST /process` call against a fixture invoice + PO) documents the observable behavior. No visual artifact is required.
- **VAL-003**: New core logic (extraction mapping, validation checks, reconciliation, decision assembly) meets the project's line-coverage gate, or documents why a given surface (e.g. live model calls) is excluded and how it is covered instead.
- **VAL-004**: Both public HTTP endpoints (`POST /process`, `GET /health`) have integration tests, using fixture documents and stubbed/recorded model responses where live calls are impractical.

## Assumptions

- **Framework**: The agent is built on the **Strands Agents** SDK (Amazon's open-source agent framework), using its model-driven agent loop and tool (`@tool`) abstraction. This is a fixed constraint from the request, recorded here because it is otherwise an implementation choice.
- **Model providers**: Per the clarification, the original providers are retained but driven through Strands — **Gemini** for document/vision extraction and **OpenAI** for semantic reconciliation reasoning. The specific model IDs and the single-agent-with-tools vs. multi-agent topology are plan-level decisions; the requirements above are agnostic to that choice.
- **Entry point**: Per the clarification, the surface is a **thin local HTTP API** (a single `POST /process` upload endpoint plus `GET /health`), not a CLI or a library — chosen for parity with the original service shape and ease of scripting.
- **PO is optional**: Per the clarification, a PO is not required; when present the agent reconciles, when absent it validates only. This mirrors the original app's with-PO / without-PO split.
- **Tax validation is self-contained**: With no database and no external tax service, sales-tax validation uses a configurable flat rate (default 9.125%, matching the original app's fallback). TaxCloud and external address verification are out of scope.
- **Tolerances carry over from the original app** as configurable defaults: line-item/total arithmetic within 0.02; PO line-item matching within quantity 10%, unit price 5%, total price 5%; vendor semantic match at ≥70% confidence; tax discrepancy threshold 0.25. The plan may tune these.
- **Single submission per request**: One invoice (and at most one PO) per call; batch processing is out of scope for v1.
- **New standalone repository**: The work lives in a new git repo at the workspace root (`agentic-invoice-processing/`), independent of both `invoice-processing` and `humain-marketplace`.
- **Runtime**: Python 3.11+ (Strands' supported runtime), consistent with the original backend's toolchain.
