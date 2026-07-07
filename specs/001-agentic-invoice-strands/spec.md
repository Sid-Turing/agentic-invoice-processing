# Feature Specification: Agentic Invoice Processing (Strands)

**Feature Branch**: `001-agentic-invoice-strands`
**Created**: 2026-07-07
**Status**: Draft
**Input**: User description: "Rework the existing multi-service Invoice Processing application into a single, truly *agentic* flow. Drop the email-fetch service and the frontend. Expose it as a ChatGPT-style chat endpoint: the user sends messages that can contain free text and/or uploaded multimodal files (an invoice, and optionally a purchase order), across multiple turns. When a PO is uploaded the agent extracts it and writes it to the database using its tools; otherwise, if the invoice carries a PO number, the agent looks that PO up in the database. Either way it reconciles the invoice against the PO — otherwise it skips reconciliation — and replies conversationally with the decision. Built on Amazon's Strands Agents framework, as a new standalone repository in the root. Keep the flow strong but not unnecessarily complex."

## Context & Motivation

The current application (separate `Email_fetch`, `extraction`, `processor`, `frontend`, and mock-database services) is a conventional pipeline that happens to call an LLM at a couple of fixed steps: extraction reads documents with a vision model, and the processor uses an LLM only for semantic vendor/line-item matching. The orchestration itself is a hardcoded chain of status transitions (`extracted → Validated1 → … → Approved`), with no reasoning about *what to check next*, no conversation with the user, and no explanation of *why* a decision was made.

This feature reimagines that same business outcome — turning an invoice into an approve / needs-review decision — as a **conversational, model-driven agent**. The user talks to it like ChatGPT: a message may carry free text, an uploaded invoice, an uploaded PO, or any combination, and the conversation can span several turns. The agent decides which tools to call, extracts and reconciles, persists the result, and answers in natural language (while also returning the structured decision for programmatic callers). Email ingestion and the web UI are removed; the surface is a single multimodal chat endpoint.

PO resolution has two paths, chosen by the agent from what the user provides:

- **Uploaded PO**: the message includes a PO document. The agent extracts it (vision tool) and writes it into the PO store (write tool), then reconciles against it.
- **PO on file**: no PO is uploaded, but the invoice carries a PO number. The agent looks that PO up in the database (read tool) and reconciles.

If neither yields a PO, reconciliation is skipped and the decision rests on invoice-internal validation alone.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process an invoice through chat (Priority: P1)

An accounts-payable user opens a conversation and sends a message with an invoice attached (optionally with its PO, and optionally with a note like "please check this against PO-54872"). The agent extracts the invoice; resolves the PO (extracting and storing an uploaded PO, or looking one up by number); validates the invoice internally; reconciles it against the resolved PO; persists the result; and replies conversationally with the verdict (**APPROVED** / **NEEDS_REVIEW**), the reasons, and a short explanation — while the response also carries the structured decision.

**Why this priority**: This is the core value and the reason the original processor exists — deciding whether an invoice is safe to pay by matching it to what was ordered — now delivered through the natural chat surface. Everything else is a refinement of, or a conversation around, this outcome.

**Independent Test**: In a single chat turn, attach an invoice (and, in a variant, a matching PO document); confirm the reply states `APPROVED` with an explanation and the structured decision is present; introduce a divergence beyond tolerance and confirm the reply is `NEEDS_REVIEW` with the correct reason code. Confirm the PO-on-file variant (invoice with a known PO number, no PO file) fetches and reconciles.

**Acceptance Scenarios**:

1. **Given** a chat message with an invoice and a matching PO document, **When** it is sent, **Then** the agent extracts the PO, writes it to the PO store, reconciles, and replies `APPROVED` with no blocking reasons plus a structured decision.
2. **Given** a chat message with an invoice that carries a PO number (no PO file) and that PO is in the database, **When** it is sent, **Then** the agent looks the PO up, reconciles, and replies accordingly.
3. **Given** an invoice whose line-item quantities differ from the resolved PO beyond tolerance, **When** it is sent, **Then** the reply is `NEEDS_REVIEW` with a `line_items_match` reason identifying the divergent item(s).
4. **Given** an invoice whose stated total does not equal subtotal + tax + shipping − discount within tolerance, **When** it is sent, **Then** the reply is `NEEDS_REVIEW` with a `financial_totals` reason regardless of PO agreement.

---

### User Story 2 - Converse and refine across turns (Priority: P2)

Within an ongoing conversation, the user follows up: asks "why did this need review?", uploads the PO in a *later* message after first sending only the invoice, supplies a PO number in text, or asks the agent to re-check. The agent uses the retained conversation context to answer and, when new information (a PO file or number) arrives, updates its reconciliation and decision without the user re-uploading the invoice.

**Why this priority**: The conversational, multi-turn nature is what makes this "ChatGPT-like" rather than a one-shot endpoint. Follow-up explanation and incremental provision of a PO are the highest-value interactions beyond the first decision, and they turn the black-box verdict into something a human can interrogate and correct.

**Independent Test**: Send an invoice with no PO (get a validation-only decision); in the next turn upload the matching PO and confirm the agent reconciles using the invoice from the prior turn and returns an updated decision; then ask "why?" in plain text and confirm the explanation is consistent with the decision — all under one conversation id.

**Acceptance Scenarios**:

1. **Given** a prior turn that produced a `NEEDS_REVIEW` decision, **When** the user asks "why?" in a follow-up message with no attachment, **Then** the agent explains the blocking reason(s) from conversation context without re-processing files.
2. **Given** a prior turn where only an invoice was sent, **When** the user uploads the matching PO in the next turn, **Then** the agent reconciles the earlier invoice against the newly uploaded PO and returns an updated decision.
3. **Given** a prior turn where reconciliation was skipped for "no PO number", **When** the user provides a PO number in text, **Then** the agent looks it up and reconciles.
4. **Given** a conversation id from an earlier turn, **When** a new message is sent with that id, **Then** the agent continues the same conversation with its context intact.

---

### User Story 3 - Graceful, explainable conversation (Priority: P3)

The user sends plain-text messages, ambiguous attachments, or incomplete requests. The agent responds helpfully: it answers general questions, asks a clarifying question when a message is ambiguous (e.g. two invoices attached, or a file that is neither an invoice nor a PO), and — for any processing outcome — exposes a check-by-check trace and the resolved PO's source so a reviewer can trust the result.

**Why this priority**: Explainability and graceful handling of imperfect input are what make the agent usable and trustworthy, but they layer on top of a system that already produces correct verdicts. This is polish, not the core mechanism.

**Independent Test**: Send a plain-text greeting/question and confirm a sensible reply with no spurious processing; attach a non-invoice image and confirm the agent asks what to do rather than fabricating a decision; for a real processing turn, confirm the structured trace lists each check's outcome, the compared values, semantic-match confidences, and the PO source.

**Acceptance Scenarios**:

1. **Given** a message with no actionable attachment and only a general question, **When** it is sent, **Then** the agent replies conversationally and does not invoke the processing tools spuriously.
2. **Given** a message whose attachment is ambiguous (e.g. two candidate invoices, or an unrelated image), **When** it is sent, **Then** the agent asks a clarifying question rather than guessing.
3. **Given** any processing turn, **When** the decision is returned, **Then** its structured payload includes a trace listing each check (pass/fail/skipped), the values compared, semantic-match confidence and rationale where applicable, and the resolved PO's source (`uploaded` | `database`).

---

### Edge Cases

- **Unreadable / corrupt attachment** (invoice or PO): the file cannot be opened or converted; the agent says so conversationally and does not crash; a bad PO is reported distinctly from a bad invoice.
- **Unsupported file format**: an attachment that is neither a supported image type nor a PDF is rejected with an explanation.
- **Multi-page document**: a multi-page PDF (invoice or PO) is fully considered, not just the first page.
- **Message with no attachment and no actionable text**: the agent responds conversationally without invoking processing tools.
- **Multiple invoices (or multiple POs) in one message**: the agent asks which to process (or processes the clearly-primary one and says so) rather than silently picking.
- **Attachment that is neither invoice nor PO**: the agent asks for clarification rather than fabricating an extraction.
- **Uploaded PO whose number already exists on file**: upserted by PO number; the uploaded version is used for reconciliation.
- **PO number present but PO neither uploaded nor on file**: reconciliation skipped with reason "PO not found"; decision rests on invoice-internal checks.
- **No PO number and no PO uploaded**: reconciliation skipped with reason "no PO number".
- **Unknown or expired conversation id**: the agent starts a fresh conversation (or reports the id is unknown) rather than erroring opaquely.
- **Database unreachable / lookup or write times out**: transient failure (retryable), distinct from "PO not found" and from `NEEDS_REVIEW`.
- **LLM/vision provider error, timeout, or rate limit**: transient-failure outcome distinct from a business `NEEDS_REVIEW`.
- **Line items reordered, grouped, or split** between invoice and PO: reconciliation tolerates ordering/grouping and still matches within tolerance.
- **Zero-quantity or zero-priced line items**: handled without divide-by-zero or false tax mismatches.
- **Missing tax inputs**: sales-tax validation marked `skipped` with a reason, not failed.

### Scope and Persona Impact *(mandatory)*

- **Affected Persona(s)**: Accounts-payable / finance operator (chats with the agent, uploads documents, reads decisions) and the developer/operator running the service and seeding the PO database.
- **In Scope**: A single conversational chat endpoint that accepts a user message containing free text and/or uploaded multimodal files (an invoice and/or a PO), with multi-turn conversation context; agent-driven extraction of the invoice and any uploaded PO; a database-backed write tool the agent uses to persist an extracted uploaded PO (upsert by PO number) and to persist the processed invoice with its final decision; a database-backed read tool that looks up a PO by the invoice's PO number; invoice-internal validation (mandatory fields, currency, line-item arithmetic, sales tax, financial totals); invoice-to-PO reconciliation (vendor + line items) when a PO is resolved; a decision (`APPROVED` / `NEEDS_REVIEW`) delivered both as a natural-language reply and as a structured payload (reason codes, per-check trace, explanation); the agent orchestration itself, built on the Strands Agents framework as a model-driven loop over purpose-built tools.
- **Out of Scope**: Email ingestion; a web/chat frontend UI (this feature delivers the chat *API*, not a UI); user accounts / multi-tenancy / auth; a dedicated PO-management API or UI, PO deletion, or bulk PO import beyond an uploaded PO in a message; a browse/search API over past decisions or conversations; TaxCloud (or any external tax authority) integration; address standardization via external services; payment execution; batch/bulk processing of many invoices in one turn.
- **Tenant/Role Impact**: None — this is a standalone, single-user local service with no tenant or role model. No authorization boundaries are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a conversational chat endpoint that accepts a user message which MAY contain free text and/or zero or more uploaded files (invoice and/or PO) as PDF or common image formats.
- **FR-002**: The system MUST support multi-turn conversations: it MUST accept an optional conversation identifier, create and return a new one when absent, and retain conversation context (prior messages, extracted documents, and the last decision) across turns within a conversation.
- **FR-003**: The system MUST convert PDFs (including multi-page PDFs) and images into a form the vision extraction tool can read.
- **FR-004**: When the user's message includes an invoice, the system MUST extract structured data from it, including at minimum: invoice number, PO number (if present), invoice date, due date, vendor identity and address, customer identity and address, currency, subtotal, tax amount, discount, shipping, total amount, and line items (description, quantity, unit price, tax rate, total price, category).
- **FR-005**: When a PO document is uploaded (in the current or a prior turn of the conversation), the system MUST extract it via the extraction tool and persist it via the write tool — upserting by PO number the purchase order, its vendor, and its line items — then use it for reconciliation.
- **FR-006**: When no PO document has been provided, the system MUST use the read tool to look up the PO by the PO number extracted from the invoice and report whether a match was found.
- **FR-007**: The system MUST resolve at most one PO per decision, preferring an uploaded PO over one on file; the resolved PO's source (`uploaded` | `database`) MUST be recorded and surfaced.
- **FR-008**: The system MUST validate the invoice's mandatory fields and flag the decision when required fields are missing, naming the missing field(s).
- **FR-009**: The system MUST validate that the invoice currency is supported and flag unsupported currencies. (Default supported set: USD; configurable.)
- **FR-010**: The system MUST verify per-line-item arithmetic (quantity × unit price ≈ total price) within a configurable tolerance and flag divergent line items.
- **FR-011**: The system MUST validate sales tax against an expected basis using a configurable flat tax rate; when required inputs are unavailable, it MUST mark the tax check `skipped` rather than failed.
- **FR-012**: The system MUST verify invoice financial totals — line items sum to subtotal, computed tax matches stated tax, and subtotal + tax + shipping − discount equals the stated total — each within a configurable tolerance, flagging any mismatch.
- **FR-013**: When a PO is resolved, the system MUST reconcile the invoice vendor against the PO vendor (tolerating superficial formatting differences), recording a match confidence; a match below the confidence threshold is a blocking reason.
- **FR-014**: When a PO is resolved, the system MUST reconcile invoice line items against PO line items — tolerant of reordering, grouping, and wording — comparing quantity, unit price, and total price within configurable per-dimension tolerances, and flag items that do not match.
- **FR-015**: When no PO is uploaded and none is found on file, the system MUST run invoice-internal validation only, MUST NOT attempt reconciliation, and MUST record reconciliation as `skipped` with the distinguishing reason (no PO number vs. PO not found).
- **FR-016**: For any processing turn, the system MUST produce a single terminal decision of `APPROVED` or `NEEDS_REVIEW`. `APPROVED` requires every applicable check to pass; any failing check yields `NEEDS_REVIEW` with one or more reason codes drawn from a fixed taxonomy covering at least: mandatory fields, currency, line-item arithmetic, sales tax, financial totals, PO vendor match, and PO line-item match.
- **FR-017**: The system MUST reply to the user in natural language, and the response MUST also carry the structured decision — verdict, reason codes, a per-check trace (each check `pass`/`fail`/`skipped` with the values compared and, for semantic judgments, confidence and rationale), the resolved PO and its source, the extracted invoice, and the persisted `record_id`.
- **FR-018**: When new information arrives in a later turn (an uploaded PO, a PO number, or a request to re-check), the system MUST update its reconciliation and decision using the conversation's retained invoice context, without requiring the user to re-upload the invoice.
- **FR-019**: The system MUST handle non-processing messages gracefully: answer general or follow-up questions (including "why?" about the last decision) from conversation context, and ask a clarifying question when a message is ambiguous or incomplete, rather than invoking the processing tools spuriously or fabricating a decision.
- **FR-020**: The orchestration MUST be agent-driven: a model reasons over the conversation and invokes purpose-built tools (extraction, PO write, PO read, and a deterministic math helper) rather than executing a fixed hardcoded sequence, and MUST be resilient to a tool returning ambiguous or partial results.
- **FR-021**: The system MUST persist each processed invoice together with its final decision (verdict, reason codes, check trace) to a results store via the write tool, addressable by a `record_id`.
- **FR-022**: The system MUST confine database writes to two controlled operations — (a) upserting an uploaded PO (with vendor and line items) into the PO store, and (b) persisting a processed-invoice result — with no other mutations and no deletes. Raw uploaded files MUST NOT be persisted beyond the request; only extracted structured data and decisions are stored.
- **FR-023**: The system MUST distinguish transient failures (model/provider errors, timeouts, database unavailability on read or write, including a failure to persist an uploaded PO or a result) from business `NEEDS_REVIEW` outcomes and from a benign "PO not found" skip, so a caller can tell "retry me" apart from "a human must review this" apart from "no PO available".
- **FR-024**: The system SHOULD support streaming the assistant's reply incrementally (ChatGPT-style), and MAY instead return the complete reply in one response; either way the structured decision MUST be available once processing completes.
- **FR-025**: The system MUST operate as a standalone service requiring only the chat requests, a reachable database, and configured model credentials — no email service and no frontend are required to run it.

### API Schema Requirements *(mandatory when HTTP endpoints are added or changed)*

- **SCH-001**: `POST /chat` MUST accept a multipart request carrying an optional `message` text part, an optional `conversation_id`, and zero or more uploaded `files` (invoice and/or PO). It MUST return a `ChatResponse` containing: the `conversation_id`, the assistant's natural-language `message`, and — when a processing action ran this turn — a `decision` object (`record_id`, `verdict` = `APPROVED` | `NEEDS_REVIEW`, `reasons[]`, `checks[]`, `explanation`, `extracted_invoice`, and, when a PO was resolved, `matched_po` with its `source`). When streaming (FR-024) the endpoint MAY emit incremental message chunks followed by the final structured payload. Exact model names are finalized in the plan.
- **SCH-002**: `GET /health` MUST return a lightweight liveness/readiness response (`HealthResponse`) indicating the service, its configured model provider(s), and the database are reachable.

### Security and Data Requirements *(mandatory when auth, tenants, secrets, or state are touched)*

- **SEC-001**: No authentication or tenant model is introduced; the service is a single-user local tool. This is an explicit scope decision, not an omission.
- **SEC-002**: All model-provider credentials (Gemini and OpenAI API keys) and database connection credentials MUST be sourced from the runtime environment / a secrets mechanism at startup; they MUST NOT be committed to the repository or baked into images or manifests.
- **SEC-003**: Uploaded files MUST be treated as untrusted input: size and type MUST be validated before processing, and the raw files MUST NOT be persisted beyond the lifetime of the request (see FR-022). Conversation context MAY retain extracted structured data for the life of the conversation, but not the raw file bytes.
- **SEC-004**: The service MUST write to the database only via the two controlled operations in FR-022 (upsert uploaded PO; persist result). It MUST NOT delete PO or vendor data and MUST NOT mutate a stored PO except by upsert from a freshly uploaded PO of the same number.

### Key Entities *(include if feature involves data)*

- **Conversation**: A multi-turn thread identified by a `conversation_id`, holding the ordered messages and the retained context (extracted invoice/PO data and the last decision). Context lifetime is the conversation; raw files are not retained.
- **Message**: One turn — a user message (text and/or attachments) or an assistant reply (text plus, on processing turns, a structured decision).
- **Extracted Invoice**: Structured invoice data — header fields, vendor block, customer block, line items — including the PO number when present.
- **Purchase Order**: A record in the PO store — PO number, vendor, dates, subtotal, tax, total, currency, payment terms, status — seeded, previously stored, or freshly upserted from an uploaded PO. Carries a `source` (`uploaded` | `database`) when used in a decision.
- **Vendor**: The vendor record associated with a PO — name, tax ID, address, banking and tax-classification details.
- **PO Line Item** / **Invoice Line Item**: A single line — description, quantity, unit price, tax rate, total price, category.
- **Check**: One validation or reconciliation step — identifier, outcome (`pass`/`fail`/`skipped`), values compared, and any confidence/rationale.
- **Decision**: The terminal verdict — `APPROVED` or `NEEDS_REVIEW` — with blocking reason codes, the ordered Checks, the natural-language explanation, and the resolved PO source.
- **Processed Invoice Record (persisted)**: The durable record written once per processing turn via the write tool — extracted invoice + decision + check trace, addressable by `record_id`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can process an invoice by sending it (with or without a PO) in a chat message and receive both a readable natural-language reply and a structured decision — with no email service and no frontend involved.
- **SC-002**: When a PO is uploaded in a message, it is extracted and persisted (retrievable afterward by PO number) and used for reconciliation; when no PO is uploaded, a matching PO on file is fetched and used — both paths verified.
- **SC-003**: Within one conversation, providing a PO (file or number) in a later turn updates the decision using the retained invoice context, without re-uploading the invoice; and a plain-text "why?" follow-up returns an explanation consistent with the last decision.
- **SC-004**: A well-formed invoice matching its resolved PO returns `APPROVED`; an invoice with a deliberately introduced discrepancy (missing field, total mismatch, or line-item/vendor divergence) returns `NEEDS_REVIEW` with a reason code that correctly identifies it — verified across a labelled test set of at least 10 invoices.
- **SC-005**: On a labelled test set, the verdict matches the expected outcome for at least 90% of cases, with no well-formed matching invoice flagged for a reason unrelated to a real discrepancy.
- **SC-006**: Every `NEEDS_REVIEW` decision includes at least one reason code and a trace entry a reviewer can act on without inspecting logs or source.
- **SC-007**: A single processing turn with no resolvable PO returns a decision within a typical interactive wait (target: under 60 seconds for a single-page document), with reconciliation recorded as skipped.
- **SC-008**: Corrupt, unsupported, ambiguous, or empty messages never crash the service; each yields a clear conversational reply (an error, a clarifying question, or a categorized `NEEDS_REVIEW` reason).
- **SC-009**: Transient failures — provider errors and database unavailability (read or write) — are reported as retryable and are never reported as a business `NEEDS_REVIEW` or as "PO not found".
- **SC-010**: Each successful processing turn produces exactly one persisted result record (extracted invoice + verdict + reason codes + check trace), retrievable by `record_id`; database writes are limited to result records and PO upserts, with no deletions.

### Validation Expectations

- **VAL-001**: Backend startup / import-level check — the service starts and `GET /health` returns healthy with valid credentials and a reachable, seeded database (see plan/README for the exact command).
- **VAL-002**: No UI in scope; instead, sample chat transcripts (a turn with an uploaded invoice + PO; a multi-turn refinement where the PO arrives in a later turn; a plain-text follow-up) document the observable behavior. No visual artifact is required.
- **VAL-003**: New core logic (invoice + PO extraction mapping, PO upsert, PO lookup, validation checks, reconciliation, decision assembly, conversation-context handling) meets the project's line-coverage gate, or documents why a surface (e.g. live model calls) is excluded and how it is otherwise covered.
- **VAL-004**: The public HTTP endpoints (`POST /chat`, `GET /health`) have integration tests covering: single-turn uploaded-PO, single-turn PO-on-file, multi-turn PO-arrives-later, and a non-processing message — using fixture documents, a seeded (or stubbed) database, and stubbed/recorded model responses where live calls are impractical.

## Assumptions

- **Framework**: The agent is built on the **Strands Agents** SDK (Amazon's open-source agent framework), using its model-driven agent loop, tool (`@tool`) abstraction, and conversation/session state management. This is a fixed constraint from the request.
- **Model providers**: Per an earlier clarification, the original providers are retained but driven through Strands — **Gemini** for document/vision extraction and **OpenAI** for the conversational reasoning and semantic reconciliation. Specific model IDs and single-agent-vs-multi-agent topology are plan-level; the requirements are agnostic to that choice.
- **Entry point**: The surface is a **ChatGPT-style multimodal chat API** (`POST /chat` accepting text and/or file attachments with a conversation id, plus `GET /health`) — not a one-shot upload endpoint, a CLI, or a UI. This supersedes the earlier single-shot `POST /process` design.
- **Agreed agent architecture**: A single **Orchestrator/Invoice agent** drives the conversation with four tools — (1) a **VLM-backed extraction tool** (document → structured data, for invoice and uploaded PO), (2) a **database write tool** (upsert an uploaded PO; persist the processed invoice + decision), (3) a **read-only PO lookup/search tool** (by PO number), and (4) a deterministic **math tool** (summations, total/tax checks). Validation and reconciliation are performed by the orchestrator's own reasoning, using the math tool for arithmetic, rather than as separate tools. This mirrors the original app, where the LLM did the semantic matching and only extraction/lookup/persistence were mechanical.
- **Conversation state**: Conversation context (messages, extracted data, last decision) is maintained per `conversation_id`, in-memory at minimum; durable storage of conversation history is a plan-level option, not required for v1. Result records are persisted to the database regardless.
- **Streaming**: A ChatGPT-style streaming response is desirable (FR-024); the transport (e.g. SSE / chunked) is a plan-level detail. A non-streaming complete response is an acceptable v1 fallback.
- **Purchase orders live in a database**: A PO store holds POs with vendors and line items, seeded from the existing project data — `purchase_orders_data.csv`, `po_vendors_data.csv`, `purchase_order_line_items_data.csv` — and additionally populated at runtime when a PO is uploaded (upsert by PO number). It is read for lookup when no PO is uploaded. The original app never mutated PO tables at runtime; the upload-upsert path is the one deliberate exception this feature adds.
- **Persistence**: The processed invoice and its decision are written to a **results store** (the analog of the original `extracted_invoices` record), addressable by `record_id`. The original app's intermediate status-machine writes (`extraction_status` transitions, claim handoffs, raw-email queue) do NOT carry over — they existed only to coordinate the async multi-service pipeline and dashboard, both removed here.
- **PO precedence**: If both an uploaded PO and a stored PO of the same number exist, the uploaded PO wins (and upserts the stored copy). At most one PO is reconciled per decision.
- **Tax validation is self-contained**: a configurable flat rate (default 9.125%, matching the original's fallback). TaxCloud and external address verification are out of scope.
- **Tolerances carry over from the original app** as configurable defaults: arithmetic/total within 0.02; PO line-item matching within quantity 10%, unit price 5%, total price 5%; vendor semantic match ≥70% confidence; tax discrepancy threshold 0.25.
- **Database engine & access layer** are plan-level decisions (the original used PostgreSQL + SQLAlchemy; a lighter self-contained engine is an option for a single-user local service).
- **New standalone repository**: The work lives in a new git repo at the workspace root (`agentic-invoice-processing/`), independent of both `invoice-processing` and `humain-marketplace`.
- **Runtime**: Python 3.11+ (Strands' supported runtime), consistent with the original backend's toolchain.
