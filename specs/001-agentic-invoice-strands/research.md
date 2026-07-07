# Research: Agentic Invoice Processing (Strands)

**Feature**: `001-agentic-invoice-strands` | **Date**: 2026-07-07

This resolves the open technical unknowns from the spec (framework mechanics,
provider wiring, persistence engine, multimodal handling, conversation state).
Each decision lists rationale and the alternatives rejected.

---

## R1 — Agent topology: single orchestrator + tools (the crux)

**Decision**: One **Orchestrator/Invoice agent** (a Strands `Agent`) drives every
turn, with five tools attached: `extract_document`, `lookup_purchase_order`,
`store_purchase_order`, `store_decision`, and `calculate`. Validation and
reconciliation are performed by the orchestrator's own reasoning; only the
mechanical steps (vision extraction, DB read/write, arithmetic) are tools.

**Rationale**: Mirrors the original app, where the LLM only ever did semantic
matching and the mechanical work (extraction, PO lookup, persistence) was code.
It is the leanest design that is still genuinely agentic — the model chooses
which tools to call and in what order, and can recover from partial results —
satisfying "strong but not unnecessarily complex". A single agent keeps
conversation state in one place (one message history per conversation).

**Alternatives rejected**: (a) A multi-agent graph (extractor agent + validator
agent + reconciler agent) — more moving parts, more latency, harder to keep one
coherent conversation; deferred as unnecessary for v1. (b) Dedicated
deterministic tools for each validation check — more reproducible but pushes the
"reasoning" out of the agent and inflates the tool count; the math tool already
gives us numeric determinism where it matters.

## R2 — Model providers: OpenAI orchestrator, Gemini vision tool

**Decision**: The orchestrator agent uses `strands.models.openai.OpenAIModel`
(`pip install 'strands-agents[openai]'`, model id `gpt-4o-mini` by default,
configurable). The `extract_document` tool internally uses
`strands.models.gemini.GeminiModel` (`pip install 'strands-agents[gemini]'`,
`gemini-2.0-flash`) with **structured output** to turn document images into a
typed `ExtractedInvoice` / `PurchaseOrder`. Provider clients are built once and
reused; API keys come from the environment.

**Rationale**: Matches the earlier clarification (keep Gemini + OpenAI) and the
original split (Gemini vision for extraction, OpenAI for semantic reasoning).
Strands supports different providers per agent/tool in one process, so this is
idiomatic. Structured output (`structured_output_model=` on the Gemini call)
replaces the original's brittle regex/JSON-scraping of the model's text.

**Alternatives rejected**: Passing invoice images directly to the OpenAI
orchestrator as image content blocks — would make the orchestrator multimodal
and blur the provider roles; extraction-as-a-tool keeps OpenAI text-only and
isolates all vision in one place. LiteLLM routing — unnecessary indirection when
first-class `OpenAIModel`/`GeminiModel` exist.

## R3 — Multimodal input routing (images go to the tool, not the orchestrator)

**Decision**: Uploaded files are held in a **request-scoped attachment store**
(a `contextvar` holding `{attachment_id: (bytes, mime, hint)}`). The chat handler
assigns each uploaded file an `attachment_id`, notes them in the user message it
hands the agent (e.g. "Attachments: invoice=att_1 (application/pdf)"), and the
agent calls `extract_document(attachment_id, document_type)`. The tool reads the
bytes from the contextvar, renders PDF pages to PNG, and runs the Gemini
structured-output call with Strands image content blocks
(`{"image": {"format": "png", "source": {"bytes": ...}}}`).

**Rationale**: Tools receive JSON-serializable arguments, not raw bytes, so a
per-request store keyed by a short id is the clean bridge. A `contextvar` is
async-safe and scoped to the request, so raw bytes never outlive the request
(SEC-003). Because extracted JSON lands in the agent's message history, a PO
uploaded in a *later* turn can be reconciled against an invoice from an earlier
turn without re-upload (FR-018) — only the earlier file's *bytes* are gone, not
its extracted data.

**Alternatives rejected**: Pre-extracting before the agent loop (not agentic —
the user asked the agent to use tools). Persisting raw bytes across turns
(violates SEC-003; unnecessary since extracted JSON is retained).

## R4 — Persistence engine: SQLite + SQLAlchemy 2.0

**Decision**: **SQLite** (a single file, path from env, default `./invoices.db`)
accessed through **SQLAlchemy 2.0** ORM. Three read-mostly reference tables
(`po_vendors`, `purchase_orders`, `purchase_order_line_items`) seeded once from
the project CSVs, plus one results table (`processed_invoices`). The uploaded-PO
path upserts the reference tables by PO number.

**Rationale**: A single-user local service needs zero-infra persistence; SQLite
is file-based, needs no server, and SQLAlchemy keeps the code portable to
Postgres later (the original used Postgres + SQLAlchemy, so the ORM models carry
over almost verbatim). This is the "not unnecessarily complex" choice — drops
`psycopg2`, the Cloud SQL proxy, and the whole email-queue/status-machine schema.

**Alternatives rejected**: PostgreSQL — real infra for a local single-user tool;
kept as a documented future swap (change the SQLAlchemy URL). A JSON/file store —
loses relational PO lookup and upsert-by-number semantics we need.

## R5 — Conversation state: per-conversation Agent registry, in-memory

**Decision**: An in-memory registry maps `conversation_id → (Agent, asyncio.Lock)`.
Each conversation gets its own `Agent` (with
`SlidingWindowConversationManager(window_size=~20)`); the lock serializes turns
within a conversation. A new `conversation_id` (uuid) is minted when the request
omits one. Provider clients and tool definitions are shared across agents; only
the Agent + its `messages` are per-conversation.

**Rationale**: The research is explicit that a single mutable `Agent` must not be
shared across concurrent requests (message-history corruption) and that Strands
publishes no thread-safety guarantee. Per-conversation agents with a shared
client is the documented-safe pattern. In-memory is enough for v1 (SC/FR do not
require chat history to survive restart); result records are persisted to the DB
regardless.

**Alternatives rejected**: A global singleton Agent (unsafe, interleaves
histories). `FileSessionManager`/`S3SessionManager` for durable sessions — real
capability, but durable *conversation* history is explicitly out of scope for v1;
noted as the future upgrade path (swap the registry for a `SessionManager`).

## R6 — Structured decision via the `store_decision` tool

**Decision**: At the end of a processing turn the orchestrator calls
`store_decision(decision)` with the fully assembled `Decision` (verdict, reason
codes, per-check trace, explanation, extracted invoice, matched PO + source). The
tool validates it against a Pydantic model, persists it (returning `record_id`),
and stashes the persisted object in a request-scoped contextvar. The handler
reads that stash to populate `ChatResponse.decision`; the agent's natural-language
reply becomes `ChatResponse.message`. Non-processing turns never call
`store_decision`, so `decision` is `null`.

**Rationale**: Ties persistence (FR-021) and structured output (FR-017) to one
enforced tool call, and keeps the human-readable reply and machine-readable
decision from diverging. Strands enforces the tool's Pydantic argument schema, so
the model is forced to emit well-formed reason codes and checks. Cleaner than
running a separate `structured_output` pass, which would conflict with the
tool-calling loop and the free-text reply.

**Alternatives rejected**: A final `structured_output_model=` call after the loop
(double round-trip; loses the conversational reply). Parsing the decision out of
the assistant's prose (the exact brittleness we are removing from the original).

## R7 — PDF rendering and the extraction contract

**Decision**: Render PDF pages to PNG with `pdf2image` at 300 dpi (as the
original), downscale any page over ~1600 px (Pillow, LANCZOS), and pass one image
block per page to the Gemini structured-output call. The extraction prompt is
carried over from the original (accuracy-focused, dates `YYYY-MM-DD`, tax rate as
decimal, null for missing), but the output is a typed Pydantic model rather than
free JSON. Multi-page invoices merge page results (later pages fill gaps / extend
line items).

**Rationale**: Reuses proven parameters from the original extraction service;
`pdf2image` + Pillow are already the project's approach. Typed output removes the
regex JSON-scraping step.

**Prompt location**: all prompt text — the orchestrator system prompt and the
invoice/PO extraction prompts — lives in a single module `app/agent/prompts.py` as
named constants. `extraction_service.py` and `orchestrator.py` import them and hold
no inline prompt strings, so every prompt is tuned/reviewed in one place.

**Alternatives rejected**: PyMuPDF (`fitz`) rendering — capable, but no reason to
diverge from the working `pdf2image` path. OCR (`pytesseract`) — the vision model
reads the image directly; OCR is redundant.

## R8 — Reason-code taxonomy, tolerances, tax (carried from the original)

**Decision**: Fixed reason-code set: `mandatory_fields`, `unsupported_currency`,
`line_item_math`, `sales_tax`, `financial_totals`, `po_vendor_match`,
`po_line_items_match`, plus `extraction_quality` for unreadable/garbage
extraction. Configurable tolerance defaults (from the original): line-item &
total arithmetic ±0.02; PO line-item match quantity 10% / unit price 5% / total
price 5%; vendor semantic match ≥70% confidence; tax discrepancy 0.25; flat tax
rate 9.125%. Supported currency default `["USD"]`.

**Rationale**: Keeps parity with the original's business rules so behavior is
comparable; centralizing them in config (not literals) satisfies the "configurable"
FRs. `sales_tax` is `skipped` (not failed) when tax inputs are unavailable
(FR-011), matching the original's preconditions.

**Alternatives rejected**: TaxCloud API / external address verification — out of
scope; the flat-rate self-contained path is the original's documented fallback.

## R9 — Streaming: complete-response baseline, SSE as a stretch

**Decision**: v1 ships the **non-streaming** complete `ChatResponse` (JSON) as the
tested baseline (MUST). A streaming variant using `agent.stream_async(...)` bridged
to a FastAPI `StreamingResponse` (`text/event-stream`, `callback_handler=None`) is
specified in the contract and implemented as a stretch task; the final structured
decision is emitted as the terminal SSE event.

**Rationale**: FR-024 is a SHOULD. A correct, testable synchronous response is the
right first increment; streaming is additive and does not change the domain logic
or the decision schema.

**Alternatives rejected**: Streaming-only (harder to integration-test
deterministically; not required for v1).

## R10 — FastAPI concurrency

**Decision**: `POST /chat` is `async`; it calls `await agent.invoke_async(...)`
under the per-conversation lock. Provider clients are constructed once at startup
and injected into tools; the Agent is per-conversation. `callback_handler=None`
in the server context. A test seam (`AGENT_FACTORY`) allows integration tests to
inject a deterministic fake agent instead of hitting live providers.

**Rationale**: Directly follows the research's concurrency guidance (per-request/
per-conversation Agent, shared client, async invocation, no stdout callback).

---

## Consolidated dependency & license review

| Dependency | Purpose | License |
|---|---|---|
| `strands-agents`, `[openai]`, `[gemini]` | mandated agent framework + providers | Apache-2.0 |
| `openai` (via extra) | OpenAI orchestrator client | MIT |
| `google-genai` (via extra) | Gemini vision client | Apache-2.0 |
| `pdf2image` (+ system `poppler`) | render PDF pages to images | MIT |
| `pillow` | image downscale/encode | MIT-CMU (HPND) |
| `fastapi`, `uvicorn[standard]`, `python-multipart` | chat API + file upload | MIT / BSD |
| `sqlalchemy` | DB access (SQLite now, Postgres later) | MIT |
| `pydantic` (transitive) | schemas | MIT |
| `python-dotenv` | local `.env` loading | BSD |
| `pytest`, `pytest-cov`, `httpx` (dev) | tests + TestClient | MIT |

No GPL/AGPL/LGPL/SSPL/BUSL. Dropped vs. original: `psycopg2-binary`, `pandas`,
`numpy`, `pytesseract`, `aiohttp`, `google-cloud-storage` (no GCS — files arrive by
upload). CSV seeding uses the stdlib `csv` module (no pandas).
